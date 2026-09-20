# Task 2 补充 · 工具如何加载与选择

**适用**：ch01 Harness 概念 + ch02 快速上手 + ch03 动手观察（Step1/Step2）  
**实验现象来源**：`D:\agent_study\labs\ch03\step1_list_tools.py` / `step2_write_read.py`

---

## 1. 一句话分清两件事

| 问题 | 答案 | 发生在何时 |
|------|------|------------|
| **工具怎么被加载进 Agent？** | `create_deep_agent` 时把「你的 tools + Harness 默认工具」bind 到模型，并挂到 LangGraph 的 **ToolNode** | **建图时**（静态） |
| **模型怎么决定调用哪个？** | 每轮 LLM 根据 **工具 schema/docstring + system_prompt + 用户问题 + 对话历史** 输出 `tool_calls` | **每次推理时**（动态） |

`tools=[]` **不等于**没有工具，只等于「你不额外注册业务工具」。

---

## 2. 加载链路（Harness 为什么会「无中生有」）

```text
create_deep_agent(model, tools=[], system_prompt=...)
        │
        ├─ ① 用户传入 tools（可为 []）
        │
        ├─ ② Harness / Middleware 注入默认能力
        │      文件：ls, read_file, write_file, edit_file, delete, glob, grep
        │      编排：task（子 Agent）
        │      （视 Backend 等还可能出现 execute 等）
        │
        ├─ ③ 生成 OpenAI Function Calling 用的 tools schema
        │      （name / description / parameters JSON Schema）
        │
        └─ ④ bind_tools → 图中 ToolNode 持有可执行函数
```

**Step1 实测**（`tools=[]`）ToolNode 上出现的名字：

```text
delete, edit_file, execute, glob, grep, ls, read_file, task, write_file
```

其中 **7 个文件工具** 对应课程 ch03；`task` 对应子 Agent 委派（ch05）；`execute` 与执行/Backend 相关。

**若你写了 `tools=[get_weather]`**：清单 = 默认集 **∪** 你的工具，而不是只有天气。

**需要「显式打开」的能力**（不是 `tools=[]` 就自动有）：

| 能力 | 如何出现 |
|------|----------|
| `write_todos` 任务规划 | 传入 `TodoListMiddleware`（ch04，v0.7 默认更轻） |
| 自定义业务工具 | 你传入 `tools=[...]` |
| MCP 等外部工具 | 通过 MCP 接入（ch12） |
| 运行时 Skills | `create_deep_agent(skills=...)`（ch07） |

---

## 3. 选择链路（模型如何「点名」某个工具）

Deep Agents 要求模型支持 **Tool Calling**。每轮大致是：

```text
messages + tools(schema)
        │
        ▼
   LLM 输出
   要么 tool_calls=[{name, args}]
   要么最终自然语言答案
        │
        ▼
   ToolNode 执行对应 Python 函数
        │
        ▼
   ToolMessage 写回 messages
        │
        └──► 再次调 LLM（循环，直到无 tool_calls）
```

**影响「选谁」的因素（按调试优先级）：**

1. **工具描述 / 参数 schema**（三要素：类型标注、docstring、默认值 → ch02）  
2. **system_prompt**（如「必须先 write 再 read」）  
3. **用户指令**（「列出根目录」→ 倾向 `ls`）  
4. **已有对话与工具结果**（刚写完再问内容 → `read_file`）  
5. **模型能力**（弱模型漏调/错参；复杂任务换强模型）

Harness **保证「调得动」**；**「调不调、调谁」由模型决定**，可用 Trace 看 `tool_calls`。

---

## 4. 用 Step2 现象巩固（已实测）

**你的预测**：B（摘要 + 路径）  

**实际工具序列**：

```text
write_file
ToolMessage<-write_file
read_file
ToolMessage<-read_file
```

**FINAL** 含路径 `/workspace/notes/demo.md`，内容为**要点总结**，而非全文粘贴。

**说明：**

| 观察 | 对应知识点 |
|------|------------|
| 出现 `write_file` / `read_file` | 模型在默认工具集里**主动选择**了 FS 工具（选择层） |
| 先写后读 | 与 system_prompt / 用户指令一致，不是随机调用 |
| 摘要 + 路径 | 上下文**外置**到虚拟 FS；对话里保留引用与概括（Context Engineering） |

若改 prompt 为「必须原文粘贴全文」，FINAL 会变长——同一套工具，**选择与输出策略**由提示词改变。

---

## 5. 和课程章节的对应（会不会解答你的疑问）

| 疑问 | 章节 |
|------|------|
| 为何默认就有文件工具 | ch01 Harness、ch03 VFS |
| 工具描述如何影响调用 | ch02 三要素 |
| 规划如何改变下一步调用 | ch04 Todo |
| `task` 子 Agent 工具 | ch05 |
| 新能力如何插进工具表 | ch07 Skills、ch12 MCP |
| 权限能否拦住已加载的工具 | ch03/ch11 Permission（工具层 deny） |

**结论**：后面内容会继续展开，但**主干已在本节讲清**——加载在 create，选择在每轮 LLM。

---

## 6. 自测（建议口头答）

1. `tools=[]` 时 Step1 为何仍列出 `write_file`？  
2. 建图时与推理时分别决定什么？  
3. 如何让 Agent「更容易」调用某个自定义工具？（答：docstring + prompt + 示例问题）  
4. Step2 中证明「选择」与「外置」的证据各是什么？  

---

## 7. 调试清单（以后遇到「模型不用工具」）

- [ ] 模型是否支持 tool calling  
- [ ] 工具是否真的 bind（打印 ToolNode / Trace）  
- [ ] docstring 是否说明「何时用」  
- [ ] system_prompt 是否与期望工具一致  
- [ ] 是否该用更强模型 / 是否被 Permission deny  
- [ ] 改 `.env` 后是否重启了 `agentseek-api`（研究应用场景）  
