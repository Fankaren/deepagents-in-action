"""Task 9-1 · 组装 Agent

- 主 Agent：男性向微信公众号「内容主编」
- 子 Agent（ch05 上下文隔离）：trend-researcher（选题）、image-scout（配图）
- Skills（ch07）：/skills/wechat-article
- 记忆（ch08，持久化）：content-strategy / content-plan / knowledge-base / performance / topic-ledger
- HITL（ch09）：publish_article 终稿审批
- 图床 MCP（ch12 预览）：可选，失败自动回退本地工具

新增要求（本迭代）：
  ① 主方向锁定 + 系列化体系 + 知识沉淀 + 足够阅读时长；
  ② 依据「阅读量台账 performance.md」调优（方向不变，改选题权重与写法）。
"""
from __future__ import annotations

import asyncio
import os
import sys

from _common import EditorContext, ToolLedger, build_backend, build_model
from tools import build_tools

STRATEGY = """# 内容战略（锁定方向 · 请勿自行更改）
<!-- CONTENT-STRATEGY-LOADED -->
- 品牌：公众号「**他律**」｜Slogan：不靠意志力，靠系统｜栏目统一加前缀「他律·」｜成稿署名与口吻保持一致。
- 主方向（**已锁定**）：男性成长与效率——面向 25-40 岁男性，聚焦「职场底层逻辑 / 财富习惯 / 认知升级 / 决策工具」。
- 内容体系（固定 4 个系列，**轮转推进，不得随机换方向**）：
  1. 《底层逻辑》：职场与商业的第一性原理
  2. 《习惯复利》：财富与自律的长期工程
  3. 《决策工具箱》：可操作的方法与清单
  4. 《认知升级》：反常识与思维模型
- 发布节奏：每日至少 1 篇；**每周回看数据、微调写法，但方向/系列不变**。
- 深度与时长：每篇 **1800-2600 字、阅读约 6-9 分钟**；拒绝水文、凑字。
- 知识沉淀：每篇至少沉淀 1 个可复用「框架/金句/案例」到 knowledge-base。
- 变更规则：主方向与系列一经确认**不得自行更换**；确需调整先向编辑提出并获批。
"""

CONTENT_PLAN = """# 内容规划（系列选题库）
<!-- CONTENT-PLAN-LOADED -->
按系列维护「待写 / 在写 / 已发」；**选题优先从本文件推进，保持体系连贯**。
## A.《底层逻辑》
- [ ] （示例）为什么越忙的人越穷：时间的三种定价
## B.《习惯复利》
- [ ] （示例）复利的最小行动单位：每天 20 分钟
## C.《决策工具箱》
- [ ] （示例）重大决策的 10/10/10 法则
## D.《认知升级》
- [ ] （示例）幸存者偏差如何悄悄误导你
"""

KNOWLEDGE = """# 知识沉淀（跨篇累积）
<!-- KNOWLEDGE-BASE-LOADED -->
按系列记录可复用的**框架 / 金句 / 案例 / 数据**；成稿前检索复用，成稿后追加新沉淀。
## 《底层逻辑》
## 《习惯复利》
## 《决策工具箱》
## 《认知升级》
"""

PERFORMANCE = """# 阅读量台账（用于策略调优）
<!-- PERFORMANCE-LOADED -->
格式：`日期 | 系列 | 标题 | 阅读量 | 点赞 | 完读率 | 复盘`
> 由 `python memory_cli.py record ...` 写入。**规划前必读**：据数据调整选题权重、标题写法与发布时段，但**方向/系列不变**。
"""

LEDGER_TEMPLATE = "# 已发选题台账\n（每行一条「日期 | 系列 | 选题」，用于去重）\n"

MEMORY_FILES = {
    "/content-strategy.md": STRATEGY,
    "/content-plan.md": CONTENT_PLAN,
    "/knowledge-base.md": KNOWLEDGE,
    "/performance.md": PERFORMANCE,
    "/topic-ledger.md": LEDGER_TEMPLATE,
}

