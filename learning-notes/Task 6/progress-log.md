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

## 会话 2 · Step 2 启而不等（P1 押错即题眼）

**做了什么**
- 用户跑 step2_first_async.py：P1 押「等任务做完」→ 实际 5.5s 返回（错——同步直觉带入）；P2 押区间（running或success）→ 实际 running（半对：预测要写死一个）；P3 ✓ success+报告

**学到了什么**
- **启而不等**：start_async_task 在子任务刚开始跑时就返回 task_id——启动与执行被拆开，task_id 是「欠条」不是「收货单」
- **task_id == thread_id**（channel 数据实证）；run_id 是另一个字段（指向具体某次执行）——Step 4 的伏笔：update 后 run_id 变、task_id 不变
- async_tasks channel 字段完备：agent_name/run_id/status/created_at/last_checked_at/last_updated_at，独立于消息历史
- **查完成任务比查运行中任务贵**：check 发现 success 后要多读子 thread 的 state 取报告（第 3 轮 19.9s vs 前两轮 4-5s）——异步模式新长出的成本项
- 状态机 running→success 有了时间戳证据（08:38:33 → 08:38:58）

**经验教训**
- 押区间（「running或success」）等于没押——预测的价值在写死后被证伪的可能
- 跨章迁移直觉要过一遍「机制变没变」检查：同步的等待习惯到异步就是 bug

---

## 会话 3 · Step 3 并行实验被真实世界打脏（限流 + 测量盲区）+ 仪器 v2

**做了什么**
- 跑 step3 v1：P1 同时启动 ✓（5.2s 一轮三个 task_id）；P2 用户押「错开」、脚本判「扎堆 0.0s」——两边都不可信；P3 全程 104.3s，单任务和三任务之和都对不上——实验被污染
- 交付 step3b v2：轮询改走 runs API（零模型调用），启动用 created_at（毫秒级），error 直接读子 thread 现场；离线单测 ts 解析 PASS

**学到了什么**
- **「扎堆 0.0s」是测量伪影**：第 2 轮阻塞 67.8s + 轮询 26.3s 造成 +5s~+99s 盲区，「首次观测到完成」≠ 完成时刻——事件时间 ≠ 观测时间
- **任务二 error：并行的第三本账（速率账）**——3 个 researcher + supervisor 同时打日日新，429 退避把回合拖到 67.8s，某个 researcher 重试耗尽失败；worker 槽位管服务端并发，管不住上游 API 的 RPM
- **异步的容错红利**：一个 error 不牵连另外两个 success，可单独重跑（同步模式做不到）
- in-mem 服务的 runs API 不给 started_at/ended_at（实测 null）——但 async_tasks 的 created_at 是毫秒级服务端时钟，够当启动证据；结束时刻只能 2s 粒度观测，如实标注

**经验教训**
- 脏数据比干净数据教得多：一次被限流污染的实验串起了速率账、测量伪影、容错红利三个课题
- 仪器的「判定器体检」：v1 把「首次观测到」当「事件时间」——先问测的是什么时间
- 遇到 error 别只看 status 字段：现场在子 thread 的最后消息里（也可能要 LangSmith）

---

## 待办 / 下一步

- [x] 材料搭建 + 服务排障 + 服务上线（:8123，双 graph 注册）
- [ ] Step 1：五工具盘点（脚本已验证，待用户跑）
- [x] Step 2：启而不等（5.5s 返回 vs 任务 10s+；task_id==thread_id 实证）
- [x] Step 3 v1：被限流污染（任务二 error、0.0s 离散度是伪影）→ Step 3b v2 待重跑
- [ ] Step 4（选做）：update 中途转向 + cancel
- [ ] 收尾：`ch06-lab-summary.md` + 推送
