# Task 2 · ch01 / ch02 简答题参考答案

**用途**：课程作业/复习参考。表述以 Datawhale ch01/ch02 + 本机扩展笔记为准，可按自己的话压缩。  
**说明**：标「扩展」的题来自我们的对比补充，不是课程原文必考题。

---

# ch01 从 Agent Framework 到 Agent Harness

## 题 1：简述 Agent 开发的三个层次及各自解决的问题。

**参考答案：**

1. **Runtime（运行时层，如 LangGraph）**  
   解决「Agent 如何可靠地跑」：持久化执行/断点恢复、流式输出、人机协作（HITL）、状态与 checkpoint 管理。可类比 Agent 世界的「操作系统」。

2. **Framework（框架层，如 LangChain）**  
   建在 Runtime 之上，解决「如何标准化开发」：模型抽象、工具接口、Agent 循环、Middleware。开发者通常不必直接碰图 API。

3. **Harness（工具层，如 Deep Agents）**  
   解决「复杂 Agent 如何开箱即用」：预置虚拟文件系统、任务规划（可选 Todo）、子 Agent 委派、长期记忆等被产品验证过的能力。

三者是 **自底向上层层构建**，不是互相替代：要最大灵活度用 Runtime，要快速标准化用 Framework，要复杂多步任务用 Harness。

---

## 题 2：为什么在 Runtime 和 Framework 已经存在的前提下，还需要 Agent Harness？

**参考答案：**

观察市面上真正能完成复杂任务的产品（Claude Code、Manus、Cursor 等），核心能力高度趋同：

- 文件系统读写与搜索  
- 把大任务拆成可追踪步骤  
- 子任务委派给子 Agent  
- 长对话的上下文管理  

若每次用 LangChain 从零实现，会重复造轮子。Harness 的价值是：**把这些已被验证的模式固化成可复用、可扩展的套件**，让应用开发者站在「装好的工具间」里，而不是每次自己找锤子和锯子。

---

## 题 3：什么是 Context Engineering？它与传统的 Prompt Stuffing 有何区别？

**参考答案：**

**Context Engineering（上下文工程）** 指：不把全部信息塞进 prompt，而是为模型构建一套 **高效获取与管理信息的基础设施**（典型如虚拟文件系统）。

| | 传统 Prompt Stuffing | Context Engineering（Deep Agents） |
|--|----------------------|-------------------------------------|
| 信息组织 | 尽量多塞进上下文 | 按需读取，中间结果可落盘 |
| 窗口 | 易溢出 | 上下文只保留当前步骤需要的内容 |
| 注意力 | 信息越多越稀释 | 关键信息占比更高 |
| 扩展性 | 难以处理任意规模项目 | 文件/搜索/分页读取可水平扩展 |

Deep Agents 的做法示例：需要时才 `read_file`/`grep`，长结果用 `write_file` 写入虚拟 FS；该 FS 后端可插拔（内存、磁盘、数据库、远程沙箱等）。

---

## 题 4：Deep Agents 预置了哪些 Harness 能力？（注意 v0.7 变化）

**参考答案：**

课程能力表概括为：

1. **虚拟文件系统**：`read_file`、`write_file`、`edit_file`、`delete`、`ls`、`glob`、`grep` 等  
2. **任务规划**：通过显式启用 `TodoListMiddleware` 获得 `write_todos`（**v0.7 起默认不再自动打开**）  
3. **子 Agent 委派**：`task` 工具，把子任务派给隔离上下文的子 Agent  
4. **长期记忆**：基于 LangGraph Memory Store，支持跨会话/跨线程  

**v0.7 提醒**：文件工具含新增的 `delete`；默认基础提示词可能为空，业务 system prompt 由应用自定义；默认 Harness 更「轻」，长任务再叠加规划等中间件。

---

## 题 5：课程对比了 Deep Agents、Claude Agent SDK、Codex SDK，Deep Agents 的主要优势是什么？

**参考答案：**

课程指出，三者在文件读写、Shell、搜索、规划、子 Agent、MCP、HITL 等 **核心工具面** 接近，差异在架构：

