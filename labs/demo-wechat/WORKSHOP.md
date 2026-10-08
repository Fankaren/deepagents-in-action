# Task 9-1 · 综合 Demo 工作坊（四拍）

**目标**：把「子 Agent + 技能 + 长期记忆 + 审批」拼成一条能跑的内容流水线，并用前几章的**仪器**验证每一步真的生效。
**主题**：男性向内容微信公众号推文 Agent —— 自己找方向、找易爆选题、按技能统一格式成稿、配免费图床图、**你审批后自行发布**。

---

## 你怎么用

1. **先预测**（见 `learning-notes/Task 9-1/predictions.md`）
2. **运行**
3. **对照观察清单**
4. **改一处再跑**（例如换内容方向、改技能模板、改审批决策）

```powershell
python step0_selftest.py            # 零模型
python run_daily.py --auto-approve  # 先跑通
python run_daily.py                 # 交互审批
```

---

## Step 0 · 仪器单测（零模型）

### 要回答的问题
技能文件、编辑方针标记、namespace 兜底、账本、决策构造器、图床回退，都可信吗？

### 观察清单
- [ ] SKILL.md 存在且含 `WECHAT-SKILL-LOADED`、`name: wechat-article`
- [ ] 编辑方针含 `EDITORIAL-GUIDELINES-LOADED`
- [ ] `user_namespace` 在 `server_info=None` 时回退到 `context.editor_id`
- [ ] 账本/决策构造器/图床回退全 PASS

---

## Step 1 · 跑通主流程（auto-approve）

### 要回答的问题
主编 Agent 会不会**按工作流**依次：读记忆 → 委派选题 → 读技能成稿 → 委派配图 → 写草稿 → 提交审批？

### 观察清单
- [ ] 出现 `task` 委派给 `trend-researcher`、`image-scout`
- [ ] 有 `read_file(/skills/wechat-article/SKILL.md)`
- [ ] 草稿写入 `workspace/drafts/`（磁盘上能 `Get-Content` 看到）
- [ ] 调用 `make_cover` 生成首图（`*-cover.png` 落到 drafts；未调用则 run_daily 兜底生成）
- [ ] 触发 `publish_article` 审批；auto-approve 后账本新增一笔
- [ ] 终稿符合技能骨架（3 标题候选/导语/3 小节/结尾引导/配图位）

### 改一处
把 `--topic "职场"` 换成你关心的方向，或改 SKILL.md 的小节数量，重跑看格式是否随之变化。

---

## Step 2 · 人工审批（交互）

### 要回答的问题
`publish_article` 是否在**副作用之前**暂停？approve / edit（改标题）/ reject（回流）各自落到哪？

### 观察清单
- [ ] 中断时**还没写台账**（副作用未发生）
- [ ] approve → 账本 1 笔、写入 `/memories/topic-ledger.md`
- [ ] edit → 用**改后标题**发布（账本里是新标题）
- [ ] reject → 账本 0 笔、拒绝原因回流给主编

---

## Step 3 · 记忆跨天累积 + 阅读量调优

### 要回答的问题
关掉重开，主编还记得上次吗？给它阅读量数据，它会调整策略吗（**方向不变**）？

```powershell
python run_daily.py --auto-approve                 # 第二次（记忆已在 workspace/.state/store.json）
python memory_cli.py show                          # 看 content-strategy / performance / topic-ledger
python memory_cli.py record --series 底层逻辑 --title "..." --reads 3200 --likes 120 --finish 0.42
python run_daily.py --auto-approve                 # 第三次：规划时应参考 performance
```

### 观察清单
- [ ] 跨进程持久：重开后 `topic-ledger` 仍有上次记录
- [ ] 请求里能看到 `/memories/content-strategy.md`（锁定方向）与 `performance.md`
- [ ] 本轮选题**不偏离**锁定方向、尽量避开台账里已有的
- [ ] `record` 后，下次候选选题/写法与数据呼应（如高完读率系列加码）

### 改一处
用 `set-direction` 覆盖主方向，重跑，确认主编**遵守新方向**（说明方向可被应用侧锁定，不被模型随意改）。

---

## Step 4 · 图床 MCP（ch12 预览，可选）

### 要回答的问题
把图床整理成 MCP 服务后，`image-scout` 能否直接用它拿图？

```powershell
pip install mcp langchain-mcp-adapters
python run_daily.py --mcp --auto-approve
```

### 观察清单
- [ ] `[mcp] 图床 MCP 工具：已加载`
- [ ] 配图 URL 来自 `search_free_images`（Pexels 或 picsum）
- [ ] 未装依赖时自动回退本地工具，不报错

---

## 和课程能力的对应

| 本 Demo 步骤 | 用到章节 |
|--------------|----------|
| Step 1 委派 | ch05 子 Agent（上下文隔离）|
| Step 1/2 成稿 | ch07 Skills（渐进披露）|
| Step 1/3 记忆 | ch08 长期记忆（跨线程、外部写入）|
| Step 2 审批 | ch09 HITL（interrupt_on、四决策）|
| Step 4 图床 | ch12 MCP（预览）|

## 自测（口述）
1. 为什么选题/配图要放**子 Agent**？主上下文看到了什么？
2. SKILL 是「目录」还是「文件」参数？正文何时进入上下文？
3. 记忆文件路径与 Store namespace 怎么对应？写入为什么要应用侧做？
4. `publish_article` 的审批为什么必须用 Checkpointer + 同一 thread_id？
5. 图床换成 MCP 后，Agent 侧工具名/调用方式变了吗？
