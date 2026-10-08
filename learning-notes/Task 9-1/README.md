# Task 9-1 · 综合 Demo（男性向微信推文 Agent）

对应：**综合项目**（融合 ch05 子 Agent + ch07 Skills + ch08 长期记忆 + ch09 HITL；图床 MCP 为 ch12 预览）

## 怎么学

沿用四拍工作坊 + 判定器体检 + 仪器单测 + 副作用账本。与单章实验不同，这里是**端到端项目**：
一条「找方向 → 选题 → 按技能成稿 → 配图 → 审批 → 入库」的流水线。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` / `progress-log.md` / `predictions.md` | 记录与预测 |
| `demo-lab-summary.md` | 实测小结（提交主文档，**待跑**）|
| `labs/demo-wechat/README.md` | Demo 说明与架构 |
| `labs/demo-wechat/WORKSHOP.md` | 四拍步骤与观察清单 |
| `labs/demo-wechat/_common.py` | 模型 / namespace / CompositeBackend / 仪器 / 账本 / 判定器 / v2 |
| `labs/demo-wechat/tools.py` | web_search / 图床回退 / publish_article(HITL) |
| `labs/demo-wechat/agents.py` | 主 Agent + trend-researcher/image-scout 子 Agent |
| `labs/demo-wechat/run_daily.py` | 每日一篇主流程（含交互审批）|
| `labs/demo-wechat/skills/wechat-article/SKILL.md` | 统一推文格式技能 |
| `labs/demo-wechat/mcp/image_server.py` | 免费图床 MCP 服务（ch12 预览）|
| `labs/demo-wechat/step0_selftest.py` | 零模型仪器单测 |

## 本机版本基线

- deepagents（>=0.6.8）/ langchain（>=1.3.3）/ langchain-openai；模型经**商汤日日新**接入 `glm-5.2`
- 记忆：`CompositeBackend(default=FilesystemBackend(workspace), routes={"/memories/": StoreBackend(user_namespace)})`
- 技能放**磁盘** `workspace/skills/`；草稿写 `workspace/drafts/`
- 审批：`interrupt_on={"publish_article": {"allowed_decisions":["approve","edit","reject"]}}`
- MCP：`mcp` + `langchain-mcp-adapters`，未装自动回退本地图床工具

（待办：Step 0–4 跑完后补 `demo-lab-summary.md`）
