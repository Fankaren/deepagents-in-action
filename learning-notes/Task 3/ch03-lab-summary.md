# Task 3 · ch03 实验小结（基于本人实测）

**实验目录**：`D:\agent_study\labs\ch03\`  
**模型**：日日新 `glm-5.2`  
**日期**：2026-09-20  

---

## 1. 实验结论一览

| Step | 预测 | 实际 | 结论 |
|------|------|------|------|
| 1 工具清单 | ls/read/write/grep | 7 FS + `task` + `execute`；`ls`→No files found | `tools=[]` 仍有 Harness 默认工具 |
| 2 write→read | B 摘要+路径 | write_file→read_file；FINAL 含路径与摘要 | 上下文外置；输出形态受 prompt 影响 |
| 2 加餐全文 | — | 同序列，FINAL 变为摘要+全文代码块 | 工具选择稳定，**输出长度由提示词决定** |
| 3 grep 三模式 | 语义基本正确 | 三种模式均 No matches（State 无 seed） | 语义对；**可见性由 Backend 决定** |
| 4 Backend | A 无 / B 有 | A 磁盘无；B `fs_root\workspace\hello.txt` 有 | 不能信「已写入」口头确认 |
| 5 Composite | workspace=State；memories=Filesystem（偏） | memories=**Store**；ls 聚合两套；Store key `('local-user',)` | 按路径路由；Store≠Filesystem |
| 6 Permission | 会被工具拒 | write_file@/policies/** → permission denied；ok.md 成功 | deny 是运行时强制门禁 |

---

## 2. 核心知识（用自己的话）

### 2.1 工具加载与选择（详见 Task 2 补充文档）

- **加载**：`create_deep_agent` 时 Harness 注入 FS/task 等，并 bind 到 ToolNode。  
- **选择**：每轮模型根据 schema、prompt、历史输出 `tool_calls`。  

### 2.2 虚拟文件系统七工具

`ls` · `read_file` · `write_file` · `edit_file` · `delete` · `glob` · `grep`  

- `write_file`：整文件覆盖；局部修改用 `edit_file`  
- `grep`：`files_with_matches` / `content`（匹配行）/ `count`；大仓库先定位再精读  
- 空 `ls`：v0.7 可能显示 `No files found`  

### 2.3 上下文自动管理

- 大结果约 **>20k tokens** 可卸载为「路径 + 预览」  
- 达阈值后历史可摘要；模型本轮看到摘要+近期消息  
- **提示词要求贴全文时，Agent 仍可 read_file 拉回** → 长任务需约束输出  

### 2.4 Backend

| Backend | 实测/理解 |
|---------|-----------|
| StateBackend（默认） | 线程草稿纸；磁盘不可见 |
| FilesystemBackend | `root_dir`+虚拟路径；`virtual_mode=True` 是**路径沙箱** |
| StoreBackend | 跨会话记忆；`namespace` 本地兜底 `local-user` |
| CompositeBackend | 按前缀路由；`ls` 聚合；v0.7 `backend=` 传**实例** |
| 权限 | `FilesystemPermission` deny 在工具执行前拦截 |

**共性**：工具可用 + 模型说成功 ≠ 数据在你期望的 Backend 里。

### 2.5 安全

- `root_dir` 下文件 Agent 都可读 → **勿放 `.env`/密钥**  
- Web/API 慎用裸 Filesystem；生产优先沙箱 + 权限  
- 自定义策略要覆盖 write/edit/**delete**  

---

## 3. 实测关键证据（可写入作业）

1. Step1 ToolNode 名单含全部 7 个 FS 工具。  
2. Step2 序列 `write_file` → `read_file`；改 prompt 后 FINAL 变长。  
3. Step3 seed 在磁盘，默认 State 下 grep 全空。  
4. Step4 Case A/B：Agent 均称已写入，仅 B 在 `fs_root\workspace\hello.txt` 落盘。  
5. Step5 `InMemoryStore` 探测 `ns/key: ('local-user',)`；`ls` 同时见 `/memories` 与 `/workspace`。  
6. Step6：`Error: permission denied for write on /policies/secret.md`。  

---

## 4. 简答可用要点（ch03）

**Q：为什么要虚拟文件系统？**  
A：避免 Prompt Stuffing；按需读写、搜索定位，Context Engineering。  

**Q：State 和 Store 怎么选？**  
A：临时草稿用 State；跨会话记忆用 Store（或 Composite 按 `/memories/` 路由）。  

**Q：如何验证 Agent 真的持久化了？**  
A：看 Backend 类型并用磁盘/Store 查询验证，不能只信 FINAL 文本。  

**Q：权限和 system_prompt 的区别？**  
A：权限是运行时强制；prompt 是模型自觉，可被绕过。  

---

## 5. 三句话总结

1. Deep Agents 默认注入文件与委派工具，模型再在推理时 Tool Calling 选择调用。  
2. Context Engineering 靠虚拟 FS + 自动卸载/摘要；是否贴全文仍取决于提示词。  
3. Backend 决定数据落点与可见性；Composite 按路径混合草稿纸与记忆库；Permission 在工具层强制。  

---

## 6. 后续章节钩子

| 疑问 | 去哪 |
|------|------|
| 规划如何影响下一步工具 | ch04 |
| `task` 子 Agent 细节 | ch05 |
| 权限 interrupt / 人审 | ch09 / ch11 |
| Skills、MCP 如何扩展工具表 | ch07 / ch12 |

---

## 7. 材料索引

- 工作坊：`labs/ch03/WORKSHOP.md`  
- 日志模板：`Task 3/lab-journal.md`  
- 工具加载与选择：`Task 2/tool-loading-and-selection.md`  
- 课程原文：ch03 虚拟文件系统  