**Deep Agents 较突出的优势：**

1. **模型无关**：可切换 Anthropic/OpenAI/Google/开源及 OpenAI 兼容网关（企业不锁厂商）  
2. **长期记忆**：Memory Store 跨会话持久化（课程写明 Claude/Codex SDK 侧不具备同等特性）  
3. **虚拟文件系统 + 可插拔后端**：统一文件接口，后端可内存/磁盘/DB/沙箱  
4. **Sandbox-as-Tool**：本地跑 Agent，特定操作可送远程沙箱  
5. **生产路径**：LangGraph Platform + LangSmith 可观测  

选择启发：要灵活模型与记忆 → Deep Agents；团队全 Claude → Claude Agent SDK；全 OpenAI → Codex SDK。

---

## 题 6（扩展）：DeepSeek Harness 与 DeerFlow 2 和 Deep Agents 的定位有何不同？

**参考答案：**

| 系统 | 更接近什么 | 一句话定位 |
|------|------------|------------|
| **Deep Agents** | **可嵌入的 Harness 库** | `create_deep_agent(...)` 嵌进 LangGraph/LangChain 应用，课程主线 |
| **DeepSeek Harness（DSH）** | **可运行的 Harness + 插件 Runtime** | 基于 Cordis，「Everything is a Plugin」，模型/工具/会话/UI/甚至 Agent Loop 可插拔；更像可改装的编码/通用 Agent 产品 |
| **DeerFlow 2** | **产品级长任务 SuperAgent 系统** | 字节开源，强调 minutes～hours：子 Agent、记忆、沙箱、Skills、消息网关、Gateway 部署 |

共同点：都覆盖文件、规划/技能、子 Agent、上下文管理等 Harness 共性能力。  
差异点：**交付形态**（库 vs 运行时/产品 vs 整站系统）与 **模型绑定程度**（Deep Agents 最开放；DSH 偏 DeepSeek 生态；DeerFlow 多 Provider 但部署更重）。

---

## 题 7（扩展）：结合本机实验，说明「模型无关」在实践中如何体现？

**参考答案：**

本机未使用硅基流动默认配置，而是：

- `ChatOpenAI(base_url="https://token.sensenova.cn/v1", api_key=...)` 接入商汤日日新  
- `AGENTSEEK_MODEL=glm-5.2`（可改为 `kimi-k3`、`deepseek-v4-flash` 等）  
- `switch_model.py --list/--set` 只改模型 ID，**不改 Harness 业务代码**  
- LangSmith 仍可对同一图做 Trace  

说明 Deep Agents 的 Harness 与「具体厂商模型」解耦：换 OpenAI 兼容端点即可，符合课程「模型灵活性」论点。

---

# ch02 快速上手

## 题 1：`create_deep_agent()` 的核心参数有哪些？分别做什么？

**参考答案：**

| 参数 | 作用 |
|------|------|
| `model` | 模型实例（如 `ChatOpenAI`）或 `provider:model` 字符串 |
| `tools` | 自定义工具列表（Python 函数） |
| `system_prompt` | 系统提示词，定义角色与行为 |

除用户传入的 `tools` 外，Harness 还会注入文件系统、子 Agent 等能力；v0.7 不默认启用任务规划，需要时显式加 `TodoListMiddleware`。

---

## 题 2：`agent.invoke()` 的输入输出格式是什么？

**参考答案：**

**输入**（字典，含 `messages`）：

```python
{"messages": [{"role": "user", "content": "你的问题"}]}
```

**输出**：同样包含 `messages` 的状态字典；**最后一条消息** 通常是 Agent 的最终回复：

```python
result["messages"][-1].content
```

一次 `invoke` 内部可能完成多次模型调用与工具调用（Agent Loop）。

---

## 题 3：什么是工具定义的「三要素」？缺少时可能有什么问题？

**参考答案：**

1. **参数名 + 类型标注**：告诉模型每个参数应传什么类型；缺标注易传错类型。  
2. **Docstring**：说明书，告诉模型何时该用这个工具；缺了模型不知道调用时机。  
3. **默认值**：标记可选参数，减少必填项、降低调用失败率。

