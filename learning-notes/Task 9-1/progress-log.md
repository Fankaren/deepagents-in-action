# Task 9-1 · 学习过程记录（综合 Demo）

> 惯例：每步收尾三段式——**做了什么 / 学到什么 / 遇到什么问题**。

---

## 会话 0 · 需求与材料搭建

**做了什么**
- 确认需求：男性向内容微信推文 Agent——自己找方向 + 找易爆选题 + 按技能统一格式 + 免费图床配图（MCP）+ 每日至少一篇 + **人工审批后自行发布**
- 设计组合：**子 Agent（ch05）+ Skills（ch07）+ 长期记忆（ch08）+ HITL（ch09）+ 图床 MCP（ch12 预览）**
- 搭建 `labs/demo-wechat`：`_common.py` / `tools.py` / `agents.py` / `run_daily.py` / `skills/wechat-article/SKILL.md` / `mcp/image_server.py` / `step0_selftest.py` + README/WORKSHOP
- 建立 Task 9-1 记录模板

**学到什么**
- 综合项目的关键是**职责切分**：知识（记忆）/ 能力（技能）/ 侦察（子 Agent）/ 安全（审批）各自落到合适的章法
- 记忆 + 技能可共存于一个 `CompositeBackend`：磁盘放 skills/草稿，Store 放 /memories/
- 敏感动作（发布）用 `publish_article` 工具承载，天然接入 HITL

**遇到什么问题**
- 无

---

## 会话 1 · 需求迭代：锁定方向 + 体系化 + 阅读量调优

**做了什么**
- 新增两条需求：① 方向一旦确认不轻易换 + 体系化/知识沉淀/足够阅读时长；② 依据阅读量调优
- 关键改动：
  - **记忆持久化**：`InMemoryStore` → `_JsonFileStore`（只拦截 `batch/abatch`，镜像到 `workspace/.state/store.json`），**跨进程/跨天可读**
  - 记忆文件从 2 个扩到 **5 个**：`content-strategy`（锁定方向+4 系列）/ `content-plan`（系列选题库）/ `knowledge-base`（知识沉淀）/ `performance`（阅读量台账）/ `topic-ledger`
  - `SKILL.md` 升级为**体系化长文**：系列标识 + 4-5 小节 + **1800-2600 字 / 6-9 分钟** + 「本篇沉淀」
  - `MAIN_PROMPT` 加铁律：**锁定方向不得自换**、规划前**必读 performance**、成稿后写 knowledge-base
  - 新增 `memory_cli.py`：`show` / `set-direction` / `add-plan` / `record`（记录阅读量）
  - `step0_selftest.py` 增校验：战略标记、4 系列、篇幅纪律、**持久化跨实例**

**学到什么**
- 「跨天记忆」不是 `memory=` 的问题，而是 **Store 是否持久化**——`InMemoryStore` 进程结束即丢；用 `InMemoryStore` 子类 + 拦截 `batch` 落 JSON 是最小改动方案
- 「方向锁定」靠**应用侧写死 content-strategy**（`set-direction`）+ 提示词铁律，而不是靠模型自觉
- 「按阅读量调优」= 把数据沉淀成 `performance.md`，规划前读取；**方向不变、只调写法/权重**，与「方向锁定」不矛盾

**遇到什么问题**
- 原 `step0` 引用了已改名的 `agents.GUIDELINES` → 改为 `STRATEGY`（已修）
- `_JsonFileStore` 需处理 `PutOp.value is None`（删除）与 JSON 序列化；用镜像字典记录每次 put

---

## 逐 Step 记录（三段式）

### Step 0 · 仪器单测
**做了什么**
- 按需求：**本 Demo 不设预测题**
- 运行 `python step0_selftest.py`：判定器 **21/21 PASS**（迭代后新增：战略标记、4 系列、篇幅纪律、持久化跨实例）

**学到什么**
- 技能与记忆的观测标记就位（`WECHAT-SKILL-LOADED` / `CONTENT-STRATEGY-LOADED`）
- `user_namespace` 在 `server_info=None` 时回退到 `context.editor_id`
- 图床无 `PEXELS_API_KEY` 时回退 `picsum.photos`
- **持久化 Store 跨实例可读**——跨天记忆的底座已验证

