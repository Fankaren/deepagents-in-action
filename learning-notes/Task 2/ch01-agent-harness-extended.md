# Task 2 · ch01 Agent Harness 笔记（含扩展对比）

**日期**：2026-09-20  
**对应章节**：[ch01 从 Agent Framework 到 Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/)  
**扩展**：在课程对比 Deep Agents / Claude Agent SDK / Codex SDK 之外，补充 **DeepSeek Harness（DSH）** 与 **DeerFlow 2**

---

## 1. ch01 核心结论（课程原文）

### 1.1 三层架构

| 层次 | 代表 | 解决什么 |
|------|------|----------|
| Runtime 运行时 | LangGraph | 可靠执行：checkpoint、stream、HITL、状态 |
| Framework 框架 | LangChain | 模型抽象、工具、Agent 循环、Middleware |
| Harness 工具层 | Deep Agents | 开箱：虚拟 FS、规划、子 Agent、长期记忆 |

三者 **层层构建，不是互斥替代**。

### 1.2 为什么要 Harness

成功 Agent 产品（Claude Code、Manus、Cursor 等）共性：

1. 文件系统读写/搜索  
2. 任务拆解与追踪  
3. 子任务委派  
4. 上下文管理（防「失忆」）

Harness = 把这些 **被验证的模式固化成可复用套件**。

### 1.3 Context Engineering

- **问题**：Prompt Stuffing → 溢出、注意力稀释、不可扩展  
- **做法**：虚拟文件系统 + 按需 `read_file` / `write_file` / `grep`，后端可插拔（内存/磁盘/DB/沙箱）

### 1.4 v0.7 提醒

- 文件工具含 `delete`  
- `write_todos` 需显式 `TodoListMiddleware`  
- 默认基础 system prompt 可为空，业务提示词自己写  

---

## 2. 扩展对比：五类 Harness / Agent 系统

> 课程只写了 Deep Agents、Claude Agent SDK、Codex SDK。下表补充社区/国内常见的 **DeepSeek Harness** 与 **DeerFlow 2**，并把 **Claude Code 产品**与 **Claude Agent SDK** 分开写，避免混称。

### 2.1 一览表

| 维度 | Deep Agents | Claude Code / Claude Agent SDK | Codex / Codex SDK | DeepSeek Harness (DSH) | DeerFlow 2 |
|------|-------------|--------------------------------|-------------------|------------------------|------------|
| **定位** | 通用可嵌入 Harness（SDK） | 终端编程 Agent + 可嵌入 SDK | OpenAI 编程 Agent + SDK | 通用 Agent Harness + 插件运行时 | 长任务 SuperAgent Harness（产品级系统） |
| **出品方** | LangChain | Anthropic | OpenAI | DeepSeek（基于 Cordis） | 字节跳动 ByteDance |
| **形态** | Python/TS 库 `create_deep_agent` | CLI + SDK | CLI + SDK + 云端 | CLI/Web/桌面 + 插件树 | Gateway + 前端 + 沙箱等整套服务 |
| **模型** | **模型无关**（含日日新等 OpenAI 兼容） | 偏 Claude | 偏 OpenAI/DeepSeek 系 | 以 DeepSeek 生态为中心，可配 Provider | 多 Provider（推荐豆包 Seed-Code / DeepSeek / Kimi 等） |
| **核心理念** | Context Engineering + 可插拔后端 | 编码工作流 + Hooks | OS 级沙箱策略 | **Everything is a Plugin** | 长时程：subagent + memory + sandbox + skills |
| **开源** | MIT | SDK MIT（产品闭源倾向） | Apache-2.0 | 开源仓库 + npm SDK/CLI | MIT（2.0 与 1.x 代码不共用） |
| **与 LangChain 栈** | 直接建在 LangGraph/LangChain 上 | 否 | 否 | 否（Cordis 插件运行时） | 重度使用 LangChain/LangGraph 生态 |
| **学习曲线** | 中（课程+API） | 低（当工具用）/中（SDK） | 中 | 中高（插件/Profile 概念多） | 高（整套部署与配置） |
| **适合本课** | **主路径** | 对照阅读 | 对照阅读 | 扩展视野 | 扩展视野/长任务参考 |

### 2.2 DeepSeek Harness（DSH）要点

