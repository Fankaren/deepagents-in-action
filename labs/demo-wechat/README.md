# Task 9-1 · 综合 Demo：男性向微信公众号推文 Agent

把前几章能力拼成一条**真实可跑的内容生产流水线**：

| 能力 | 章节 | 在本 Demo 里的落点 |
|------|------|-------------------|
| 子 Agent（上下文隔离）| ch05 | `trend-researcher`（选题）、`image-scout`（配图）|
| Skills（渐进披露）| ch07 | `/skills/wechat-article/SKILL.md` 统一推文格式 |
| 长期记忆（跨线程）| ch08 | `/memories/editorial-guidelines.md`、`/memories/topic-ledger.md` |
| Human-in-the-Loop | ch09 | `publish_article` 终稿审批（approve/edit/reject）|
| 图床 MCP（预览）| ch12 | `mcp/image_server.py` 免费图床服务（可选 `--mcp`）|

> 说明：本篇是**综合项目**，不是课程某章实验；用到的能力都来自你已学的章节。
> MCP 属 ch12 预览，未装依赖时自动回退本地图床工具，不影响跑通。

## 架构

```text
                 ┌────────────────────────── 主编 Agent ──────────────────────────┐
用户(编辑)  ──▶  │ 记忆: /memories/editorial-guidelines.md, /memories/topic-ledger.md │
                 │ 技能: /skills/wechat-article/SKILL.md（统一格式）                  │
                 │ 工具: web_search, publish_article(HITL)                            │
                 └───────┬───────────────────────────────┬───────────────────────────┘
                         │ task()                        │ task()
                 ┌───────▼────────┐              ┌───────▼────────┐
                 │ trend-researcher│              │  image-scout   │
                 │  选题/爆点分析   │              │ 免费图床配图(MCP)│
                 └────────────────┘              └────────────────┘
```

流程：读记忆 → 子Agent 选题 → read SKILL 按模板成稿 → 子Agent 配图 → 写草稿到 `workspace/drafts/` → `publish_article` **触发审批** → 通过后写入选题台账（你自行发布）。

## 实测证据（Evidence）

`evidence/` 是本 Demo **一次真实运行的测试数据备份**（2026-10-08，商汤日日新 `glm-5.2`），用于佐证端到端可用：

- `evidence/drafts/`：主编按 SKILL 生成的体系化长文（含免费图床配图 URL）
- `evidence/memory/`：锁定方向、系列规划、知识沉淀、阅读量台账、去重台账（5 个记忆文件）
- `evidence/store.snapshot.json`：**持久化 Store 快照**（跨天记忆的落地格式）
- 复现路径见 `evidence/README.md`（`step0_selftest.py` 21/21 → `set-direction` → `run_daily.py` → `record` → 再跑）

> live 运行态（`workspace/.state/`、`workspace/drafts/`）已 gitignore；正式产物以 `evidence/` 快照为准。

## 环境

```powershell
# 在项目根：
start_env.bat demo-wechat   # 首次自动建 venv 并装依赖
# 或手动：
pip install -r labs/demo-wechat/requirements.txt
```

复制 `.env.example` 为 `.env` 并填 `SENSENOVA_API_KEY`（可选 `PEXELS_API_KEY`）。

## 运行

```powershell
python step0_selftest.py                 # 零模型：仪器单测
python run_daily.py                      # 交互式（会停下来让你审批终稿）
python run_daily.py --auto-approve       # 非交互自动批准（首次跑通用）
python run_daily.py --mcp                # 用图床 MCP（需装 mcp + langchain-mcp-adapters）
python run_daily.py --topic "职场"       # 指定本轮方向种子（仍受锁定方向约束）
```

审批时可选：`a` 批准 / `e` 改标题 / `r` 拒绝（拒绝原因会回流给主编）。

## 记忆与调优（跨天持久）

记忆存在 `workspace/.state/store.json`（`InMemoryStore` 子类 + JSON 落盘），**关掉重开仍在**。用 `memory_cli.py` 管理：

```powershell
python memory_cli.py show                                   # 查看全部记忆
python memory_cli.py set-direction "主方向：男性成长与效率；系列：《底层逻辑》《习惯复利》《决策工具箱》《认知升级》"
python memory_cli.py add-plan "《底层逻辑》选题：为什么越忙越穷"
python memory_cli.py record --series 底层逻辑 --title "..." --reads 3200 --likes 120 --finish 0.42 --note "标题偏长"
```

| 记忆文件 | 作用 | 谁写 |
|----------|------|------|
| `/memories/content-strategy.md` | **锁定方向 + 4 系列体系 + 篇幅/节奏** | 你（`set-direction`）|
| `/memories/content-plan.md` | 系列选题库（体系化推进）| 你 / 主编 |
| `/memories/knowledge-base.md` | 知识沉淀（框架/金句/案例）| 主编（成稿后）|
| `/memories/performance.md` | 阅读量台账（调优依据）| 你（`record`）|
| `/memories/topic-ledger.md` | 已发选题去重 | 应用（审批通过后）|

**两条规则**：① 方向一经确认**不轻易更换**，只在本方向的 4 系列里做体系化长文（1800-2600 字 / 6-9 分钟）；② 规划前**必读 performance**，按阅读量调选题权重与写法（方向不变）。

## 文件

| 文件 | 说明 |
|------|------|
| `_common.py` | 模型、namespace 兜底、CompositeBackend(磁盘+Store)、请求级仪器、副作用账本、判定器、v2 invoke/resume |
| `tools.py` | `web_search`（免费热点搜索）、`search_free_images`（图床本地回退）、`publish_article`（HITL 敏感工具）|
| `skills/wechat-article/SKILL.md` | 统一推文格式（固定骨架 + 标题/文风/配图纪律）|
| `agents.py` | 组装：主 Agent + 两个子 Agent + 记忆/技能/HITL/MCP |
| `run_daily.py` | 每日一篇工作流（含交互审批）|
| `memory_cli.py` | 记忆管理（show / set-direction / add-plan / record 阅读量）|
| `make_cover.py` | 生成公众号首图（填充标题并渲染 PNG）|
| `daily_run.bat` | 每日定时跑（配合 Windows 任务计划）|
| `mcp/image_server.py` | 免费图床 MCP 服务（ch12 预览）|
| `brand/` | 品牌「他律手记」：头像（定稿 enso）、封面模板、命名与合规说明 |
| `step0_selftest.py` | 零模型仪器单测 |

## 观测点（沿用前几章）

- **技能**：终稿是否严格按 SKILL 骨架（观测标记 `WECHAT-SKILL-LOADED`）。
- **记忆**：编辑方针是否进入模型请求；审批通过后台账是否新增。
- **HITL**：`publish_article` 是否在副作用（写台账）之前暂停；approve/edit/reject 的账本差异。
- **子 Agent**：选题/配图是否由子 Agent 完成（主上下文只见报告）。
