"""Task 9-1 综合 Demo · 男性向内容微信推文 Agent · 公共模块

融合前几章能力：
- ch05 子 Agent：trend-researcher（选题）/ image-scout（配图）
- ch07 Skills：/skills/wechat-article/SKILL.md 统一推文格式
- ch08 长期记忆：/memories/* 跨线程沉淀（方向、已发选题、爆款规律）
- ch09 HITL：publish_article 终稿审批（approve/edit/reject）
- ch12 预览：图床 MCP（mcp/image_server.py）

环境变量（`labs/demo-wechat/.env` 或项目根 `.env`）：
  SENSENOVA_API_KEY   必填
  MODEL_NAME          默认 glm-5.2
  SENSENOVA_BASE_URL  默认 https://token.sensenova.cn/v1
  PEXELS_API_KEY      选填（有则图床走 Pexels，否则回退 picsum.photos）
  DEMO_CALL_INTERVAL  每次模型调用前间隔秒（默认 5，防 429）
  DEMO_RETRIES        429 重试次数（默认 5）
  DEMO_RETRY_WAIT     429 退避基数秒（默认 60）
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langgraph.types import Command

WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")


# --------------------------------------------------------------------------- #
# 环境与模型
# --------------------------------------------------------------------------- #
def _load_env() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (".env", os.path.join("..", "..", ".env")):
        path = os.path.abspath(os.path.join(here, rel))
        if os.path.isfile(path):
            try:
                from dotenv import load_dotenv  # type: ignore
            except Exception:
                return
            load_dotenv(path, override=False)


_load_env()


def build_model():
    from langchain_openai import ChatOpenAI

    api_key = os.environ.get("SENSENOVA_API_KEY")
    if not api_key:
        raise SystemExit(
            "缺少 SENSENOVA_API_KEY。\n"
            "请复制 labs/demo-wechat/.env.example 为 labs/demo-wechat/.env 并填写。"
        )
    return ChatOpenAI(
        model=os.environ.get("MODEL_NAME", "glm-5.2"),
        api_key=api_key,
        base_url=os.environ.get("SENSENOVA_BASE_URL", "https://token.sensenova.cn/v1"),
        max_retries=6,
        timeout=180,
    )


# --------------------------------------------------------------------------- #
# 记忆 namespace（ch08）
# --------------------------------------------------------------------------- #
@dataclass
class EditorContext:
    """运行时上下文：用 dataclass 让 namespace 有兜底（本地 server_info 可能为空）。"""

    editor_id: str = "editor-001"
    org_id: str = "media-lab"


def user_namespace(rt) -> tuple:
    server_info = getattr(rt, "server_info", None)
    if server_info and getattr(server_info, "user", None):
        return (server_info.user.identity, "memories")
    editor_id = getattr(getattr(rt, "context", None), "editor_id", "editor-001")
    return (editor_id, "memories")


# --------------------------------------------------------------------------- #
# Backend：磁盘（skills + 草稿） + Store（记忆）
# --------------------------------------------------------------------------- #
def memory_namespace(editor_id: str) -> tuple:
    return (editor_id, "memories")


def build_backend():
    """默认走磁盘（真文件 skills/草稿），/memories/ 路由到 StoreBackend（跨线程记忆）。"""
    from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend

    os.makedirs(WORKSPACE, exist_ok=True)
    return CompositeBackend(
        default=FilesystemBackend(root_dir=WORKSPACE, virtual_mode=True),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: user_namespace(rt),
            ),
        },
    )


# --------------------------------------------------------------------------- #
# 持久化 Store（跨天）：InMemoryStore 子类 + JSON 落盘
# --------------------------------------------------------------------------- #
def build_store(path: str | None = None):
    """跨进程/跨天持久的 Store：只拦截 batch/abatch，把内存数据镜像到 JSON。"""
    when = path or os.path.join(WORKSPACE, ".state", "store.json")
    os.makedirs(os.path.dirname(when), exist_ok=True)
    return _JsonFileStore(when)


class _JsonFileStore:
    """延迟导入实现，避免模块顶层强依赖 langgraph。"""

    def __new__(cls, path: str):
        from langgraph.store.base import PutOp
        from langgraph.store.memory import InMemoryStore

        class _Store(InMemoryStore):
            def __init__(self, p: str):
                super().__init__()
                self._path = p
                self._mirror: dict[str, dict] = {}
                self._lock = threading.Lock()
                self._load()

            @staticmethod
            def _rid(ns, key) -> str:
                return json.dumps(list(ns), ensure_ascii=False) + "\x00" + key

            def _apply(self, ops) -> None:
                for op in ops:
                    if isinstance(op, PutOp):
                        rid = self._rid(op.namespace, op.key)
                        if getattr(op, "value", None) is None:
                            self._mirror.pop(rid, None)
                        else:
                            self._mirror[rid] = {
                                "namespace": list(op.namespace),
                                "key": op.key,
                                "value": op.value,
                            }

            def _save(self) -> None:
                tmp = f"{self._path}.{os.getpid()}.{threading.get_ident()}.tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(list(self._mirror.values()), f, ensure_ascii=False)
                for _ in range(6):
                    try:
                        os.replace(tmp, self._path)
                        return
                    except PermissionError:
                        time.sleep(0.05)
                os.replace(tmp, self._path)

            def _load(self) -> None:
                if not os.path.isfile(self._path):
                    return
                try:
                    data = json.load(open(self._path, encoding="utf-8"))
                except Exception:
                    return
                ops = []
                for rec in data:
                    ns = tuple(rec["namespace"])
                    key = rec["key"]
                    val = rec["value"]
                    self._mirror[self._rid(ns, key)] = rec
                    if val is not None:
                        ops.append(PutOp(ns, key, val))
                if ops:
                    super().batch(ops)

            def batch(self, ops):
                ops = list(ops)
                if not any(isinstance(op, PutOp) for op in ops):
                    return super().batch(ops)  # 纯读：不落盘、不加锁
                with self._lock:
                    res = super().batch(ops)
                    self._apply(ops)
                    self._save()
                return res

            async def abatch(self, ops):
                ops = list(ops)
                if not any(isinstance(op, PutOp) for op in ops):
                    return await super().abatch(ops)
                with self._lock:
                    res = await super().abatch(ops)
                    self._apply(ops)
                    self._save()
                return res

        return _Store(path)


# --------------------------------------------------------------------------- #
# 仪器：请求级捕获 + 副作用账本
# --------------------------------------------------------------------------- #
class RequestCapture(BaseCallbackHandler):
    def __init__(self) -> None:
        self.requests: list[dict] = []

    def reset(self) -> None:
        self.requests.clear()

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:  # noqa: D401
        flat: list[BaseMessage] = []
        for batch in messages:
            flat.extend(batch if isinstance(batch, (list, tuple)) else [batch])
        text = "\n".join(_msg_text(m) for m in flat)
        self.requests.append({"roles": [getattr(m, "type", "?") for m in flat], "text": text})

    def last_text(self) -> str:
        return self.requests[-1]["text"] if self.requests else ""


def _msg_text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, (list, tuple)):
        out = []
        for b in content:
            out.append(b if isinstance(b, str) else (b.get("text", "") if isinstance(b, dict) else getattr(b, "text", "")))
        return "\n".join(out)
    return str(content)


class ToolLedger:
    """副作用账本：工具真正执行才记一笔（用于 HITL 判定，ch09）。"""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def record(self, name: str, args: dict) -> None:
        self.calls.append({"name": name, "args": dict(args)})

    def reset(self) -> None:
        self.calls.clear()

    def count(self, name: str | None = None) -> int:
        return len(self.calls) if name is None else len([c for c in self.calls if c["name"] == name])

    def name_calls(self, name: str) -> list[dict]:
        return [c for c in self.calls if c["name"] == name]

    def dump(self) -> str:
        return "[" + ", ".join(f"{c['name']}({c['args']})" for c in self.calls) + "]"


# --------------------------------------------------------------------------- #
# 判定器
# --------------------------------------------------------------------------- #
class Judge:
    def __init__(self, title: str) -> None:
        self.title = title
        self.rows: list[tuple[str, bool, str]] = []

    def check(self, name: str, ok: Any, detail: str = "") -> None:
        self.rows.append((name, bool(ok), detail))

    def observe(self, name: str, detail: str = "") -> None:
        print(f"[ 观察 ] {name}" + (f"  — {detail}" if detail else ""))

    def report(self, exit_on_fail: bool = False) -> tuple[int, int]:
        print("\n" + "=" * 66)
        print(f"判定器 · {self.title}")
        print("=" * 66)
        passed = 0
        for name, ok, detail in self.rows:
            passed += int(ok)
            line = f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else "")
            print(line)
        print(f"结果：{passed}/{len(self.rows)} 通过（观察项不计分）")
        if exit_on_fail and passed != len(self.rows):
            sys.exit(1)
        return passed, len(self.rows)


# --------------------------------------------------------------------------- #
# 运行辅助（v2 + 429 自愈）
# --------------------------------------------------------------------------- #
def banner(title: str) -> None:
    print("\n" + "#" * 66 + f"\n# {title}\n" + "#" * 66)


def section(title: str) -> None:
    print("\n" + "-" * 66 + f"\n· {title}\n" + "-" * 66)


def new_thread() -> str:
    return str(uuid.uuid4())


def new_config(thread_id: str | None = None) -> dict:
    return {"configurable": {"thread_id": thread_id or new_thread()}}


def _is_rate_limited(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(k in text for k in ("429", "rate limit", "ratelimit", "rpm", "quota", "too many requests"))


def _with_retry(fn):
    attempts = int(os.environ.get("DEMO_RETRIES", "5"))
    base = float(os.environ.get("DEMO_RETRY_WAIT", "60"))
    interval = float(os.environ.get("DEMO_CALL_INTERVAL", "5"))
    if interval > 0:
        time.sleep(interval)
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            if not _is_rate_limited(exc) or i == attempts - 1:
                raise
            wait = base * (i + 1)
            print(f"[rate-limit] {type(exc).__name__}，等待 {wait:.0f}s 后重试（{i + 1}/{attempts - 1}）...")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def invoke(agent, content: str, *, config: dict, context: Any = None, capture: RequestCapture | None = None):
    cfg = dict(config)
    if capture is not None:
        cfg["callbacks"] = [capture]
    payload = {"messages": [{"role": "user", "content": content}]}
    kw = {"config": cfg, "version": "v2"}
    if context is not None:
        kw["context"] = context
    return _with_retry(lambda: agent.invoke(payload, **kw))


def resume(agent, decisions: list, *, config: dict, context: Any = None):
    cfg = dict(config)
    kw = {"config": cfg, "version": "v2"}
    if context is not None:
        kw["context"] = context
    return _with_retry(lambda: agent.invoke(Command(resume={"decisions": decisions}), **kw))


# --------------------------------------------------------------------------- #
# 中断解析
# --------------------------------------------------------------------------- #
def interrupts(result) -> list:
    return list(getattr(result, "interrupts", None) or [])


def value(result) -> dict:
    return getattr(result, "value", result) or {}


def action_requests(result) -> list:
    ints = interrupts(result)
    return list((ints[0].value or {}).get("action_requests", [])) if ints else []


def action_args(action: dict) -> dict:
    return dict(action.get("arguments") or action.get("args") or {})


def messages_text(result) -> str:
    msgs = value(result).get("messages", []) if isinstance(value(result), dict) else []
    return "\n".join(str(getattr(m, "content", "")) for m in msgs)


# --------------------------------------------------------------------------- #
# 决策构造器
# --------------------------------------------------------------------------- #
def approve() -> dict:
    return {"type": "approve"}


def reject(message: str) -> dict:
    return {"type": "reject", "message": message}


def edit(name: str, args: dict) -> dict:
    return {"type": "edit", "edited_action": {"name": name, "args": dict(args)}}


def today() -> str:
    return date.today().isoformat()


def read_memory(store, editor_id: str, filename: str) -> str:
    item = store.get((editor_id, "memories"), filename)
    return (item.value.get("content") if item else "") or ""


def append_memory(store, editor_id: str, filename: str, line: str) -> None:
    """应用侧向记忆文件追加一行（ch08 外部写入）。"""
    from deepagents.backends.utils import create_file_data

    ns = (editor_id, "memories")
    item = store.get(ns, filename)
    cur = (item.value.get("content") if item else "") or ""
    if line.strip() and line not in cur:
        store.put(ns, filename, create_file_data((cur.rstrip() + "\n" + line + "\n").lstrip("\n")))


def scan(text: str, needles: Iterable[str]) -> dict:
    text = text or ""
    return {n: (n in text) for n in needles}
