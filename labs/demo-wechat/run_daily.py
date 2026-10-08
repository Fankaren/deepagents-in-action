"""Task 9-1 · 每日一条推文工作流（主入口）

流程：读记忆 → 委派 trend-researcher 选题 → 按 SKILL 成稿 → 委派 image-scout 配图
     → 写草稿到 /drafts → publish_article 触发【人工审批】→ 通过后入库。

运行：
    python run_daily.py                 # 本地图床工具
    python run_daily.py --mcp           # 用图床 MCP（ch12 预览）
    python run_daily.py --auto-approve  # 非交互：自动 approve（便于首次跑通）
"""
from __future__ import annotations

import argparse
import json
import os
import re

from make_cover import generate as generate_cover

from _common import (
    EditorContext,
    ToolLedger,
    action_args,
    action_requests,
    append_memory,
    approve,
    banner,
    build_model,
    build_store,
    edit,
    interrupts,
    invoke,
    messages_text,
    new_config,
    read_memory,
    reject,
    resume,
    section,
    today,
)
from agents import build_agent, load_mcp_image_tools, seed_memory

from langgraph.checkpoint.memory import InMemorySaver


def append_ledger(store, editor_id: str, line: str) -> None:
    """审批通过后，应用侧把选题写入长期记忆台账（ch08 外部写入）。"""
    append_memory(store, editor_id, "/topic-ledger.md", line)


def decide_interactively(action: dict) -> dict:
    args = action_args(action)
    print("\n待审批动作：publish_article")
    print("  标题：", args.get("title"))
    print("  草稿：", args.get("draft_path"))
    print("  封面：", args.get("cover_image"))
    choice = input("决策 [a]pprove / [e]dit 标题 / [r]eject ? ").strip().lower()
    if choice.startswith("e"):
        new_title = input("新的标题：").strip() or args.get("title", "")
        edited = dict(args)
        edited["title"] = new_title
        return edit("publish_article", edited)
    if choice.startswith("r"):
        reason = input("拒绝原因：").strip() or "用户拒绝发布，请调整后再试。"
        return reject(reason)
    return approve()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mcp", action="store_true", help="使用图床 MCP 服务（ch12 预览）")
    ap.add_argument("--auto-approve", action="store_true", help="非交互自动批准")
    ap.add_argument("--editor-id", default="editor-001")
    ap.add_argument("--topic", default="", help="可选：指定内容方向种子")
    args = ap.parse_args()

    banner("Task 9-1 · 男性向微信推文 Agent · 每日一篇")
    model = build_model()
    store = build_store()  # 跨天持久化（workspace/.state/store.json）
    checkpointer = InMemorySaver()
    ledger = ToolLedger()
    seed_memory(store, args.editor_id)
    print(f"[记忆] 已加载（持久化）：{os.path.join('workspace', '.state', 'store.json')}")
    strategy = read_memory(store, args.editor_id, "/content-strategy.md")
    first_line = next((l for l in strategy.splitlines() if l.strip().startswith("- 主方向")), "")
    if first_line:
        print(f"[方向锁定] {first_line.strip()}")

    image_tools = load_mcp_image_tools() if args.mcp else None
    if args.mcp:
        print(f"[mcp] 图床 MCP 工具：{'已加载' if image_tools else '不可用，回退本地'}")

    agent = build_agent(
        store=store,
        checkpointer=checkpointer,
        ledger=ledger,
        model=model,
        image_tools=image_tools,
        editor_id=args.editor_id,
    )
    context = EditorContext(editor_id=args.editor_id)
    config = new_config()

    seed_hint = f"本轮指定方向：{args.topic}。" if args.topic else "按已锁定的内容战略推进（不要更换方向）。"
    section("发起主编任务")
    instruction = (
        f"今天是 {today()}。{seed_hint}"
        "请为我整理一篇今日可发布的男性向微信公众号推文：先读 content-strategy（锁定方向/系列）与 performance（阅读量台账），"
        "从 content-plan 推进当前系列选题（可委派 trend-researcher），读 knowledge-base 复用已有沉淀，"
        "严格按 /skills/wechat-article/SKILL.md 成稿（1800-2600 字、6-9 分钟阅读），委派 image-scout 配图，"
        "把终稿写入 /drafts/，调用 make_cover 生成公众号首图，并把新沉淀写入 knowledge-base，"
        "最后调用 publish_article 提交审批。"
    )
    result = invoke(agent, instruction, config=config, context=context)

    reqs = action_requests(result)
    if not interrupts(result):
        print("\n（未产生审批中断——可能模型未调用 publish_article）")
        print(messages_text(result)[-800:])
        return

    action = reqs[0]
    if args.auto_approve:
        decision = approve()
        print("\n[auto-approve] 已自动批准")
    else:
        decision = decide_interactively(action)

    section("提交决策并恢复执行")
    final = resume(agent, [decision], config=config, context=context)

    published = ledger.name_calls("publish_article")
    if published:
        title = published[-1]["args"].get("title", "")
        path = published[-1]["args"].get("draft_path", "")
        append_ledger(store, args.editor_id, f"- {today()} | {title} | {path}")
        print(f"\n已发布就绪（账本）：{ledger.dump()}")
        print("终稿已提交审批通过，请到工作区自取后【自行发布】。")

        # 兜底：确保当日封面存在（主编若已调 make_cover 则跳过）
        try:
            name = os.path.basename(path)
            stem = name[:-3] if name.endswith(".md") else name
            m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+?)(?:-|$)", stem)
            series = m.group(1) if m else "专栏"
            cover_path = os.path.join("workspace", "drafts", stem + "-cover.png")
            if os.path.isfile(cover_path):
                print(f"封面：{cover_path}（主编已生成）")
            else:
                res = generate_cover(title, series, "", cover_path)
                print(f"封面（兜底生成）：{res.get('png') or res.get('svg')}")
        except Exception as exc:  # noqa: BLE001
            print(f"封面生成异常：{exc}")
    else:
        print("\n未执行发布（可能被 reject 或未批准）。")

    print("\n--- 主编最终回复 ---")
    print(messages_text(final)[-1000:])
    print("\n提示：草稿位于 workspace/drafts/ ; 记忆（持久化）已更新。")
    print("下一步（阅读量调优）：发布后记录数据 ——")
    print('  python memory_cli.py record --series "底层逻辑" --title "..." --reads 3200 --likes 120 --finish 0.42')


if __name__ == "__main__":
    main()
