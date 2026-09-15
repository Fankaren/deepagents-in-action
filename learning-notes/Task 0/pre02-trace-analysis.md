# pre02 §5 · LangSmith Trace 分析（实操记录）

**日期**：2026-09-16  
**项目**：`deepagents-course`  
**Trace ID**：`01a0a684-0ce6-7802-a78e-529d13fde29f`  
**总耗时**：28.12s  
**Token**：26,136  

任务：*Research what LangGraph 1.0 added vs 0.x（简短 bullet）*  
模型：日日新 `glm-5.2`（ChatOpenAI）

---

## 1. Trace 层级（根 → 中间件 → 叶子）

```text
LangGraph (chain) 28.12s
├── model → … → ChatOpenAI (llm) 10.95s   tokens 21,898
├── model → … → ChatOpenAI (llm)  6.05s   tokens  4,238
├── tools → tavily_search (tool) 10.69s
└── tools → tavily_search (tool)  9.54s
```

**不要把** 根 `LangGraph`、`model` chain 包装、`FilesystemMiddleware.wrap_*` **当成瓶颈叶子**；真正耗时在：

| 叶子 | 类型 | 耗时 | Tokens | Run ID |
|------|------|------|--------|--------|
| ChatOpenAI | llm | **10.95s** | 21,898 | `01a0a684-4ff7-...` |
| ChatOpenAI | llm | 6.05s | 4,238 | `01a0a684-0e78-...` |
| tavily_search | tool | **10.69s** | — | `01a0a684-2624-...` |
| tavily_search | tool | 9.54s | — | `01a0a684-2622-...` |

---

## 2. 瓶颈判断

| 调用 | 证据 | 可能原因 | 建议 |
|------|------|----------|------|
| 最慢 LLM 10.95s | 第二轮模型调用，token 2.1 万 | 输入含 Harness 系统提示 + 文件工具 schema + 第一轮搜索结果 | 缩短研究范围；确认 v0.7 是否已减少默认提示；避免一次塞入过多搜索原文 |
| tavily_search ~10s | 外部 HTTP | 网络 + 页面抓取/正文转换 | 降低 `max_results`；缓存重复查询；检查代理 |
| 两次 LLM 合计 ~17s | 约占总时长 60% | 模型侧推理 + 大上下文 | 复杂任务换更强模型；简单任务用 flash 类 |

**结论**：本次是 **「大上下文 LLM + 外网搜索」** 双瓶颈；中间件包装层耗时 ≈ 内部叶子，不是额外开销。

---

## 3. CLI 命令备忘

```powershell
langsmith project list
langsmith trace list --project deepagents-course --limit 5 --include-metadata
langsmith trace get <trace-id> --project deepagents-course --include-metadata
langsmith run list --trace-ids <trace-id> --project deepagents-course --run-type llm --limit 50
langsmith run list --trace-ids <trace-id> --project deepagents-course --run-type tool --limit 50
langsmith run get <run-id> --project deepagents-course --include-io
```

注意：`--name research` 在本 CLI 版本可能 400；本图根节点名为 `LangGraph`。

---

## 4. pre02 完成判定

| 检查项 | 结果 |
|--------|------|
| 区分根 / 中间件 / 叶子 | 已完成 |
| 找到最慢 llm | 10.95s ChatOpenAI |
| 找到最慢 tool | 10.69s tavily_search |
| 有 run_id + 耗时证据 | 见上表 |
| 建议与证据对应 | 见「瓶颈判断」 |

**pre02 Trace 实操：完成。**