MAIN_PROMPT = """你是「男性向微信公众号内容主编」。**铁律：内容方向已在 content-strategy 中锁定，不得自行更换；只在本方向下的 4 个系列内选题。**

工作流：
1. 先读系统提示里的【内容战略 content-strategy】（锁定方向/系列）与【已发选题台账 topic-ledger】（去重），并**务必**读【阅读量台账 performance】了解什么内容表现好。
2. 读【内容规划 content-plan】，从当前系列里推进选题（保持体系连贯）；必要时委派 trend-researcher 补充 3-5 个候选与爆点分析，再据此定 1 个。
3. 读【知识沉淀 knowledge-base】，复用已有框架/金句，避免与前文重复。
4. 用 read_file 打开 /skills/wechat-article/SKILL.md，**严格按其骨架与篇幅纪律**成稿（1800-2600 字、6-9 分钟阅读）。
5. 委派 image-scout 获取每节配图（免费图床 URL）。
6. 把终稿写入 /drafts/<日期>-<系列>-<slug>.md。
7. 把本篇新沉淀的「框架/金句/案例」用 edit_file 追加到 /memories/knowledge-base.md。
8. 调用 publish_article 提交终稿审批（title、draft_path、cover_image）。**发布必须走该工具，不得自行宣布已发布。**
9. 只有工具成功返回后，才汇报「已准备好待发布终稿」。

约束：严格遵守 content-strategy 的方向与禁忌；标题给 3 个候选；篇幅达标；结尾必须有互动引导；不传播未证实结论。
"""


def seed_memory(store, editor_id: str = "editor-001", force: bool = False) -> None:
    """首次初始化记忆文件（ch08：缺失文件跳过/不创建，需显式写入）。"""
    from deepagents.backends.utils import create_file_data

    ns = (editor_id, "memories")
    for key, content in MEMORY_FILES.items():
        if force or store.get(ns, key) is None:
            store.put(ns, key, create_file_data(content))


def load_mcp_image_tools():
    """尝试从图床 MCP 服务加载工具（ch12 预览）；失败返回 None 走本地回退。"""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except Exception:
        return None
    server = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp", "image_server.py")
    client = MultiServerMCPClient(
        {"free-image-host": {"command": sys.executable, "args": [server], "transport": "stdio"}}
    )
    try:
        tools = asyncio.run(client.get_tools())
        return tools or None
    except Exception as exc:  # noqa: BLE001
        print(f"[mcp] 加载图床 MCP 失败，回退本地工具：{exc}")
        return None


def build_subagents(tools: dict, image_tools: list) -> list:
    return [
        {
            "name": "trend-researcher",
            "description": "在已锁定的内容方向内寻找候选选题与爆点（可联网搜热点）。当需要补充选题、判断哪个话题易爆时委派给它。",
            "system_prompt": (
                "你是内容趋势研究员。**只在给定方向内**产出 3-5 个候选选题，每个给出："
                "所属系列、目标人群痛点、爆点分析（为什么易传播）、可复用框架/数据线索。"
                "只做选题侦察，不写全文；不确定的事实标注「需核实」。"
            ),
            "tools": [tools["web_search"]],
        },
        {
            "name": "image-scout",
            "description": "为推文各小节寻找免费图床配图并返回图片 URL。当需要配图/封面时委派给它。",
            "system_prompt": (
                "你是配图专员。针对给定的小节主题，调用图床工具搜索免费图片，"
                "返回每节 1 张图片 URL 及 1 张封面。只返回 URL 与简短用途说明。"
            ),
            "tools": image_tools,
        },
    ]


def build_agent(
    *,
    store,
    checkpointer,
    ledger: ToolLedger,
    model=None,
    image_tools: list | None = None,
    editor_id: str = "editor-001",
):
    from deepagents import create_deep_agent

    model = model or build_model()
    tools = build_tools(ledger)
    image_tools = image_tools or [tools["search_free_images"]]

    return create_deep_agent(
        model=model,
        tools=[tools["publish_article"], tools["web_search"]],
        subagents=build_subagents(tools, image_tools),
        skills=["/skills/"],
        memory=list(MEMORY_FILES.keys()),
        backend=build_backend(),
        store=store,
        checkpointer=checkpointer,
        context_schema=EditorContext,
        interrupt_on={
            "publish_article": {"allowed_decisions": ["approve", "edit", "reject"]},
        },
        system_prompt=MAIN_PROMPT,
    )
