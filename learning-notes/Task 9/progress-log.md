# Task 9 · 学习过程记录（ch09 Human-in-the-Loop）

> 惯例：每个 Step 收尾按三段式记录——**做了什么 / 学到什么 / 遇到什么问题**（参考 Task 4–8）。
> 对应课程：https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/
> 预测题见 `predictions.md`；逐步预测表见 `lab-journal.md`。

---

## 会话 0 · 材料搭建（labs/ch09 + Task 9 模板）

**做了什么**
- 读课程 ch09 原文，梳理主线：`interrupt_on` 配置、四种决策（approve/edit/reject/respond）、条件中断 `when`、中断-恢复流程、子 Agent 独立配置、按风险分层、文件系统权限中断、底层 `interrupt()` 机制与五条规则
- 搭建 `labs/ch09`：`_common.py`（ToolLedger 副作用账本 / RequestCapture / Judge / 决策构造器 / v2 invoke-resume）+ step0 仪器单测 + step1~5 实验脚本 + WORKSHOP.md
- 建立 Task 9 模板：README / lab-journal / predictions / progress-log / 小结（待跑）
- 模型沿用商汤日日新 `glm-5.2`；内置 429 限速自愈（`CH09_*`）

**学到什么**
- 本章观测点与记忆章不同：不是「内容有没有进上下文」，而是**「暂停有没有发生、副作用有没有在审批前误触发」** → 仪器换成**副作用账本**
- HITL 三铁律：**Checkpointer 必需** + **同一 `thread_id`** + **`version="v2"`**
- 决策语义：`respond` 是「人亲自当工具结果」，副作用工具必须用 `reject`

**遇到什么问题**
- （待跑后补）

---

## 逐 Step 记录（三段式）

### Step 0 · 仪器单测 + 判定器体检

**做了什么**
- 预测：Q0-1=A（全 PASS）、Q0-2=B（观测点=工具副作用账本）
- 运行 `python step0_selftest.py`（**零模型调用**）：判定器 **14/14 PASS**

**学到什么**
- 本章的量具是**副作用账本**：把「危险动作有没有发生」变成「账本里有没有那一笔」，可观测、成本≈0
- 单测覆盖：ledger 增删取参、四种决策构造器形状、中断结构解析（兼容 `arguments`/`args`）、无中断时返回空、金丝雀扫描
- 与 ch08 一致：仪器先行，先证明量具可信再跑真模型

**遇到什么问题**
- 无（14/14 全 PASS，未消耗模型额度）

### Step 1 · 首次中断（approve）

**做了什么**
- 预测：Q1-1=B、Q1-2=A、Q1-3=B、Q1-4=B
- 运行 `step1_first_interrupt.py`：判定器 **6/6 PASS**
- 中断动作 `send_email`，参数 `{to: admin@example.com, subject: 通知, body: 系统维护}`

**学到什么**
- **Q1-4 预测错（B→A）**：`approve` 使用 Agent 的**原始参数**（照单全收）；改参数是 `edit` 的职责——approve≠"确认后可改"
- 暂停确实在副作用**之前**：中断时账本为 `[]`（危险动作未发生）——这正是 HITL 的意义
- approve 后账本恰好 **1 笔、原始参数**；工具结果 `EMAIL-SENT` 进入消息历史，模型据此回复"已发送"

**遇到什么问题**
- 无

### Step 2 · 三种决策（approve / reject / edit）

**做了什么**
- 预测：Q2-1=B、Q2-2=A、Q2-3=B
- 运行 `step2_decisions.py`：判定器 **6/6 PASS**

**学到什么**
- **Q2-1 预测错（B→A）**：`reject` 后账本 **0 笔**——工具**完全没执行**（不是"执行后再撤销"）
- `reject` 的 `message` 作为 ToolMessage **回流给模型**（后续请求命中"站内通知"）→ 模型可据此改道
- `edit` 用**改后参数**（`to=team@example.com`）执行一次
- 三种决策在账本上**完全可区分**：approve=1 笔原参 / edit=1 笔改参 / reject=0 笔

**遇到什么问题**
- 无

### Step 3 · respond + 批量中断

