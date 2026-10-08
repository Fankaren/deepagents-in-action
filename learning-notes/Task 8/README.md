# Task 8 · ch08 长期记忆（StoreBackend / CompositeBackend / 三种作用域）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/>

## 怎么学

沿用四拍工作坊 + 判定器体检 + 仪器单测（ch05/06/07 遗产）。**无需起服务**，回到轻量模式。
核心观测点：`memory=` 注入的是**模型请求**里的 system 提示——用 `RequestCapture` 拦在请求上，不读 `result["messages"]`。
证据链：**写入看 Store 断言，加载看请求文本**，两者分开验证（不轻信模型口头「已记住」）。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板（预测 vs 实际） |
| `progress-log.md` | 会话过程记录（每会话收尾追加） |
| `ch08-lab-summary.md` | 实测小结（提交主文档，**待跑**） |
| `labs/ch08/WORKSHOP.md` | 一步步怎么做（四拍） |
| `labs/ch08/_common.py` | 公共仪器与判定器（RequestCapture / Judge / namespace 兜底） |
| `labs/ch08/step0_selftest.py` | **零模型调用**：仪器单测 + 判定器体检 |
| `labs/ch08/step1_cross_thread.py` | 跨线程闭环：thread A 写 → 查 Store → thread B 加载 |
| `labs/ch08/step2_scopes.py` | 作用域：user-scoped 隔离 vs agent-scoped 共享 |
| `labs/ch08/step3_routing.py` | CompositeBackend 路由：`/memories/` 持久 vs `/workspace/` 线程内 |
| `labs/ch08/step4_init_missing.py` | 缺失文件跳过、外部预填、覆盖 vs 追加 |

## 本机版本基线

- deepagents **0.7.14**（本章代码按 0.7.10+ 行为编写）/ langchain-openai；模型经商汤日日新接入 `glm-5.2`
- `StoreBackend` 存文件用 v2 格式 JSON（`content` 完整字符串 + `encoding`），由 `create_file_data` 生成
- `CompositeBackend` 路由：Agent 可见路径去掉前缀后作为 Store key；直接挂 `StoreBackend`（无路由层）则保留完整虚拟路径
- `memory=` 是**读取配置**：缺失文件跳过、不创建、不注入；写入位置须靠提示词/工具约定

（待办：Step 0–4 跑完后补 `ch08-lab-summary.md` 与收官记录）
