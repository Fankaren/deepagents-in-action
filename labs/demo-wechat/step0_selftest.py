"""Task 9-1 · 仪器单测（零模型调用）

校验：技能文件与编辑方针的观测标记、namespace 兜底、副作用账本、决策构造器、图床本地回退。
运行：python step0_selftest.py
"""
import os
from types import SimpleNamespace

import agents
import tools
from _common import (
    EditorContext,
    Judge,
    ToolLedger,
    approve,
    build_store,
    edit,
    memory_namespace,
    reject,
    user_namespace,
)

SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", "skills", "wechat-article", "SKILL.md")


def main() -> None:
    judge = Judge("Task 9-1 Step0 仪器单测")

    # 1) 技能文件（ch07）：存在 + 观测标记 + frontmatter
    judge.check("SKILL.md 存在", os.path.isfile(SKILL))
    text = open(SKILL, encoding="utf-8").read() if os.path.isfile(SKILL) else ""
    judge.check("SKILL 含观测标记 WECHAT-SKILL-LOADED", "WECHAT-SKILL-LOADED" in text)
    judge.check("SKILL frontmatter name=wechat-article", "name: wechat-article" in text)
    judge.check("SKILL description 具体（含触发场景）", "description:" in text and "推文" in text)

    # 2) 内容战略（ch08 记忆）观测标记
    judge.check("内容战略含 CONTENT-STRATEGY-LOADED", "CONTENT-STRATEGY-LOADED" in agents.STRATEGY)

    # 3) namespace 兜底（server_info 为空时用 context.editor_id）
    rt = SimpleNamespace(server_info=None, context=EditorContext(editor_id="editor-xyz"))
    judge.check("user_namespace 兜底", user_namespace(rt) == ("editor-xyz", "memories"))
    judge.check("memory_namespace", memory_namespace("editor-abc") == ("editor-abc", "memories"))

    # 4) 副作用账本（ch09）
    led = ToolLedger()
    led.record("publish_article", {"title": "t"})
    judge.check("ledger 计数", led.count("publish_article") == 1 and led.count() == 1)
    led.reset()
    judge.check("ledger reset", led.count() == 0)

    # 5) 决策构造器
    judge.check("approve", approve() == {"type": "approve"})
    judge.check("reject", reject("no") == {"type": "reject", "message": "no"})
    judge.check(
        "edit",
        edit("publish_article", {"title": "x"})
        == {"type": "edit", "edited_action": {"name": "publish_article", "args": {"title": "x"}}},
    )

    # 6) 图床本地回退（无 PEXELS_API_KEY → picsum）
    os.environ.pop("PEXELS_API_KEY", None)
    urls = tools._free_image_urls("健身", 3)
    judge.check("图床回退返回 3 个 URL", len(urls) == 3)
    judge.check("回退用 picsum.photos", all("picsum.photos" in u for u in urls), str(urls))
    md = tools.image_markdown(urls, "配图")
    judge.check("image_markdown 生成 3 段", md.count("![") == 3)

    # 7) 内容战略（锁定方向）与技能篇幅纪律
    judge.check("战略含锁定标记", "CONTENT-STRATEGY-LOADED" in agents.STRATEGY)
    judge.check("战略声明方向已锁定", "已锁定" in agents.STRATEGY)
    judge.check("战略含 4 个系列", agents.STRATEGY.count("《") >= 4)
    judge.check("记忆文件数=5", len(agents.MEMORY_FILES) == 5, str(list(agents.MEMORY_FILES)))
    judge.check("SKILL 篇幅 1800-2600", "1800-2600" in text and "6-9 分钟" in text)

    # 8) 持久化 Store 跨实例（跨天记忆）
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", ".state", "_selftest.json")
    if os.path.exists(p):
        os.remove(p)
    s1 = build_store(p)
    s1.put(("editor-001", "memories"), "/x.md", {"content": "hello", "encoding": "utf-8"})
    s2 = build_store(p)
    item = s2.get(("editor-001", "memories"), "/x.md")
    judge.check("持久化 Store 跨实例可读", item is not None and item.value.get("content") == "hello")
    if os.path.exists(p):
        os.remove(p)

    judge.report(exit_on_fail=True)


if __name__ == "__main__":
    main()
