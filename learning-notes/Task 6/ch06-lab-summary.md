# Task 6 · ch06 异步子 Agent —— 实验小结

**对应课程**：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/>
**环境基线**：deepagents 0.7.14 / langgraph 1.2.11 / langgraph-cli[inmem] 0.4.32（本章新装）/ langgraph-sdk 0.4.4 / 日日新 `glm-5.2`
**实验方法**：四拍工作坊 + 判定器体检 + 仪器单测 + **服务端日志取证**（本章新增）
**材料**：`D:\agent_study\labs\ch06\`（langgraph.json + graphs/supervisor|researcher + start_server.bat + step1~4 + step3b + check_task.py）；过程日志 `progress-log.md`（7 会话）
**服务**：Agent Server :8123（避开 research 应用的 2024），`--n-jobs-per-worker 4`，ASGI 进程内传输

---

## 一、实验总览与实测结果

| Step | 问题 | 预测 vs 实测 | 关键证据 |
|------|------|--------------|----------|
| 1 | 异步注入几个工具 | 5 个 ✓ | start/check/update/cancel/list——对照同步只有 1 个 task；描述含 "immediately" 纪律 |
| 2 | 启而不等 | P1 错即题眼 | 启动轮 5.5s ≪ 任务 10s+；task_id==thread_id（channel 实证）、run_id 独立；查完成任务 19.9s 比查运行中贵 |
| 3 v1 | 真并行？ | **被真实世界打脏** | 任务二 error（429）；「扎堆 0.0s」是测量伪影（supervisor 阻塞 67.8s 盲区）；全程 104.3s 对不上任何基准 |
| 3b v2/v3 | 干净测量 | P1 铁证 ✓、P2 悬案、P3 仪器 bug | created_at 离散度 0.00s（两次复现）；时钟混用 -17.9 亿秒 → 统一 epoch + 离线单测 |
| 日志取证 | P2 悬案裁决 | **真并行 + 限流拖慢** | worker 日志：三个 run `run_started_at` 同微秒、`active=3`、429 风暴逐行可见、exec 12.8/26.7/41.9s 膨胀 |
| 4 | 转向与刹车 | P1a ✓ P1b ✓ P2 半中 | update=整任务重启（task_id 不变、run_id 换、报告带「修订版：」）；cancel 落点 **interrupted**；runs 族谱：旧 interrupted/新 success 并列 |

---

## 二、知识主线（实测支撑）

### 1. 同步 → 异步：拆开「等待」

- **委派默认开（同步 1 工具）→ 异步化后 5 工具**：启动/查询/转向/取消/列表——生命周期每个阶段一个工具，工具数量 = 自由度；「等待的权利」从工具手里还给主 agent
- `start_async_task` **立即返回 task_id**（欠条，不是收货单）：task_id == thread_id；run_id 指向具体某次执行（update 后 run_id 换、task_id 不变——Step 2 伏笔 Step 4 兑现）
- 状态词表（物证版）：`running / success / error / interrupted`——cancel 的落点是 interrupted，与课程文字有出入，以物证为准
- 任务元数据存独立 `async_tasks` state channel（agent_name/run_id/status/时间戳俱全）——「会被截断的放消息历史，必须长存的进 state channel」（ch04 todos 同族哲学）

### 2. 真并行与三本账

- **并行启动铁证**：created_at 离散度 0.00s（毫秒级服务端时钟，两次复现）
- **并行执行铁证**：worker 日志三个 run `run_started_at` 同微秒；`Worker stats: active=3 available=1 max=4`
- **错开完成的原因 = 限流而非排队**：429 风暴 + 指数退避让 exec 从 12.8s 膨胀到 41.9s；排队的表现是「exec 短、开始晚」，限流是「开始同刻、exec 膨胀」——两者可分
- **速率账 = 第三本账**（token 账、墙钟账之外）：worker 槽位管服务端并发，管不住上游 API 的 RPM；速率受限时，并行保证「同时开始」，保证不了「同时结束」
- 容错红利：一个任务 error 不牵连其余 success，可单独重跑（同步模式做不到）
- 查完成任务比查运行中贵（要多读子 thread 的 state 取报告）

### 3. 转向与刹车（异步独有的方向盘）

- **update = 整任务重启**：旧 run 作废（打断了 `interrupts the current run`）、thread 对话历史经 checkpoint 续上、没跑完的工具从头来——**转向响应时间 = update 落地时刻 + 完整任务时长**，不是剩余时长（实测差 2 秒错过）
- **cancel 异步生效**：落点 interrupted，二次 check 确认稳定
- **runs 列表 = run 族谱**：同 thread 上旧 run（interrupted）与新 run（success）并列——update 与 cancel 共用 interrupt 策略的物证

### 4. 架构与部署

- Agent Protocol（API 规范）/ Agent Server（`langgraph dev` 起 in-mem 服务）/ thread=服务端会话 / run=一次执行
- ASGI（同部署，url 不填，必须 `ainvoke`）vs HTTP（填 url，远程部署）——单部署拓扑起手
- `langgraph.json` 双 graph 注册（graph_id 大小写严格一致）；worker 槽位 ≥ 主+子数量，不够排队

---

## 三、方法论遗产（本章主贡献）

1. **验货工具化（用户点名，第一条）**：悬案 = 事实 × 查询成本；**第一次手工做是探索，第二次手工做是欠账**——凡第二次需要的手工验证当场固化成常驻脚本（`check_task.py`）；验证便宜 → 悬案不存活；反向清单：临时拼命令、关键字流程控制、猜等待预算
2. **服务端日志 = 零成本第一现场**：裁决优先翻 worker 日志（started_at/exec_ms/429 记录全在里面），比云端 trace 更近；**每本账只回答它那一层的问题**——created_at 管启动、worker log 管调度、exec_ms 管执行、API status 管结果，裁决权在离现场最近的账本手里
3. **事件时间 ≠ 观测时间**：首次观测到完成 ≠ 完成时刻；supervisor 回合阻塞造成的盲区能把真并行抹成「0.0s 扎堆」伪影
4. **时钟纪律**：每笔减法两边必须同一本时钟（perf_counter 单调钟 ≠ epoch 墙钟，混用算出 -17.9 亿秒）；单测要覆盖数值合理性，且单测场景要来自真实故障模式
5. **速率账意识**：并行的隐藏成本不是 token 是速率；限流让真并行呈现错开完成，光看墙钟会误判为串行
6. **流程判定用结构化字段**（status），不用文本子串（「不会再继续运行」误触发关键字匹配）
7. 错误栈第一层不是根因（dictConfig ValueError → 剥两层才是缺 colorama）；新环境起服务先验平台相关隐式依赖

---

## 四、环境变更记录

- 新装：`langgraph-cli[inmem]` 0.4.32、`colorama`（Windows + structlog 彩色渲染的隐式依赖）
- 新增常驻服务拓扑：labs/ch06 双 graph（supervisor/researcher）@ :8123
- 新增常驻工具：`labs/ch06/check_task.py`（查任意 task 的 run 状态 + 最终报告）

---

## 五、与课程原文对应

| 工作坊 | 课程 ch06 知识点 |
|--------|------------------|
| Step 1 | 五工具与 AsyncSubAgentMiddleware |
| Step 2 | start 异步返回、thread/run/task_id 模型、async_tasks channel |
| Step 3 + 3b + 日志取证 | 并行委派、worker 池（扩展：速率账、测量伪影、日志取证） |
| Step 4 | update（interrupt 策略、task_id 不变）与 cancel（异步生效） |
| 全章 | 同步/异步六维对比、5 秒法则、Agent Protocol 架构分层 |

自测题见 `labs/ch06/WORKSHOP.md` 文末；逐会话过程记录见 `progress-log.md`。
