# Task 8 · ch08 长期记忆 —— 实验小结

**对应课程**：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/>
**环境基线**：deepagents 0.7.x（无需起服务，轻量模式）/ 商汤日日新 `glm-5.2`（OpenAI 兼容）
**实验方法**：四拍工作坊 + 判定器体检 + **金丝雀探针** + 请求级 callback 仪器
**材料**：`labs/ch08/`（`_common.py` + step0~4 + WORKSHOP.md）；过程日志 `progress-log.md`

---

## 一、实验总览与实测结果

| Step | 问题 | 预测 vs 实测 | 关键证据 |
|------|------|--------------|----------|
| 0 | 仪器可信吗 | Q0-1/0-3 实测全中；Q0-2 属知识题，留 Step 4 实证 | 判定器 10/10 PASS；负样本（裸 callback）实测抛 `AttributeError` |
| 1 | 换线程还记得吗 | Q1-1~4 **全中** | thread A 请求含金丝雀 + `store.get` 有两条偏好（金丝雀保留）+ thread B 请求含偏好；**5/5** |
| 2 | 作用域隔离/共享 | Q2-1/3 中、**Q2-2 错（C→A）** | A/B 各只见自己金丝雀；agent-scoped 两用户同见 `SHARED-AGENT-77`；**7/7** |
| 3 | 前缀决定活多久 | Q3-1/2/4 中、**Q3-3 错（B→A）** | `/memories/` 落 Store、`/workspace/` 落 thread1 `state.files`、thread2 `files=[]`；**4/4** |
| 4 | 缺失/预填/覆盖 | Q4-1~4 **全中**；首跑误报 1 项（判定器缺陷） | 缺失不创建不注入；预填进请求；金丝雀不在 result；`edit_file` 保留；**4/4** |

**预测命中**：Q0-1、Q0-3、Q1-1~4、Q2-1、Q2-3、Q3-1/2/4、Q4-1~4；**押错 2 题**：Q2-2（agent-scoped 共享）、Q3-3（state 线程内）。

---

## 二、知识主线（实测支撑）

### 1. 两种记忆：Checkpointer vs Store

| | 短期（Thread-scoped） | 长期（Cross-thread） |
|---|---|---|
| 机制 | Checkpointer | Store + `StoreBackend` |
| 落地 | State（`files` 字段） | namespace + key |
| 换 `thread_id` | 消失（Step 3：thread2 `files=[]`） | 仍在（Step 1/3） |

- Step 1 铁证：thread A 写入后，**全新** thread B 的请求里出现已保存偏好，且回答守约
- 验证要**分两处看**：写入压 `store.get`，加载压请求文本；「模型说已记住」不作数

### 2. 三种作用域（namespace 决定谁能看）

| 作用域 | namespace | Step 2 实测 |
|--------|-----------|-------------|
| 用户级 | `(user_id, 'memories')` | A、B 互不可见（隔离）|
| Agent 级 | `(assistant_id, 'memories')` | A、B **都**看到同一份共享知识 |
| 组织级 | `(org_id,)` | 通常只读（本章未跑，见 ch11）|

- **易错点（Q2-2）**：agent-scoped「不隔离」≠「都不共享」——它是**故意**跨用户共享的

### 3. CompositeBackend 路由

```text
/memories/**  → StoreBackend     （跨线程持久）
/workspace/** → StateBackend     （线程内）
其余          → default(=State)
```

- Step 3 实测：同一套 `write_file`/`read_file`，前缀不同 → 新线程里 `/memories/` 读得到、`/workspace/` 报 `not found`
- 路由前缀会被**去掉**再作为 Store key；直接挂 `StoreBackend` 则保留完整虚拟路径

### 4. `memory=` 的读取语义与写入约定

- `memory=` 是**读取配置**：缺失文件**跳过、不创建、不注入**（Step 4-A 实测）
- 写入位置靠 `system_prompt` + 工具约定；仅声明 `memory=` 不保证 Agent 用它
- 追加/局部修订用 `edit_file`，`write_file` 是**整文件覆盖**（Step 4-C：三条偏好齐全）
- 外部预填用 `store.put` + `create_file_data`，不要手写底层 JSON

---

## 三、方法论遗产（本章新增 / 复现）

1. **区分「知识预测」与「实测预测」**：Q0-2（观测点）step0 无法证伪，真正的判别证据在 Step 4-B；把知识题当实测题记账 = 判定标签与条件脱节
2. **判定器必须与实验设计匹配**：Step 4 首跑误报——「说明你记得什么」诱导模型**复述**金丝雀，被误判成「注入回写 state」。改用中性问题 + 打印命中**角色**即可区分「框架回写」vs「模型复述」
3. **金丝雀 + 请求级仪器**：`RequestCapture(BaseCallbackHandler).on_chat_model_start` 拦模型请求；memory 注入**不回写 state**
4. **负样本才有证伪力**：step0 加上「裸对象当 callback」负样本，Q0-3 才从「能跑通」升级为「能区分对错」
5. **限速自愈**：日日新 429 `rpm exhausted` → `run()` 加调用间隔 + 线性退避重试（`CH08_CALL_INTERVAL/RETRIES/RETRY_WAIT`），Step 2 起零阻塞

---

## 四、与课程原文对应

| 工作坊 | 课程 ch08 知识点 |
|--------|------------------|
| Step 1 | Checkpointer vs Store、跨对话访问、`create_file_data` 预置 |
| Step 2 | 三种作用域、namespace 兜底 |
| Step 3 | CompositeBackend 路径路由、StateBackend vs StoreBackend |
| Step 4 | `memory=` 读取语义、缺失文件跳过、外部预填、覆盖 vs 追加 |

自测题见 `labs/ch08/WORKSHOP.md` 文末；逐会话过程记录见 `progress-log.md`；预测题与解析见 `predictions.md`。
