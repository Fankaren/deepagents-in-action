# Task 4 · ch04 任务规划与分解（TodoListMiddleware / write_todos）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/>

## 怎么学

沿用 ch03 的四拍工作坊：**先预测 → 运行 → 对照观察清单 → 改一处再跑**。
实验材料在主仓库 `D:\agent_study\labs\ch04\`（WORKSHOP.md + step1~5 脚本），本目录放日志与小结。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板（预测 vs 实际） |
| `ch04-lab-summary.md` | 跑完后的实测小结（提交主文档，做完再写） |
| `labs/ch04/WORKSHOP.md` | 一步步怎么做（主仓库） |
| `labs/ch04/step1_planning_off.py` | 默认不带 write_todos（对照 ch03 Step1） |
| `labs/ch04/step2_enable_planning.py` | 打开 TodoListMiddleware，首次看见状态流转 |
| `labs/ch04/step3_todo_lifecycle.py` | 4 步任务的生命周期与计划修订 |
| `labs/ch04/step4_with_vs_without.py` | 有规划 vs 无规划对照实验 |
| `labs/ch04/step5_todos_vs_summarization.py` | 选做：摘要压缩后 todos 幸存 |

## 本机版本基线（实验结论以此为准）

- deepagents **0.7.14** / langchain **1.4.0** / langgraph 1.2.11
- `TodoListMiddleware` 来自 `langchain.agents.middleware`（deepagents 包不再自带）
- `Todo` = `{content: str, status: "pending"|"in_progress"|"completed"}`；状态存 State 的 `todos` 字段；文件存 `files` 字段
