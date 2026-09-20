# ch03 虚拟文件系统 · 动手工作坊

**目标**：不是「读完笔记」，而是**你自己跑命令、先猜结果、再对照**。  
**环境**：conda `deepagents`（或任意已装 `deepagents` + 日日新配置的解释器）  
**模型**：日日新 `glm-5.2`（见 `D:\agent_study\.env`）

---

## 你怎么用这套材料

每个 Step 固定四步：

1. **读「本步要回答的问题」**（先自己写一句猜测）  
2. **运行**对应脚本  
3. **对照「观察清单」**勾选  
4. **做「你的任务」**（小改动，验证你真的懂了）

全部实验目录：`D:\agent_study\labs\ch03\`

启动环境（任选其一）：

```powershell
# 方式 A
D:\agent_study\start_env.bat
# 方式 B
C:\Users\18942\miniconda3\Scripts\activate.bat deepagents
cd D:\agent_study\labs\ch03
```

常用命令：

```powershell
python step0_predict.md  # 不存在，预测写在纸上或本 md 空白处
python step1_list_tools.py
python step2_write_read.py
python step3_grep_modes.py
python step4_backends.py
python step5_composite.py
```

---

## 背景 3 分钟（知道在学什么）

你平时怎么处理一堆资料？不会全摊在桌上，而是：**分类存放 → 需要再取 → 搜索定位 → 便签记中间结果**。

Deep Agents 给模型一套 **虚拟文件系统（Virtual FS）**，目的就是 Context Engineering：

| 不要这样做 | 要这样做 |
|------------|----------|
| 把所有文件/搜索结果塞进 prompt | 需要时 `read_file` / `grep` |
| 中间结果全靠「记在对话里」 | `write_file` 落盘，路径引用进上下文 |
| 换存储就改 Agent 逻辑 | 换 **Backend**（State / 磁盘 / Store / 混合） |

**七个内置工具**（v0.7）：

| 工具 | 作用 | 类比 |
|------|------|------|
| `ls` | 列目录与元信息 | 打开文件夹 |
| `read_file` | 读内容，可 `offset`/`limit`；可多模态 | 翻资料 |
| `write_file` | 新建或**整文件覆盖** | 重写草稿 |
| `edit_file` | 精确字符串替换 | 红笔改文档 |
| `delete` | 删文件/目录 | 清理 |
| `glob` | 按模式找文件 | 按标签找 |
| `grep` | 搜内容 | 全文检索 |

**自动上下文管理**（Agent 不用你手写逻辑）：

- 工具结果超过约 **20k tokens** → 写入虚拟 FS，对话里只留 **路径 + 前 10 行预览**  
- 上下文达阈值 → **旧消息存 Backend**，模型本轮看到的是 **摘要 + 近期消息**（原始历史仍在 State/文件里）

**Backend（存哪里）**：

| Backend | 生命周期 | 典型用途 |
|---------|----------|----------|
| StateBackend（默认） | 线程内有效 | 草稿纸、实验 |
| FilesystemBackend | 本地磁盘永久 | 编程助手 |
| StoreBackend | 跨会话 | 记忆/知识库 |
| CompositeBackend | 按路径混合 | 临时 + `/memories/` 持久 |
| LocalShell / 沙箱 | 执行代码 | 本地高危 / 生产隔离 |

---

## Step 1 · 看见工具（15 分钟）

### 本步要回答的问题

> 不写任何自定义 tool，Deep Agent **默认**会带上哪些与文件相关的工具？名字是什么？

### 你的任务（先做再跑）

1. 在下面空白处 **先写猜测**（至少 3 个工具名）：  
   - 我猜：________________  
2. 运行：

```powershell
cd D:\agent_study\labs\ch03
python step1_list_tools.py
```

### 观察清单

- [ ] 脚本是否打印出一批 tool 名称  
- [ ] 其中是否出现 `ls` / `read_file` / `write_file` / `glob` / `grep` / `edit_file` / `delete`  
- [ ] 是否还有你没猜到的（如与 task/memory 相关）  
- [ ] **没有**自定义业务工具时，Harness 仍注入 FS 工具 → 证明「开箱 Harness」不是空话  

### 知识点落袋

- Harness 能力 = **框架预置**，不是 `tools=[]` 时 Agent 什么都不会  
- 后面每一步都是在「工具已存在」的基础上观察 **Agent 会不会用、Backend 存在哪**

---

## Step 2 · 写入再读出（20 分钟）

### 本步要回答的问题

> 让 Agent **先写文件、再读回来复述**，最终回答里的信息来自哪里？对话消息本身会不会塞进全文？

### 你的任务

1. **预测**：Agent 最终 `content` 里更可能出现  
   - A. 全文粘贴文件  
   - B. 一句总结 + 可能提到路径 `/...`  
2. 运行：

```powershell
python step2_write_read.py
```

3. 打开脚本输出里提示的 **消息轨迹摘要**（脚本会列出 tool 调用名）。确认是否出现 `write_file` → `read_file`。

### 观察清单

- [ ] 有 `write_file` 调用  
- [ ] 有 `read_file`（或 Agent 声称已根据文件作答）  
- [ ] 最终回复是 **摘要风格**，而不是整份文件原文  
- [ ] （进阶）若你改 prompt 要求「必须原文粘贴」，对比长度  

### 你的任务（改代码）

把 `step2_write_read.py` 里的提示改成：

1. 写入 `/workspace/notes/team.md`，内容为 **至少 8 条** 互不相同的项目约定  
2. 再读出并只总结 **第 3 条和第 7 条**  

重新运行。你看到工具调用顺序有无变化？

### 知识点落袋

- 虚拟 FS 是 **外置存储**；对话里更常见的是 **路径与预览**  
- `write_file` 是 **覆盖写**；改局部要用 `edit_file`（下一章实验可自己试）

---

## Step 3 · grep 三种模式（20 分钟）

### 本步要回答的问题

> 同样是搜索，`files_with_matches` / `content` / `count` 分别适合什么阶段？

### 你的任务

1. **填表预测**（先写再跑）：

| 模式 | 返回什么 | 适合 |
|------|----------|------|
| files_with_matches | ？ | ？ |
| content | ？ | ？ |
| count | ？ | ？ |

2. 运行：

```powershell
python step3_grep_modes.py
```

脚本会先在磁盘 `workspace_grep/` 里造几个假文件，再让 Agent 按三种模式搜 `TODO` / 函数名等。

### 观察清单

- [ ] Agent **是否分多次** 调用 `grep`（而不是一次 content 全糊）  
- [ ] 输出里是否只在合适时机出现文件路径列表 vs 行内容  
- [ ] 你能否从 Trace/日志看出「先定位再深入」的策略（若模型没做，这正是小模型局限，可换模型再跑）  

### 你的任务

把搜索目标改成你真实关心的关键词（例如仓库里的 `create_deep_agent`），对比 `count` 与 `content` 的回答长度。

### 知识点落袋

- v0.7：`grep`/`glob` 可能 **截断**（`truncated=True`），成功 ≠ 全集  
- 先 `files_with_matches`/`count`，再 `content`，是 **省上下文** 的标准姿势  

---

## Step 4 · 换 Backend：草稿纸 vs 真磁盘（25 分钟）

### 本步要回答的问题

> 同一段「请写入 `/workspace/hello.txt`」，**StateBackend** 与 **FilesystemBackend** 结束后，**你的磁盘上有没有多出文件**？

### 你的任务

1. **预测**：  
   - 默认 State：磁盘可见文件？ 是 / 否  
   - FilesystemBackend(root_dir=...)：磁盘可见文件？ 是 / 否  
2. 运行：

```powershell
python step4_backends.py
```

3. 亲自检查（不要只信打印）：

```powershell
Get-ChildItem D:\agent_study\labs\ch03\fs_root -Recurse
```

### 观察清单

- [ ] State 组结束后，`fs_root` **没有**（或未新增）hello 文件  
- [ ] Filesystem 组结束后，`fs_root\hello.txt` **存在**，内容能 `Get-Content` 看到  
- [ ] 理解：`virtual_mode=True` 是路径沙箱，**不是**「文件只在内存」  

### 你的任务（安全意识）

1. 故意让 Agent 尝试 `read_file("/../.env")` 或 `C:/Windows/win.ini`（改 prompt）。  
2. 在 `virtual_mode=True` + `root_dir=fs_root` 下，期望结果是什么？  
3. 记录：拒绝还是读到？  

**红线（课程原文）**：FilesystemBackend 能读 root 下所有文件（含 `.env`）；Web/API **不要**用裸磁盘后端；生产慎用 LocalShell。

### 知识点落袋

- Backend = **存储策略**，工具名可以不变  
- State：线程内「草稿纸」；Filesystem：**永久、可逆性差**  
- `virtual_mode` 必填意识：防 `..`、`~` 越界  

---

## Step 5 · Composite：草稿纸 + 记忆库（30 分钟）

### 本步要回答的问题

> 路径前缀如何路由？`/workspace/x.md` 与 `/memories/y.md` 会不会走不同后端？

### 你的任务

1. **画一张你自己的路由图**（纸上）：

```text
/workspace/**  →  ??
/memories/**   →  ??
其余           →  ??
```

2. 运行：

```powershell
python step5_composite.py
```

3. 对照脚本打印：哪些路径被标成 state，哪些进入 store（或本地模拟持久化目录）。

### 观察清单

- [ ] Agent 写入两条不同前缀路径  
- [ ] 结果显示两条 **不会** 都消失在同一「临时状态」里  
- [ ] 你能在笔记里用一句话解释：**Composite = 按 path 选 Backend**  

### 你的任务

增加第三条路由，例如 `/scratch/**` → State，`/memories/**` → Store，其余 State。  
让 Agent 一次任务里三个前缀各写一个文件，检查是否符合你的路由图。

### 知识点落袋

- v0.7：`backend=` 必须是 **Backend 实例**（工厂 lambda 已移除）  
- Store 的 `namespace` 本地要对 `rt.server_info is None` 做兜底  
- 「记忆」不是魔法关键字，是 **路径约定 + 后端路由**  

---

## Step 6 · 权限与策略（选做，20 分钟）

### 本步要回答的问题

> `FilesystemPermission(mode="deny")` 与「模型自觉不写」有何本质区别？

### 你的任务

运行：

```powershell
python step6_permission.py
```

### 观察清单

- [ ] Agent **尝试**写 `/policies/secret.md`（或脚本指定的禁止路径）  
- [ ] 结果是 **工具层拒绝**，而不是最终答案里「我选择不写」  
- [ ] 理解：**权限在工具执行前判定**（first-match-wins），与 prompt 道德约束无关  

### 知识点落袋

- `mode`: `allow` / `deny` / `interrupt`（interrupt 见第 9 章）  
- 自定义后端/PolicyWrapper 时要同时保护 `write` / `edit` / **`delete`**  

---

## 推荐学习节奏（给自己排期）

| 时段 | 完成 |
|------|------|
| 第 1 次 | Step 1–2 + 自己改 prompt |
| 第 2 次 | Step 3–4 + 磁盘亲自 ls |
| 第 3 次 | Step 5（+6 选做）+ 写 Task 3 小结 |

每完成一步，把「预测 vs 实际」差异写进 `learning-notes/Task 3/lab-journal.md`（实验记录模板见同目录）。

---

## 和课程原文的对应

| 本工作坊 | 课程 ch03 |
|----------|-----------|
| Step 1–3 | 内置工具、read_file、grep |
| Step 2 | 大结果卸载、上下文自动管理（观察层） |
| Step 4–5 | 可插拔 Backend、Composite |
| Step 6 | FilesystemPermission / 策略 |

完整论述仍以 [课程 ch03](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) 为准；本目录负责 **动手路径**。

---

## 做完后自测（口述）

1. 为什么 FS 比「全塞 prompt」更省且更稳？  
2. `write_file` 和 `edit_file` 何时用哪个？  
3. State vs Filesystem vs Store 各一句话？  
4. Composite 解决什么产品问题？  
5. 为何 deny 要写在 Permission，而不是只写在 system_prompt？  
