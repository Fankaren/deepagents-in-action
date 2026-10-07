# Task 6 · ch06 异步子 Agent（AsyncSubAgent / 五工具）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/>

## 怎么学

沿用四拍工作坊 + 判定器体检 + 仪器单测。**本章特殊性：先起服务**（`labs/ch06/start_server.bat`，端口 8123，`--n-jobs-per-worker 4`），实验脚本是客户端（langgraph-sdk 走 HTTP）。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板 |
| `progress-log.md` | 会话过程记录（每会话收尾追加） |
| `ch06-lab-summary.md` | 实测小结（提交主文档，做完再写） |
| `labs/ch06/langgraph.json` | 服务配置（supervisor + researcher 两 graph，env 指向根 .env） |
| `labs/ch06/graphs/supervisor.py` | 主 Agent（AsyncSubAgentMiddleware 五工具 + 铁律 system_prompt） |
| `labs/ch06/graphs/researcher.py` | 调研员（slow_research 睡 8 秒模拟长任务） |
| `labs/ch06/start_server.bat` | 起 Agent Server（:8123） |
| `labs/ch06/step1_inventory.py` | 五工具盘点（零模型调用、零服务依赖） |
| `labs/ch06/step2_first_async.py` | 启而不等：快速返回 task_id → running → success |
| `labs/ch06/step3_parallel.py` | 真并行：三任务同时 running + 完成时刻扎堆/错开判据 |
| `labs/ch06/step4_steering.py` | 选做：update 中途转向 + cancel 取消 |

## 本机版本基线

- deepagents **0.7.14**（AsyncSubAgent/AsyncSubAgentMiddleware）/ langgraph 1.2.11 / langgraph-cli[inmem] **0.4.32**（本次新装）/ langgraph-sdk 0.4.4
- 服务：`langgraph dev --port 8123 --n-jobs-per-worker 4`；graph_id：`supervisor`、`researcher`；ASGI 进程内传输（url 不填）
- 任务元数据在 `async_tasks` state channel（独立于消息历史——与 ch04 todos 同一设计哲学）