**遇到什么问题**
- 无

### Step 1 · 跑通主流程
**做了什么**
- 运行 `run_daily.py --auto-approve`：**端到端跑通**
- 主编读 5 个记忆 → 委派 `trend-researcher` 出 5 个候选 → 按 SKILL 成稿（**2200 字 / 7 分钟 / 4 节 + 可复用框架**）→ 委派 `image-scout` 取 5 张免费图床图 → 写草稿 → 沉淀 knowledge-base + 标记 content-plan + 记录 topic-ledger → `publish_article` 审批通过

**学到什么**
- **融合成立**：子 Agent（侦察/配图）+ 技能（统一格式）+ 记忆（方向/沉淀/台账）+ HITL（发布审批）串成一条真实流水线
- **记忆真持久**：`store.json` 里 knowledge-base 累积了「年度时间余额表」框架 + 3 条金句；content-plan 把该选题标为已发——**跨进程可读**
- 产物合规：系列标识、4 节、篇幅/时长达标、附 3 个标题候选

**遇到什么问题**
- **路径前缀嵌套**：初版把草稿写 `/workspace/drafts` → 实际落到 `workspace/workspace/drafts`。根因：`FilesystemBackend(root_dir=workspace)` 下虚拟路径应为 `/drafts`、`/skills`，不是 `/workspace/...`。已修（并把已有草稿搬正）
- **Windows 并发保存冲突**：`_JsonFileStore` 纯读也落盘 + 并行工具调用 → `store.json.tmp` 占用 `WinError 32`。已修：仅含 PutOp 时落盘 + `threading.Lock` + 唯一 tmp + 重试

### Step 2 · 人工审批
**做了什么**
- 交互式跑 `run_daily.py`，在审批处选 **`e`（edit）**，把标题改为 `test`，再恢复执行

**学到什么**
- **edit 的真实效果**：`publish_article` 用**改后标题**执行（账本 `title=test`）；草稿文件名仍是原标题——决策只改**工具参数**，不重写草稿内容
- 审批发生在副作用（写台账）**之前**；只有 approve/edit 才产生账本记录
- 与 ch09 一致：approve=原参、edit=改参、reject=不执行

**遇到什么问题**
- 台账被**两方各写一套格式**：agent 写「日期 | 系列 | 选题」，应用侧 append「- 日期 | 标题 | 路径」→ 出现混排与近似重复。建议收敛为单一写入方（都用 agent 或都用 `memory_cli`）

### Step 3 · 记忆跨天累积 + 阅读量调优
**做了什么**
- 录入阅读量：`memory_cli.py record` → `performance.md` 出现一行数据
- 第三次 `run_daily.py`：主编推进**《决策工具箱》**，并在「选题依据」里**引用了 performance 的完读率 0.42**，据此改为「更强开头钩子、更紧凑节奏」，同时**复用 knowledge-base** 里前两篇的框架（时间余额 / 沉没成本）
- `memory_cli.py show` 确认 5 个记忆文件持久化，knowledge-base 已跨三个系列累积

**学到什么**
- **跨天持久化兑现**：关掉重开，方向/规划/沉淀/数据都在（`store.json`）
- **阅读量调优兑现**：主编规划前读取 `performance` 并据此调整写法（**方向/系列未变**）——正是需求②
- **体系化兑现**：四系列轮转推进、知识跨系列复用（需求①）

**遇到什么问题**
- `topic-ledger` 格式被混写、并混入 demo 的 `test` 标题（数据污染，实际使用会更干净）
- 建议：台账单一写入方 + 固定列格式

### Step 4 · 图床 MCP（可选）
**做了什么**
**学到什么**
**遇到什么问题**

---

## 待办 / 下一步
- [x] Step 0：仪器单测（零模型，21/21 PASS；含持久化跨实例）
- [x] Step 1：跑通主流程（端到端 PASS；修复路径嵌套 + 并发保存）
- [x] Step 2：人工审批（edit 改标题 → 用改后标题发布；台账两方混写待收敛）
- [x] Step 3：记忆跨天累积 + 阅读量调优（持久化兑现；主编引用完读率 0.42 调整写法）
- [ ] Step 4：图床 MCP（可选，未跑）
- [x] 收尾：`demo-lab-summary.md` + 推送
