# 专业名词解析（Task 0 / 准备篇）

按课程出现顺序整理，便于提交与复习。

## Agent Harness（智能体运行时脚手架）

比 Framework 更「开箱」的层：在 Agent 循环之上默认提供规划、文件系统、子 Agent、上下文管理等能力。Deep Agents 是典型 Harness。

## Deep Agents

LangChain 开源的 Agent Harness（Python 包 `deepagents`）。特点：虚拟文件系统、子 Agent 委派、上下文总结、Skills、可插拔模型。

## LangChain / LangGraph

- **LangChain**：LLM 应用框架（模型、工具、Agent 组装）。  
- **LangGraph**：把 Agent 做成可持久化的状态图运行时（checkpoint、streaming）。

## create_deep_agent()

Deep Agents 核心工厂函数。常用参数：`model`、`tools`、`system_prompt`、`middleware`、`subagents`。

## Tool Calling

模型输出结构化「函数调用」而非纯文本。Deep Agents **要求**模型支持 Tool Calling。

## OpenAI 兼容接口

`/v1/chat/completions` 事实标准。商汤日日新用 `ChatOpenAI(base_url="https://token.sensenova.cn/v1")` 接入。

## AgentSeek

模板 + 生命周期 CLI：`create` / `info` / `task` / `doctor` / `dev`。本项目使用模板 `deepagents/research`。

## lifecycle.toml

`.agentseek/lifecycle.toml`：声明工具依赖、环境变量、任务、前后端进程，供 `doctor`/`dev` 读取。

## Tavily

研究 Agent 的网页搜索 API。工具函数 `tavily_search` 需要 `TAVILY_API_KEY`。

## LangSmith

LangChain 可观测性平台：Trace 每一次模型/工具调用。通过环境变量开启，无需改代码。

## SeekDB / OceanBase

AgentSeek API 的存储后端。**嵌入式** SeekDB（`pylibseekdb`）目前 **仅 Linux**；Windows 改用 SQLite。

## WSL1 vs WSL2

- WSL1：翻译层，无完整 Linux 内核虚拟化。  
- WSL2：轻量 VM，可跑 Docker、嵌入式 SeekDB 等。  
- 本机当前为 WSL1，且 BIOS 未开 CPU 虚拟化。

## TodoListMiddleware

v0.7 起任务规划 **默认关闭**。需要 `write_todos` 时显式加入该 Middleware。

## Sub-agent（子 Agent）

主 Agent 通过 `task` 把子任务委派给隔离上下文的子研究者，避免主上下文爆炸。

## Virtual Filesystem

Harness 内置 `read_file` / `write_file` 等，用于把长结果落盘，做 Context Engineering。

## reasoning_content

部分推理模型在 `content` 外额外返回思考字段；`glm-5.2` / `deepseek-v4-*` / `kimi-k3` 均可能出现。

## 429 / RPM 限流

日日新按请求次数（RPM）限流。学习时用 `switch_model.py` 换模型或退避重试。
