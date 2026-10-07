# Task 5 · ch05 子 Agent 与上下文隔离（task 工具）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/>

## 怎么学

沿用四拍工作坊（先预测 → 运行 → 对照 → 改一处再跑）+ ch04 确立的「判定器体检」。
实验材料在主仓库 `D:\agent_study\labs\ch05\`（WORKSHOP.md + step1~5 脚本），本目录放日志与小结。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板（预测 vs 实际） |
| `progress-log.md` | 会话过程记录（每会话收尾追加） |
| `ch05-lab-summary.md` | **实测小结（提交主文档，已完成）** |
| `labs/ch05/step1_task_inventory.py` | task 工具与默认 general-purpose 盘点（零模型调用） |
| `labs/ch05/step2_first_delegation.py` | 首次委派：中间过程不可见 + 共享文件系统 |
| `labs/ch05/step3_isolation_ledger.py` | 隔离的账本：自己干 vs 委派（主上下文账 vs 全局账） |
| `labs/ch05/step4_custom_subagent.py` | description 路由 + 隔离中的 system_prompt 约束 |
| `labs/ch05/step5_coordinator.py` | 选做：协调者模式（ch04 规划 × ch05 委派） |

## 本机版本基线（实验结论以此为准）

- deepagents **0.7.14**：`task(description, subagent_type)`，返回子 agent 最终报告并**合并子 agent 的文件改动回主 state**（共享 FS 的代码级证据）
- 默认 general-purpose 子 agent：能力继承主 agent，上下文独立（工具描述原文 "stateless by default: sees only the prompt"）
- 自定义子 agent：`{name, description, system_prompt}` 三要素；tools 显式指定**完全替换**；middleware 不继承；`mode="fork"` 为实验特性
- ch04 的 TodoListMiddleware 不被字典声明的子 agent 继承（需自带）

（2026-10 收官：Step 1–5 + 3b 本地子账本全部完成，见 ch05-lab-summary.md）
