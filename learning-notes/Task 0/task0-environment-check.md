# Task 0 · 环境自检报告

**日期**：2026-09-16  
**工作区**：`D:\agent_study`  
**课程**：Datawhale《Deep Agents 实战》  
**模型供应商**：商汤日日新（OpenAI 兼容接口）

---

## 1. 自检结论总表

| 检查项 | 要求 | 实测结果 | 状态 |
|--------|------|----------|------|
| Python | 3.11+ 可运行 DeepAgents | 系统 3.12.9；conda `deepagents` 3.12.14；项目 venv 3.12.9 | 通过 |
| 模型 API | 可调用 Tool Calling 模型 | `token.sensenova.cn/v1` + `glm-5.2`，对话与 Tavily 均成功 | 通过 |
| Git | 可用且可管理本地仓库 | git 2.54.0；`D:\agent_study` 已 `git init` | 通过 |
| LangSmith | 安装 SDK；追踪可选开启 | 包 `langsmith 0.12.4` 已装；`LANGSMITH_TRACING=false` | 通过（未开追踪） |
| AgentSeek | CLI + doctor | v0.1.4；doctor 全绿 | 通过 |
| 服务连通 | API + 前端 | `:2024/health` 200；`:5174` 200 | 通过 |

详细日志见：`docs/logs/task0-check-*.txt`、`docs/logs/model-probe.txt`。

---

## 2. Python 环境

| 层级 | 路径 | 版本 | 用途 |
|------|------|------|------|
| 系统 Python | `C:\Users\18942\AppData\Local\Programs\Python\Python312` | 3.12.9 | 日常/脚本 |
| Miniconda 环境 | `C:\Users\18942\miniconda3\envs\deepagents` | 3.12.14 | 课程脚本练习（`hello_world.py` 等） |
| 项目 venv | `D:\agent_study\research_deepagent\.venv` | 3.12.9 | AgentSeek research 应用 |

**关键包（项目 venv）**：

- `deepagents` 0.7.14  
- `langchain` 1.4.0  
- `langchain-openai` 1.6.2  
- `langgraph` 1.2.11  
- `agentseek-api` 0.2.3  

**验证命令**：

```powershell
D:\agent_study\research_deepagent\.venv\Scripts\python.exe --version
D:\agent_study\research_deepagent\.venv\Scripts\python.exe -c "import deepagents; print('ok')"
```

---

## 3. 模型 API（商汤日日新）

| 配置项 | 值 |
|--------|-----|
| Provider | `openai`（OpenAI 兼容） |
| Base URL | `https://token.sensenova.cn/v1` |
| 默认模型 | `glm-5.2` |
| Key 环境变量 | `OPENAI_API_KEY`（模板约定，勿改成 `SENSNOVA_*`） |

**已验证**：

1. `GET /v1/models` 列出 8 个支持 tools 的模型。  
2. `ChatOpenAI(base_url=...)` 中文对话成功。  
3. Tavily 搜索返回真实网页摘要。  

**手动切换模型（Key 不变）**：

```powershell
cd D:\agent_study
python switch_model.py --list
python switch_model.py --set kimi-k3
# 重启 agentseek dev 生效
```

可选模型：`glm-5.2`、`deepseek-v4-flash`、`deepseek-v4-pro`、`kimi-k3`、`sensenova-6.8-flash-lite`、`sensenova-6.7-flash-lite`、`sensenova-u1-fast`、`sensenova-u1.5-lite`。

---

## 4. Git

| 项 | 结果 |
|----|------|
| 版本 | `git version 2.54.0.windows.1` |
| 仓库 | `D:\agent_study` 已初始化 |
| 用户 | `agent-study` / `agent-study@local`（本地学习用） |

```powershell
cd D:\agent_study
git status -sb
```

> 注意：`.env` 已在 `.gitignore`，**不要提交 API Key**。

---

## 5. LangSmith

| 项 | 结果 |
|----|------|
| Python 包 | `langsmith 0.12.4`（依赖自动安装） |
| CLI | 未单独安装（pre02 实操 Trace 时再装） |
| 追踪 | `LANGSMITH_TRACING=false` |

开启方式（可选）：在 `research_deepagent\.env` 填写：

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<你的 key>
LANGSMITH_PROJECT=deepagents-course
```

---

## 6. AgentSeek 与服务

```text
agentseek doctor  → 全部 ok
agentseek dev     → API 2024 + 前端 5174
```

Windows 持久化：`SEEKDB_EMBED=false` + SQLite（`data/agentseek.db`），因嵌入式 SeekDB 仅 Linux。

启动：

```text
D:\agent_study\research_deepagent\start_research.bat
```

---

## 7. 提交清单（Task 0）

- [x] Python 3.12 环境可导入 `deepagents`
- [x] 日日新 API 连通并支持 Tool Calling
- [x] Git 可用且工作区已初始化
- [x] LangSmith SDK 已就绪（追踪未强制开启）
- [x] 过程文档：`docs/` 下术语、部署、日志、问题
