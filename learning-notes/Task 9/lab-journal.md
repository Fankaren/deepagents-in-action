# Task 9 · 实验日志（lab-journal）

每做完一个 Step，复制一节填进去。开跑前先跑 `python step0_selftest.py` 做「仪器单测 + 判定器体检」。

---

## Step 0 · 仪器单测 + 判定器体检（零模型调用）

- 预测：Q0-1=A Q0-2=B
- ToolLedger 记录/计数/取参/清空：全部正确 ✓
- 四决策构造器形状：approve/reject/edit/respond 均正确 ✓
- 中断结构解析（假 result）：action_names / action_args(兼容 arguments) / review_map / messages_text 均正确 ✓
- 全部 PASS / 有 FAIL：**14/14 PASS**

## Step 1 · 首次中断（approve）

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 暂停时账本为空 | B | PASS（`[]`） |
| P2 动作名 send_email | A | PASS |
| P3 approve 后账本 1 笔 | B | PASS |
| P4 使用原始参数 | B（押错）→ 实际 A | **PASS（to=admin@example.com 原始参数）** |

- 中断时看到的参数：`{to: admin@example.com, subject: 通知, body: 系统维护}`
- 最终消息含 EMAIL-SENT：是（模型回复"邮件已成功发送"）
- 一句话总结：HITL 的暂停发生在**副作用之前**；approve 用**原始参数**执行

## Step 2 · 三种决策

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 reject 后账本 0 笔 | B（押错）→ 实际 A | **PASS（账本 `[]`）** |
| P2 reject 原因回流 | A | PASS |
| P3 edit 用改后参数 | B | PASS（to=team@example.com） |

- 三种决策在账本上的差异（一句话）：**approve=1 笔原参 / edit=1 笔改参 / reject=0 笔（不执行）**；reject 的 message 还会作为 ToolMessage 回流

## Step 3 · respond + 批量

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 respond 工具体不执行 | A（押错）→ 实际 B | **PASS（账本不含 ask_user）** |
| P2 批量打包成 1 个中断 | B（押错）→ 实际 A | **PASS（首轮 2 动作、共 1 轮）** |
| P3 [approve SQL, reject email] 只 SQL 执行 | A | PASS |

- respond 与 reject 的本质区别（一句话）：**respond 把人的话当成功工具结果（工具体不跑）**；reject 明确告诉模型工具没执行
- 打包观察：首轮 2 动作、共 1 轮（同轮并行）；打包与否取决于模型是否并行发多个 tool_calls

## Step 4 · 条件中断 + 文件系统权限

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 区内写入不中断 | B | PASS（files 有 notes.txt） |
| P2 区外写入中断 | A | PASS（动作 write_file） |
| P3 /secrets/** 写入中断 | A | PASS（动作 write_file） |

- `when` 谓词的作用（一句话）：**返回 True 才中断**——只把真正需要人决策的调用放进审批，其余自动放行
- 两种中断格式一致（都可 `Command(resume=...)` 恢复），可与 `interrupt_on` 合并

## Step 5 ·（选做）底层 interrupt()

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 恢复用 {"approved": True} | A（押错）→ 实际 B | **PASS（raw value 恢复）** |
| P2 节点从头重放 | A（押错）→ 实际 B | 机制如此（非从下一行） |

- 五条使用规则里最反直觉的一条：**恢复时节点从头重放**——`interrupt()` 之前的代码会再跑一次，所以副作用必须幂等

---

## 本章三句话总结（自己写，勿抄）

1.
2.
3.

## 还没搞懂的问题

-
