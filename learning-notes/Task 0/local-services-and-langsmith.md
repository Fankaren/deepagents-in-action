# 本地服务与 LangSmith 说明

**日期**：2026-09-16  
**场景**：`agentseek dev` / `start_research.bat` 启动后的本机拓扑

---

## 1. 当前本地开启了哪些服务

| 服务 | 监听 | 是什么 | 怎么起 / 停 |
|------|------|--------|-------------|
| **AgentSeek API**（LangGraph 后端） | `127.0.0.1:2024` | 执行 DeepAgents 研究图；提供 `/health`、`/docs` | `start_research.bat` 或 `agentseek dev` |
| **Vite React 前端** | `127.0.0.1:5174` | 浏览器提交问题、看流式输出与工具卡片 | 同上（`frontend/` 下 `npm run dev`） |

健康检查：

```powershell
Invoke-WebRequest http://127.0.0.1:2024/health
Invoke-WebRequest http://127.0.0.1:5174
```

两者 **不是** LangSmith；只是本机一对前后端进程。

```text
浏览器 :5174
   │ HTTP
   ▼
:2024 AgentSeek API  ──► 日日新 (token.sensenova.cn)
        │                 Tavily 搜索
        │  LANGSMITH_TRACING=true 时旁路上传
        ▼
   LangSmith 云端 api.smith.langchain.com
```

---

## 2. 这些服务和 LangSmith 的关系

| 层级 | 本地 | LangSmith（云） |
|------|------|-----------------|
| 职责 | 真正跑模型、调工具 | **事后/旁路观测**：记录每次调用 |
| 配置 | `research_deepagent\.env`：`LANGSMITH_TRACING` / `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` | 项目 `deepagents-course` 下的 Runs |
| 依赖 | 无 Smith 也能跑 Agent | 只是上传失败时多报错日志 |

要点：

1. LangSmith **不是** 本地要「启动」的服务，而是 SaaS。  
2. 开启追踪 **只改环境变量**，不用改业务代码。  
3. Key 无效（如曾 403）时：Agent 仍工作，只是云上看不到 Trace。  
4. Trace 根节点本项目里常叫 **`LangGraph`**（不一定叫 `research`）。

---

## 3. 只能从 CLI 看吗？能不能网页看？

**两者都可以；日常以网页为主。**

### 网页（推荐）

1. 打开 https://smith.langchain.com  
2. 用与 API Key 相同的账号登录  
3. 项目列表选 **`deepagents-course`**  
4. 点开某条 Trace，可展开：  
   - 根 `LangGraph`  
   - 各次 `ChatOpenAI`（耗时、token、输入输出）  
   - `tavily_search`（query、结果）  
   - Middleware 包装层  

适合：看树、点开 Prompt、复制 Trace 链接。

### CLI

```powershell
langsmith project list
langsmith trace list --project deepagents-course --limit 5 --include-metadata
langsmith trace get <trace-id> --project deepagents-course --include-metadata
langsmith run list --trace-ids <trace-id> --project deepagents-course --run-type llm
langsmith run get <run-id> --project deepagents-course --include-io
```

适合：批量列表、脚本对比、无浏览器环境。

---

## 4. 你想做什么 → 用哪里

| 目标 | 入口 |
|------|------|
| 跑研究、看最终报告 | http://127.0.0.1:5174 |
| API 文档 | http://127.0.0.1:2024/docs |
| 看某次研究的模型/工具调用树 | https://smith.langchain.com → `deepagents-course` |
| 命令行列最近 Trace | `langsmith trace list --project deepagents-course` |

页面里再提一个问题后刷新 Smith 网页，应能看到新的一条 Trace。

---

## 5. 相关文档

- [pre02-trace-analysis.md](./pre02-trace-analysis.md) — 一次真实 Trace 的瓶颈分析  
- [pre02-status.md](./pre02-status.md) — Key 403 排查与完成状态  
- [glossary.md](./glossary.md) — LangSmith / AgentSeek 等名词  