**做了什么**
- 预测：Q3-1=A、Q3-2=B、Q3-3=A
- 首跑：respond 组通过，但**批量断言 FAIL**（模型串行、只调了 SQL）→ 修 `step3` 缺 `import interrupts`，并把批量改成**鲁棒循环**（多轮中断）+ 强化「同轮并行调用」提示
- 重跑：判定器 **6/6 PASS**；本轮 `glm-5.2` **同轮并行**调用两工具（首轮 2 动作、共 1 轮）→ 打包成一个中断

**学到什么**
- **Q3-1 预测错（A→B）**：`respond` 时工具体**不执行**，人的 `message` 直接当**成功的工具结果**（区别于 `reject`「工具没执行」）
- **Q3-2 预测错（B→A）**：一次调用多个工具时，中断**打包成一个**（本轮实测 1 轮 2 动作）；但**能否打包取决于模型是否同轮发多个 tool_calls**——首跑串行就没打包，强化提示后才并行
- `decisions` 与 `action_requests` **一一对应**（SQL approve、email reject → 只有 SQL 执行）
- 结论：打包是「并行调用」的结果，而是否并行是**模型行为**，不是框架保证

**遇到什么问题**
- `step3` 漏 `import interrupts` → `NameError`（已修）
- 批量行为受模型影响（串行 vs 并行）→ 测试改成鲁棒循环 + 打印「轮次/首轮动作数」观察

### Step 4 · 条件中断 + 文件系统权限中断

**做了什么**
- 预测：Q4-1=B、Q4-2=A、Q4-3=A —— **全对**
- 运行 `step4_conditional_fs.py`：判定器 **5/5 PASS**（A 组条件中断可用，本机 langchain 满足 `>=1.3.3`）

**学到什么**
- **条件中断 `when` 生效**：区内 `/workspace/notes.txt` **不中断**且文件落盘（`files=['/workspace/notes.txt']`）；区外 `/notes.txt` **中断**
- **文件系统权限中断生效**：写 `/secrets/token.txt` 触发中断，动作名 `write_file`，与 `interrupt_on` 的中断**格式一致**（同一套 `Command(resume=...)` 恢复）
- `when` 谓词的意义：返回 `True` 才中断——审批界面只展示真正需要人决策的动作
- `FilesystemPermission(operations=["write"], mode="interrupt")`：保护的是「写入/覆盖/删除」，不是仅"新建"

**遇到什么问题**
- 无

### Step 5 ·（选做）底层 interrupt()

**做了什么**
- 预测：Q5-1=A、Q5-2=A
- 运行 `step5_custom_interrupt.py`：判定器 **3/3 PASS**
- 自定义 `DraftApprovalMiddleware.after_model` 里 `interrupt()` 触发（类型 `draft_review`）；用 `Command(resume={"approved": True})` 恢复；批准后不再暂停

**学到什么**
- **Q5-1 预测错（A→B）**：底层 `interrupt()` 的恢复是**直接把值传给 `interrupt()` 的返回值**（`{"approved": True}`），**不是**工具审批的 `{"decisions":[...]}`——两套 resume 格式不同
- **Q5-2 预测错（A→B）**：恢复时节点**从头重放**，不是从 `interrupt()` 下一行继续 → 由此推出四条规则：副作用要**幂等**、**不裸 try/except**、**不动态改调用顺序**、并行中断用 **`Interrupt.id` 映射**
- `after_model` 等 Node-style Hook 可作暂停点，并通过 `middleware=[...]` 注入 Deep Agents（`interrupt_on` 覆盖不到的场景）

**遇到什么问题**
- 无（本机支持 `AgentMiddleware.after_model` + 底层 `interrupt()`）

---

## 待办 / 下一步

- [x] 预测：在 `predictions.md` 作答（Step 0 已作，A/B）
- [x] Step 0：仪器单测 + 判定器体检（零模型调用，14/14 PASS）
- [x] Step 1：首次中断（暂停时副作用为零 → approve 原参执行，6/6 PASS；Q1-4 预测错=B→实际A）
- [x] Step 2：三决策对照（approve / reject 回流 / edit 改参，6/6 PASS；Q2-1 预测错=B→实际A）
- [x] Step 3：respond + 批量中断（6/6 PASS；Q3-1/Q3-2 预测错；模型同轮并行时打包成一个中断）
- [x] Step 4：条件中断 when + 文件系统权限中断（5/5 PASS，预测全对）
- [x] Step 5（选做）：自定义 Middleware + 底层 interrupt()（3/3 PASS；Q5-1/Q5-2 预测错）
- [x] 收尾：`ch09-lab-summary.md` + 推送
