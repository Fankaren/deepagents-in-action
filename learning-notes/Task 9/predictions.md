# Task 9 · ch09 预测题（先作答，再执行）

> 每个 Step 运行前先在此勾选预测；跑完把「实际」填回 `lab-journal.md`。
> 判定器输出的 PASS/FAIL 是「实际」，本文件只放「预测」。

---

## Step 0 · 仪器单测 + 判定器体检（零模型调用）

**Q0-1** 运行 `step0_selftest.py`，预计通过率？
- A. 全 PASS
- B. 个别失败
- C. 大量 FAIL

**Q0-2** 判定「敏感工具的副作用有没有发生」的正确观测点是？
- A. 模型的文字回答
- B. 工具**副作用账本**（工具真正执行才记一笔）
- C. 消息历史长度

---

## Step 1 · 首次中断（approve 路径）

**Q1-1** 第一次 invoke 后（尚未恢复），账本里有 `send_email` 吗？
- A. 有 1 笔（先执行了）
- B. 空（暂停发生在副作用之前）

**Q1-2** 第一次 invoke 后 `interrupts` 里的动作是？
- A. `send_email`
- B. `read_file`
- C. 无中断

**Q1-3** 恢复 `approve` 后，账本里有几笔？
- A. 0
- B. 1
- C. 2

**Q1-4** approve 执行时用哪套参数？
- A. Agent 提出的原始参数（to=admin@example.com）
- B. 被改后的参数

---

## Step 2 · 三种决策（approve / reject / edit）

**Q2-1** `reject` 后账本里有几笔？
- A. 0
- B. 1

**Q2-2** `reject` 的 `message` 会出现在**后续模型请求**里（回流）吗？
- A. 会
- B. 不会

**Q2-3** `edit` 后执行时用的收件人是？
- A. admin@example.com（原始）
- B. team@example.com（改后）

---

## Step 3 · respond + 批量中断

**Q3-1** `respond` 决策时，`ask_user` 的**工具体**会执行吗？
- A. 会
- B. 不会（人的 message 直接当工具结果）

**Q3-2** 一次调用两个敏感工具，打包成几个中断？
- A. 1 个（含 2 个 action）
- B. 2 个独立中断

**Q3-3** 批量给 `[approve SQL, reject email]` 后，账本里有什么？
- A. 只有 SQL 执行
- B. 只有 email 执行
- C. 两个都执行

---

## Step 4 · 条件中断 + 文件系统权限中断

**Q4-1** 写 `/workspace/notes.txt`（区内），会中断吗？
- A. 会
- B. 不会（`when` 返回 False）

**Q4-2** 写 `/notes.txt`（区外），会中断吗？
- A. 会
- B. 不会

**Q4-3** 写 `/secrets/token.txt`，会中断吗？
- A. 会（FilesystemPermission mode="interrupt"）
- B. 不会

---

## Step 5 ·（选做）底层 interrupt()

**Q5-1** 自定义 Middleware 里 `interrupt()` 的恢复用什么？
- A. `Command(resume={"decisions": [...]})`
- B. `Command(resume={"approved": True})`
- C. 不需要恢复

**Q5-2** 恢复时节点从哪里继续执行？
- A. 从 `interrupt()` 的**下一行**
- B. 从**节点开头重放**（interrupt 之前的代码会再跑一次）

---

## 作答方式

```text
Step0: Q0-1=  Q0-2=
Step1: Q1-1=  Q1-2=  Q1-3=  Q1-4=
...
```
