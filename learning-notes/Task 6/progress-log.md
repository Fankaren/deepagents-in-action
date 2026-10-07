# Task 6 · 学习过程记录（ch06 异步子 Agent）

> 惯例：每次会话收尾追加一节，三段式——做了什么 / 学到了什么 / 经验教训。
> 对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/>

---

## 会话 1 · 材料搭建 + 服务排障（colorama）

**做了什么**
- 抓取课程 ch06 原文，核实本机 `async_subagents.py`（931 行）：AsyncSubAgent 字段（name/description/graph_id/url/headers）、五个异步工具 schema、ASGI（url 不填，必须 ainvoke）与 HTTP（填 url）两种传输
- 安装缺失依赖 `langgraph-cli[inmem]` 0.4.32（langgraph-sdk 0.4.4 已有）
- 搭建 `labs/ch06` 服务端：langgraph.json（supervisor + researcher 双 graph，端口 8123 避开 research 应用的 2024，env 指根 .env）+ start_server.bat + 4 个实验脚本 + WORKSHOP
- **服务启动失败两次排障**：表层报错 `ValueError: Unable to configure formatter 'simple'`（uvicorn dictConfig 包装），逐层追到真实根因——**Windows 上缺 colorama**，structlog 的 `ConsoleRenderer(colors=True)` 在模块导入时直接 SystemError；装 colorama 后 dictConfig 全链路实测 OK
- 服务验证：`/ok` 健康，`/assistants/search` 确认 supervisor 与 researcher 均注册
- step1 盘点脚本验证通过（零模型调用、零服务依赖）：五工具齐全，start_async_task 描述含 "immediately" 纪律关键词

**学到了什么**
- 异步委派注入 **5 个工具**（对照同步只有 1 个 task）：start/check/update/cancel/list——「等待的权利」从工具手里还给主 agent：启而不等，问而再查
- ch06 的架构前提：主/子 agent 都是**服务端 graph**（Agent Protocol），thread=服务端会话、run=一次执行、task_id 就是子任务 thread_id；ASGI 进程内传输必须异步入口
- **排障方法论实战**：报错栈的第一层（dictConfig 的 ValueError）不是根因，剥开两层才见真凶（colorama）——「错误信息会说谎，import 一下组件才知道它到底能不能活」
- 任务元数据在独立的 `async_tasks` state channel——与 ch04 todos 同一设计哲学：「会被截断的放消息历史，必须长存的进 state channel」

**经验教训**
- 新环境跑服务前先验证「隐式依赖」（colorama 这类平台相关包）——pip 依赖树不保证装全
- 端口规划要提前（8123 避开 research 的 2024）；worker 槽位 ≥ 主+子数量是本章第一坑

---

## 待办 / 下一步

- [x] 材料搭建 + 服务排障 + 服务上线（:8123，双 graph 注册）
- [ ] Step 1：五工具盘点（脚本已验证，待用户跑）
- [ ] Step 2：启而不等（快速返回 task_id → running → success）
- [ ] Step 3：真并行（三任务 + 完成时刻扎堆/错开判据）
- [ ] Step 4（选做）：update 中途转向 + cancel
- [ ] 收尾：`ch06-lab-summary.md` + 推送
