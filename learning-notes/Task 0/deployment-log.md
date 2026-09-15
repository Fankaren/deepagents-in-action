# 部署过程记录

时间线：2026-09-14 ~ 2026-09-16  
工作区：`D:\agent_study`

---

## 阶段 A：基础环境（conda + 脚本练习）

1. 确认 Miniconda：`C:\Users\18942\miniconda3`  
2. 创建环境：`conda create -n deepagents python=3.12`  
3. 安装：`deepagents langchain-openai python-dotenv`  
4. 编写：
   - `model.py`：ChatOpenAI → 日日新  
   - `hello_world.py`：天气工具 Agent  
   - `calculator_agent.py`：计算 + 汇率  
   - `list_models.py`：列出可用模型  
5. `.env` 写入 `SENSNOVA_API_KEY` / `SENSNOVA_BASE_URL` / `MODEL_NAME`  

**结果**：`hello_world` 与 `calculator` 均跑通（`glm-5.2`）。

---

## 阶段 B：AgentSeek 研究应用

1. `uv tool install --upgrade agentseek` → v0.1.4  
2. PATH 加入 `C:\Users\18942\.local\bin`  
3. GitHub 直连失败 → 经 `codeload.github.com` 下载 `agentseek-templates` zip  
4. 本地模板创建：

```powershell
agentseek create D:\agent_study\vendor\agentseek-templates-main\templates\deepagents\research --no-input
```

5. 配置 `research_deepagent\.env`：
   - `OPENAI_API_BASE=https://token.sensenova.cn/v1`
   - `AGENTSEEK_MODEL=glm-5.2`
   - `TAVILY_API_KEY=tvly-...`
6. `agentseek task sync` / `agentseek task frontend`  
7. 首次 `agentseek-api` 启动失败：SeekDB 嵌入库仅 Linux  
8. 改为 `SEEKDB_EMBED=false` + `METADATA_DB_BACKEND=sqlite`  
9. `agentseek doctor` 全绿；`/health` 与 `:5174` 均为 200  

---

## 阶段 C：可切换模型 + pre02

1. `D:\agent_study\switch_model.py`：读写 `AGENTSEEK_MODEL`，调用 `/v1/models`  
2. `npx skills add ob-labs/agentseek --skill langchain-dev-guide --skill langsmith-trace`  
   → 安装到 `research_deepagent\.agents\skills\`  

---

## 阶段 D：Task 0 文档与 Git

1. `git init D:\agent_study`  
2. 输出 `docs/task0-environment-check.md` 与 `docs/logs/`  

---

## 关键路径速查

| 内容 | 路径 |
|------|------|
| 学习环境启动 | `D:\agent_study\start_env.bat` |
| 研究应用启动 | `D:\agent_study\research_deepagent\start_research.bat` |
| 切模型 | `python D:\agent_study\switch_model.py --set <model>` |
| 研究项目 env | `D:\agent_study\research_deepagent\.env` |
| 任务文档 | `D:\agent_study\docs\` |
