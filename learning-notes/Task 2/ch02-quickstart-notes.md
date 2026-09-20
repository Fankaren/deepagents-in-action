# Task 2 · ch02 快速上手笔记

**日期**：2026-09-20  
**对应章节**：[ch02 快速上手 — 5 分钟构建你的第一个 Deep Agent](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/)  
**本机状态**：已在 Task 0/pre 完成等价实践（日日新 + Deep Agents 0.7.14）

---

## 1. ch02 教学目标

1. 安装 `deepagents` + OpenAI 兼容客户端  
2. 配置模型 API Key  
3. 写 Hello World Agent（自定义工具 + `create_deep_agent` + `invoke`）  
4. 理解工具「三要素」：类型标注、docstring、默认值  
5. （进阶）研究 Agent + 搜索工具 + LangSmith  

课程默认供应商是硅基流动；**本机改为商汤日日新**，原理相同。

---

## 2. 与课程的配置映射

| 课程（SiliconFlow） | 本机（SenseNova） |
|--------------------|-------------------|
| `SILICONFLOW_API_KEY` | `OPENAI_API_KEY`（模板约定）/ 根目录 `SENSNOVA_API_KEY` |
| `https://api.siliconflow.cn/v1` | `https://token.sensenova.cn/v1` |
| `MODEL_NAME=Qwen/...` 或 `zai-org/GLM-5.2` | `glm-5.2` 等，见 `switch_model.py --list` |
| `ChatOpenAI(..., base_url=...)` | 相同 |

可用模型（均支持 tool calling）：`glm-5.2`、`deepseek-v4-flash/pro`、`kimi-k3`、`sensenova-6.8-flash-lite` 等。

---

## 3. 课程核心 API 形态

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,              # ChatOpenAI 实例或 provider:model
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
print(result["messages"][-1].content)
```

| 参数 | 说明 |
|------|------|
| `model` | 模型实例或字符串；本机用实例以便挂日日新 base_url |
| `tools` | Python 函数列表；Harness 额外注入文件/子 Agent 等 |
| `system_prompt` | v0.7 起更依赖应用自己写 |

**工具三要素**（课程强调）：

1. 参数 **类型标注**  
2. **docstring**（Agent 何时用它）  
3. **默认值**（减少必填参数）  

---

## 4. 本机已完成的对应实验

| 脚本 | 路径 | 对应课程 |
|------|------|----------|
| Hello World 天气工具 | `D:\agent_study\hello_world.py` | ch02 Hello World |
| 计算器 + 汇率 | `D:\agent_study\calculator_agent.py` | ch02「小试牛刀」 |
| 模型接入封装 | `D:\agent_study\model.py` | ChatOpenAI + 限流重试 |
| 切换模型 | `D:\agent_study\switch_model.py` | MODEL_NAME 可切换 |
| 完整研究应用 | `D:\agent_study\research_deepagent\` | ch02 进阶 + AgentSeek research |

运行：

```powershell
D:\agent_study\start_env.bat
python hello_world.py
python calculator_agent.py
python switch_model.py --list
```

研究应用 UI：`research_deepagent\start_research.bat` → http://127.0.0.1:5174  

---

## 5. Agent 在 invoke 背后做了什么（课程图示对应）

1. （可选）`write_todos` 规划 — 需 `TodoListMiddleware`  
2. 调用你的工具（如 `tavily_search` / `get_weather`）  
3. 虚拟 FS 落盘长结果  
4. （可选）`task` 委派子 Agent  
5. 综合成最终回复  

你在 LangSmith 里看到的 `model ↔ tools` 树就是这个循环的图化。

---

## 6. 易错点（本课 + 本机）

| 问题 | 处理 |
|------|------|
| 429 / rpm exhausted | 换模型或退避；见 `model.run_agent` |
| 改 `.env` 后 UI 无 Trace | **重启 agentseek-api** |
| 中文 bat 乱码 | 用 `start_env.bat` / GBK 中文 bat |
| reasoning 模型 content 空 | 提高 max_tokens；或换 glm-5.2 等 |
| 模板要求 `OPENAI_*` | 不要改成 `SENSNOVA_*` 传给 research 模板 |

---

## 7. 自测题

1. `create_deep_agent` 三个最小参数是什么？  
2. 工具三要素缺了 docstring 会怎样？  
3. 本机 `base_url` 是什么？为什么不用 `api.sensenova.cn`？  
4. v0.7 为何默认不带 `write_todos`？  
5. 研究应用改模型后为何必须重启？  
