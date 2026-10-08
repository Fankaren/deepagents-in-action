# Task 8 · 实验日志（lab-journal）

每做完一个 Step，复制一节填进去。开跑前先跑 `python step0_selftest.py` 做「仪器单测 + 判定器体检」。

---

## Step 0 · 仪器单测 + 判定器体检（零模型调用）

- 预测：Q0-1=A Q0-2=B Q0-3=B
- `RequestCapture` 是否继承 BaseCallbackHandler：是 ✓
- 能否抓到 system/human 文本：能 ✓（多块 content 也可 ✓）
- 全部 PASS / 有 FAIL：首跑 9/9 PASS；补负样本后 **10/10 PASS**
- 预测性质：Q0-1 实测✓；Q0-3 需负样本才实测✓（已补）；Q0-2 属知识题，实测证据留 Step 4-B

## Step 1 · 跨线程记忆闭环

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 thread A 请求含初始金丝雀（启动加载） | A | PASS |
| P2 Store 里真的有偏好（不只看口头确认） | A | PASS |
| P3 thread B 请求含已保存偏好（跨线程） | A | PASS |

- thread A / thread B 的 thread_id：`906bd541-…` / `10762e6a-…`（全新线程）
- 偏好文件写入后的内容（抄一行）：`- 代码注释用中文` / `- 变量名用英文` / `<!-- MEM-CANARY-LOAD-7f3a91 -->`（金丝雀保留）
- 一句话总结：跨线程加载的证据是——**新 thread_id 的模型请求 system 提示里出现已保存偏好**（写入侧由 `store.get` 佐证）

## Step 2 · 作用域：隔离 vs 共享

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 user-scoped：A 请求不含 B 金丝雀 | A | PASS |
| P2 agent-scoped：A、B 都看到共享金丝雀 | C（押错）→ 实际 A | **PASS（都能看到，共享=不隔离）** |
| P3 两用户 namespace 不同 | A | PASS |

- 一句话总结：作用域 = **namespace 的写法**（`(user_id,)` 隔离 / `(assistant_id,)` 共享 / `(org_id,)` 组织级）

## Step 3 · CompositeBackend 路由

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 `/memories/` 落在 Store | A | PASS（content=`ROUTE-MEM-1123`） |
| P2 `/workspace/` 落在 thread1 的 state.files | A | PASS |
| P3 thread2 的 state.files 不含 workspace 文件 | B（押错）→ 实际 A | **PASS（thread2 files=[]，线程内消失）** |

- 我画的路由图：
  ```text
  /memories/**  →  StoreBackend（跨线程持久）
  /workspace/** →  StateBackend（线程内）
  其余          →  default StateBackend
  ```
- 一句话总结：Composite = **按 path 前缀选 Backend**

## Step 4 · 初始化与缺失文件

| 预测 | 答案 | 实际 |
|------|------|------|
| P1 缺失文件被自动创建？ | B 不会 | PASS（未创建） |
| P2 缺失路径被注入提示？ | B 不会 | PASS（未注入） |
| P3 外部预填金丝雀进入新线程请求 | A 会 | PASS |
| P4 Q0-2：金丝雀在请求里、不在 result 里 | — | PASS（命中角色=无） |

- C 组观察：已有偏好被保留还是覆盖：**保留**（追加第三条，前两条仍在）
- write_file 与 edit_file 的分工：`write_file` 整文件**覆盖**；`edit_file` **局部/追加**
- 首跑一次误报：中性问题修好后 4/4（判定器与实验设计要匹配）

---

## 本章三句话总结（自己写，勿抄）

1.
2.
3.

## 还没搞懂的问题

-
