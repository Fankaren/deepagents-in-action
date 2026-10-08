# Task 9 · ch09 Human-in-the-Loop（interrupt_on / 中断恢复 / 按风险分层）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/>

## 怎么学

沿用四拍工作坊 + 判定器体检 + 仪器单测（ch05~08 遗产）。**无需起服务**，轻量模式。
本章观测点：**「暂停 → 决策 → 恢复」**。核心仪器是 **工具副作用账本 `ToolLedger`**（工具真正执行才记一笔），
配合**中断结构解析**与**请求级捕获**（验证 `reject` 反馈回流）。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板（预测 vs 实际） |
| `progress-log.md` | 会话过程记录（每会话收尾追加） |
| `predictions.md` | 每个 Step 的预测题（先作答再执行） |
| `ch09-lab-summary.md` | 实测小结（提交主文档，**待跑**） |
| `labs/ch09/WORKSHOP.md` | 一步步怎么做（四拍） |
| `labs/ch09/_common.py` | 仪器与判定器（ToolLedger / RequestCapture / Judge / 决策构造器 / v2 invoke-resume） |
| `labs/ch09/step0_selftest.py` | **零模型调用**：仪器单测 + 判定器体检 |
| `labs/ch09/step1_first_interrupt.py` | 首次中断：暂停时副作用为零；approve 用原参执行 |
| `labs/ch09/step2_decisions.py` | 三决策对照：approve / reject（不执行+回流）/ edit（改参执行） |
| `labs/ch09/step3_respond_batch.py` | respond（人工输入型）+ 批量中断的决策顺序 |
| `labs/ch09/step4_conditional_fs.py` | 条件中断 `when` + 文件系统权限中断 |
| `labs/ch09/step5_custom_interrupt.py` | （选做）自定义 Middleware + 底层 `interrupt()` |

## 本机版本基线

- deepagents（需 `>=0.6.8` 才有文件系统权限中断）/ langchain（需 `>=1.3.3` 才有条件中断 `when`）/ langchain-openai；模型经**商汤日日新**接入 `glm-5.2`
- HITL 三铁律：**Checkpointer 必需** + **同一 `thread_id`** + **`version="v2"`**
- 中断结构：`result.interrupts[0].value["action_requests"]` / `["review_configs"]`；恢复 `Command(resume={"decisions":[...]})`
- 决策：`approve` / `edit`（`edited_action` 用 `args`）/ `reject`（带 `message`）/ `respond`

（待办：Step 0–5 跑完后补 `ch09-lab-summary.md` 与收官记录）
