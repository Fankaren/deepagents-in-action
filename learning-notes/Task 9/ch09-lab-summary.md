# Task 9 · ch09 Human-in-the-Loop —— 实验小结

**对应课程**：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/>
**环境基线**：deepagents（>=0.6.8）/ langchain（>=1.3.3）/ 商汤日日新 `glm-5.2`（无需起服务）
**实验方法**：四拍工作坊 + 判定器体检 + **副作用账本 ToolLedger** + 请求级 callback 仪器
**材料**：`labs/ch09/`（`_common.py` + step0~5 + WORKSHOP.md）；过程日志 `progress-log.md`

---

## 一、实验总览与实测结果

| Step | 问题 | 预测 vs 实测 | 关键证据 |
|------|------|--------------|----------|
| 0 | 仪器可信吗 | 全中 | 判定器 **14/14**（账本 / 决策构造器 / 中断解析） |
| 1 | 暂停时副作用发生没 | **Q1-4 错** | 中断时账本 `[]`；approve 后 1 笔、原始参数；EMAIL-SENT 进历史；**6/6** |
| 2 | 三决策差异 | **Q2-1 错** | approve 原参 / edit 改参 / **reject 0 笔**；reject message 回流；**6/6** |
| 3 | respond 与批量 | **Q3-1、Q3-2 错** | respond 工具体不执行、人话成工具结果；同轮并行→打包成 1 个中断；**6/6** |
| 4 | 选择性拦截 | 全中 | 区内不中断、区外中断；`/secrets/**` 中断；**5/5** |
| 5 | 底层 interrupt() | **Q5-1、Q5-2 错** | draft_review 中断；raw value 恢复；**3/3** |

**预测命中**：Q0-1/2、Q1-1/2/3、Q2-2/3、Q3-3、Q4-1/2/3；**押错 6 题**：Q1-4、Q2-1、Q3-1、Q3-2、Q5-1、Q5-2。

---

## 二、知识主线（实测支撑）

### 1. `interrupt_on` 与四种决策（账本判据）

| 决策 | 账本表现 | 语义 | 实测 |
|------|----------|------|------|
| approve | 1 笔、**原参** | 批准 | Step1/2 |
| edit | 1 笔、**改后参** | 改参执行 | Step2（team@…） |
| reject | **0 笔** | 不执行 + 反馈回流 | Step2 |
| respond | 工具**不执行** | 人的话当成功工具结果 | Step3 |

- **易错点**：approve 用**原始参数**（不是"确认后可改"）；reject 是**完全不执行**（不是先执行再撤销）；respond 不等于 reject

### 2. 中断-恢复流程与三铁律

- **Checkpointer 必需** + **同一 `thread_id`** + **`version="v2"`**
- 中断结构：`action_requests` / `review_configs`；恢复 `Command(resume={"decisions":[...]})`
- 一次性调用多个工具时，中断**打包成一个**（多个 action 按序决策）——**前提是模型同轮并行发多个 tool_calls**

### 3. 选择性拦截

- 条件中断 `when`（langchain>=1.3.3）：返回 `True` 才中断；区内写不拦、区外写拦（Step4 实测）
- 文件系统权限中断：`FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="interrupt")`；`write` 覆盖写入/覆盖/删除；与 `interrupt_on` 中断**格式一致**可合并

### 4. 底层 `interrupt()` 机制

- 靠**抛异常**暂停；恢复时节点**从头重放** → 副作用幂等、不裸 `try/except`、不动态改顺序、并行用 `Interrupt.id` 映射
- 工具审批用 `{"decisions":[...]}`；底层 `interrupt()` 用**任意 resume 值**（本项目 `{"approved": True}`）

---

## 三、方法论遗产（本章新增 / 复现）

1. **副作用账本 ToolLedger**：把「危险动作有没有发生」转成「账本里有没有那一笔」——判定 approve/edit/reject/respond 四态**完全可区分**
2. **判定器与模型行为解耦**：批量「打包」与否取决于模型是否并行调用 → 改成**鲁棒循环 + 观察项**，硬断言只压「两工具都被审批 + 最终账本正确」（Step3 首跑 FAIL 的教训）
3. **预测的价值**：本章押错 6 题（含 approve 原参、reject 零执行、respond 不执行、resume 格式、从头重放），每题都是概念盲点
4. **限速自愈**：`CH09_*` 调用间隔 + 退避重试，全程未因 429 阻塞
5. **区别于记忆章**：观测点从「内容进没进上下文」换成「暂停/副作用/恢复」

---

## 四、与课程原文对应

| 工作坊 | 课程 ch09 知识点 |
|--------|------------------|
| Step 1 | `interrupt_on`、四种决策、中断/恢复、`version="v2"` |
| Step 2 | approve/edit/reject 语义与拒绝反馈 |
| Step 3 | respond（ask_user）、批量中断的决策顺序 |
| Step 4 | 条件中断 `when`、文件系统权限中断 |
| Step 5 | 底层 `interrupt()`、自定义 Middleware、五条规则 |

自测题见 `labs/ch09/WORKSHOP.md` 文末；逐会话过程记录见 `progress-log.md`；预测题与解析见 `predictions.md`。
