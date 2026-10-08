# Task 8 · ch08 预测题（先作答，再执行）

> 用法：**每个 Step 运行前**先在此勾选你的预测；跑完把「实际」填回 `lab-journal.md`。
> 预测对了验证理解，预测错了最有教学价值（ch07 遗产：猜错照样是素材）。
> 判定器输出的 `PASS/FAIL` 是「实际」，本文件只放「预测」。

---

## Step 0 · 仪器单测 + 判定器体检（零模型调用）

**Q0-1** 运行 `step0_selftest.py`，你预计通过率？
- A. 全 9 项 PASS
- B. 多数 PASS，个别失败
- C. 大量 FAIL

**Q0-2** 「memory 注入有没有生效」的正确观测点是？
- A. `result["messages"]` 里的 SystemMessage
- B. `on_chat_model_start` 拦到的【模型请求】
- C. graph state 的 `files` 字段

> 验证方式：step0 **只能证明 B 可实现**，不能证伪 A/C；真正的判别证据在 **Step 4-B**（金丝雀在请求里、不在 `result["messages"]` 里）。

**Q0-3** 自定义 callback 若不继承 `BaseCallbackHandler`，会发生什么？
- A. 静默失效，什么都不记
- B. 抛 `AttributeError`（缺 `raise_error` 等属性）
- C. 正常工作

> 验证方式：step0 第 7 项**负样本**（裸对象当 callback）实测；只做正向 `issubclass` 断言不算实证。

---

## Step 1 · 跨线程记忆闭环

**Q1-1** thread A 启动时，请求里是否含初始金丝雀 `MEM-CANARY-LOAD-7f3a91`？
- A. 含（启动加载已有记忆生效）
- B. 不含

**Q1-2** 对话 1 后，`store.get(...)` 里的 `preferences.md` 会包含「代码注释用中文」吗？
- A. 会，且初始金丝雀也保留（模型用 `edit_file` 局部改）
- B. 会，但初始金丝雀被覆盖（模型用 `write_file` 整文件覆盖）
- C. 不会（模型没真正调用写入工具）

**Q1-3** 对话 2（**全新** `thread_id`）的【模型请求】里会出现已保存偏好吗？
- A. 会出现（跨线程加载）
- B. 不会出现
- C. 只有继续用旧 thread_id 才出现

**Q1-4** 对话 2 的回答会遵守那条偏好（中文注释 / 英文变量名）吗？
- A. 会
- B. 不会
- C. 只遵守一半

---

## Step 2 · 作用域：隔离 vs 共享

**Q2-1** user-scoped：用户 A 的请求里会出现用户 B 的金丝雀 `USER-B-SECRET-4k7` 吗？
- A. 不会（namespace 按 user_id 隔离）
- B. 会

**Q2-2** agent-scoped：用户 A 与用户 B 是否都能看到同一份共享金丝雀 `SHARED-AGENT-77`？
- A. 都能看到（共享 = 不隔离）
- B. 只有 A 能看到
- C. 都看不到

**Q2-3** 两个用户是否落在**不同** namespace？
- A. 是
- B. 否

---

## Step 3 · CompositeBackend 路由

**Q3-1** `write_file("/memories/route-note.md", ...)` 的内容最终落在哪？
- A. Store（`store.get` 能读到）
- B. thread1 的 `state.files`
- C. 两边都有

**Q3-2** `write_file("/workspace/route-scratch.md", ...)` 的内容落在哪？
- A. thread1 的 `state.files`
- B. Store
- C. 磁盘

**Q3-3** thread 2（全新线程）的 `state.files` 里还有那个 workspace 文件吗？
- A. 没有（线程内即消失）
- B. 有（写进了 state 就一直在）

**Q3-4** Store 里的 `/memories/` 文件，thread 2 还能读到吗？
- A. 能（跨线程持久）
- B. 不能

---

## Step 4 · 初始化 / 缺失文件 / 覆盖

**Q4-1** `memory=["/memories/nonexistent.md"]` 指向一个不存在的文件，它会被自动创建吗？
- A. 会
- B. 不会（跳过，不创建）

**Q4-2** 这个缺失路径会被作为「已加载记忆」注入系统提示吗？
- A. 会
- B. 不会

**Q4-3** 用 `store.put(ns, "/seeded.md", create_file_data(...))` 外部预填后，新线程请求里会出现金丝雀 `SEED-CANARY-5e1f` 吗？
- A. 会（预填生效）
- B. 不会

**Q4-4** 让 Agent「新增第三条偏好」，已有两条是否会被保留？
- A. 保留（用了 `edit_file`）
- B. 被覆盖（用了 `write_file`）
- C. 取决于提示词是否强调「保留已有条目」+ 模型选哪个工具

---

## 作答方式

把每题的选择写在同一行，例如：

```text
Step0: Q0-1=A  Q0-2=B  Q0-3=B
Step1: Q1-1=  Q1-2=  Q1-3=  Q1-4=
...
```

跑完把实际结果贴给我，我来写三段式记录。