- **一句话**：DeepSeek 开源的 Agent Harness，口号近似 **Agent = Model + Harness**，架构基于 **Cordis**，强调 **一切皆插件**（模型适配、工具、会话、UI、甚至 Agent Loop 都可插件化）。  
- **入口**：`npx @deepseek-ai/dsh web`；Python SDK：`deepseek-harness-sdk`。  
- **生态**：大量 `dsh-plugin`（Agent Teams、深度研究、上下文审计、沙箱、桌面壳等）。  
- **与 Deep Agents 差异**：  
  - Deep Agents：**库**，嵌进你自己的 LangGraph 应用  
  - DSH：**可运行的产品 + 可扩展 Runtime**，更像「可改装的 Claude Code」  
- **注意**：官方明示开发者预览，沙箱/权限 **不构成完整安全隔离**；插件安装脚本可能在沙箱外执行。  
- **参考**：[deepseek.com/harness](https://deepseek.com/harness/) · [awesome-deepseek-harness](https://github.com/libukai/awesome-deepseek-harness)

### 2.3 DeerFlow 2（Deer-flow）要点

- **一句话**：字节开源的 **long-horizon SuperAgent harness**（Deep Exploration and Efficient Research Flow），用 **sub-agents + memory + sandboxes + skills + message gateway** 跑「分钟到小时」级研究/编码/创作任务。  
- **v2 说明**：相对 v1（Deep Research 框架）是 **重写**，定位升到 Super Agent Harness；v1 在 `1.x` 分支维护。  
- **技术栈**：Python 3.12 + Node 22，前端 + Gateway，内部使用 LangGraph checkpoint/store，可接 LangSmith。  
- **与 Deep Agents 差异**：  
  - Deep Agents：你写 `create_deep_agent(...)` 组装能力  
  - DeerFlow 2：直接部署 **完整 Agent 产品**（会话、沙箱、技能、IM 渠道、定时任务等）  
- **资源门槛**：官方给出本地评估约 4C/8G 起，长跑服务更高；Windows 更适合评估，生产偏 Linux+Docker。  
- **参考**：[bytedance/deer-flow](https://github.com/bytedance/deer-flow) · [deerflow.tech](https://deerflow.tech)

### 2.4 如何选择（结合本课）

| 你的目标 | 建议 |
|----------|------|
| 跟 Datawhale 课、接日日新 API、写可复现实验 | **Deep Agents**（当前主线） |
| 日常终端改代码、要成熟 UX | Claude Code / Codex 类产品 |
| 研究「Harness 可插件化、自进化 Runtime」 | 读 DSH 架构与插件生态 |
| 需要整站长任务研究系统（报告、多 Agent 编排） | 参考 DeerFlow 2 架构，不必整站搬进课程作业 |
| 企业要模型无关 + LangSmith 可观测 | Deep Agents + LangSmith（我们已配） |

### 2.5 结构关系（心智模型）

```text
                    ┌─────────────────────────────┐
  产品/系统层        │ Claude Code · Codex · DSH UI │
                    │ DeerFlow 2 整站 · Manus…     │
                    └──────────────┬──────────────┘
                                   │ 可能基于 / 或平行于
  Harness 层        Deep Agents SDK · Claude Agent SDK · DSH Runtime · DeerFlow Harness
                                   │
  Framework 层      LangChain · 其他 Agent 框架
                                   │
  Runtime 层        LangGraph · Temporal · …
```

**要点**：Deep Agents 是 **可嵌入的 Harness 库**；DSH/DeerFlow/Claude Code 更接近 **可运行的 Harness 产品**。课程教你的是前者。

---

## 3. 与本机实验的对应

| ch01 概念 | 我们环境里的对应 |
|-----------|------------------|
| Harness 能力 | `research_deepagent`：文件工具 + 子 Agent + Tavily |
| Context Engineering | Agent 虚拟 FS；长结果不全塞 prompt |
| 模型无关 | `ChatOpenAI(base_url=token.sensenova.cn)` + `switch_model.py` |
| Runtime 可观测 | LangSmith Trace（:2024 跑图，网页看树） |
| v0.7 默认更轻 | 复杂任务才加 `TodoListMiddleware` |

---

## 4. 自测题

1. Runtime / Framework / Harness 各解决什么问题？Deep Agents 在哪一层？  
2. Context Engineering 和「把文件全塞进 prompt」有何区别？  
3. Deep Agents 相对 Claude/Codex SDK 的两个结构性优势？  
4. DSH 与 DeerFlow 2 分别更像「库」还是「产品」？和 Deep Agents 如何定位区分？  
5. 为什么课程作业用 Deep Agents + 自选模型，而不是绑定 Claude Code？  