示例：`convert_currency(amount: float, from_currency: str, to_currency: str = "CNY")` 中，类型 + 文档 + 默认 `CNY` 三要素齐全。

---

## 题 4：课程如何用 OpenAI 兼容接口接入第三方模型？请以本机日日新为例。

**参考答案：**

课程模式：`ChatOpenAI` + 自定义 `base_url` + 平台 API Key（供应商写 `openai` 是因为协议兼容）。

本机等价写法：

```python
ChatOpenAI(
    model="glm-5.2",
    api_key=os.environ["OPENAI_API_KEY"],          # 日日新 Key
    base_url="https://token.sensenova.cn/v1",      # OpenAI 兼容
)
agent = create_deep_agent(model=model, tools=[...], system_prompt="...")
```

注意：AgentSeek research **模板**读取的是 `OPENAI_API_KEY` / `OPENAI_API_BASE`，不要改成未声明的 `SENSNOVA_*` 变量名。

---

## 题 5：调用 `agent.invoke()` 时，Deep Agent 在背后可能自动做哪些事？

**参考答案（视任务与配置而定）：**

1. （若启用 Todo）用 `write_todos` 拆解任务  
2. 调用用户提供的工具（如搜索、天气、计算）  
3. 用虚拟文件系统读写，管理长结果、控制上下文  
4. （如需要）`task` 委派子 Agent  
5. 综合信息生成最终答复  

课程强调：开发者往往只写几行代码 + 一次 `invoke`，内部可能是 10+ 次工具/模型调用；LangSmith Trace 可将该过程可视化。

---

## 题 6：Deep Agents 对模型有什么硬性要求？复杂任务为何建议更强的模型？

**参考答案：**

**硬性要求**：模型需支持 **Tool Calling（函数/工具调用）**。纯对话、无 tools 能力的模型无法作为标准 Deep Agent 后端。

课程还指出：简单试跑可用轻量模型；**任务规划、上下文总结、多子 Agent 编排** 等需要更强模型，小模型（如 7B 级）可能跑不稳完整流程。本机默认 `glm-5.2` 并可用 `switch_model.py` 切换，即出于该考虑。

---

## 题 7：LangSmith 在 ch02 场景中起什么作用？如何开启？

**参考答案：**

**作用**：可观测平台——记录每次模型调用、工具调用、耗时、token、子 Agent 过程，用于理解「Agent 为什么这么做」并定位慢点/错误。  
**开启**：只需环境变量，一般不必改业务代码，例如：

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<你的 key>
LANGSMITH_PROJECT=deepagents-course
```

**本机经验**：变量必须写在应用实际加载的 `.env`（`research_deepagent\.env`）；改完后 **重启** `agentseek-api`，否则 UI 请求不会带上新配置。

---

## 题 8（扩展）：本机为何同时保留脚本练习与 AgentSeek research 项目？二者如何对应 ch02？

**参考答案：**

| 形态 | 作用 | 对应 ch02 |
|------|------|-----------|
| `hello_world.py` / `calculator_agent.py` | 最小闭环：模型 + 自定义工具 + invoke | Hello World 与「小试牛刀」 |
| `research_deepagent/` | 完整研究 Agent + 前端 + LangSmith | 进阶「研究助手」与可观测 |

脚本便于理解 API 与工具三要素；research 模板对应课程「真实多步研究」与生产向结构（前后端分离、生命周期配置）。两者共用日日新 OpenAI 兼容配置，体现同一模型接入方式。

---

## 答题技巧（简短版）

1. 先写 **定义**，再写 **对比/原因**，最后可加 **本机或课程例子**。  
2. ch01 分层题务必写清 **Runtime ≠ Framework ≠ Harness**。  
3. ch02 必写清 **输入 messages / 输出最后一条 content**、**工具三要素**、**Tool Calling 前提**。  
4. 涉及扩展对比时注明 DSH/DeerFlow 是 **产品/系统向**，Deep Agents 是 **可嵌入库**。  
5. 不要在答卷中粘贴真实 API Key。  
