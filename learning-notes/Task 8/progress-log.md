# Task 8 · 学习过程记录（ch08 长期记忆）

> 惯例：每个 Step 收尾按三段式记录——**做了什么 / 学到什么 / 遇到什么问题**（参考 Task 4–7 的 progress-log）。
> 对应课程：https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/
> 预测题见 `predictions.md`；逐步预测表见 `lab-journal.md`。

---

## 会话 0 · 材料搭建（labs/ch08 + Task 8 模板）

**做了什么**
- 抓取课程 ch08 原文，梳理知识主线：Checkpointer（短期）vs Store（长期）、CompositeBackend 路径路由、三种作用域、`memory=` 读取语义、外部预填
- 搭建 `labs/ch08`：`_common.py`（RequestCapture / Judge / namespace 兜底 / build_model）+ step0 仪器单测 + step1~4 实验脚本 + WORKSHOP.md
- 建立 Task 8 模板：README / lab-journal / predictions / progress-log / 小结（待跑）
- 模型接入从硅基流动切换为**商汤日日新** `glm-5.2`（OpenAI 兼容）；实测连通与工具调用均 OK

**学到什么**
- 记忆的观测点与 Skills 一致：注入发生在**模型请求**，不回写 state → 仪器拦在请求上
- ch08 的证据要**分两处看**：写入压 Store（`store.get`），加载压请求文本——这是「模型说记住≠真记住」的判定方法
- `memory=`（文件路径列表）与 `skills=`（目录列表）参数类型不同，是最易混淆的一对
- `glm-5.2` 是推理模型：返回 `reasoning_content`，`max_tokens` 过小会全被推理吃掉、`content` 为空

**遇到什么问题**
- 本机 `git clone` 走代理（127.0.0.1:10808）失败 → 改用 GitHub API / raw 抓内容
- `D:\agent_study` 在本机不存在 → labs 放在当前工作区；原仓库 labs 需自行搬迁
- 本机未装 `deepagents`（执行前需 `pip install "deepagents>=0.7.10" langchain-openai`）

---

## 逐 Step 记录（三段式）

> 每跑完一个 Step，复制下面模板填一节；判定器 `PASS/FAIL` 与实际现象一起记。

### Step 0 · 仪器单测 + 判定器体检

**做了什么**
- 先作答预测题：Q0-1=A、Q0-2=B、Q0-3=B
- 运行 `python step0_selftest.py`（**零模型调用**）：判定器 **9/9 PASS**
- 复核发现「三题全中」的记法有问题 → 给 step0 补一个**负样本**（不继承 `BaseCallbackHandler` 的裸对象当 callback），实测抛 `AttributeError`；判定器增至 **10/10 PASS**

**学到什么**
- **区分「知识预测」与「实测预测」**：
  - Q0-1 由 step0 **实测**（通过率）；
  - Q0-3 原来只是正向断言（`issubclass==True`），**不能证伪** → 加负样本后才成为实测题；
  - Q0-2 是**知识题**，step0 只能证明「B 这种观测点可实现」，不能证明 A/C 是错的——真正的判别证据在 **Step 4-B**（金丝雀在请求里、**不在** `result["messages"]` 里）
- 一次「误报全中」的教训：把知识题记成实测题，就是 ch07 说的**判定标签与判定条件脱节**
- 负样本把判定器从「能跑通」升级为「能区分对错」

**遇到什么问题**
- 原 step0 只有正向断言、缺负样本，Q0-3 不可证伪（已修：9 项 → 10 项）
- 预期报错的 `AttributeError` 会被 langchain 记 error 日志；已在负样本处临时 `logging.disable` 压掉，保持输出干净
- 无模型额度消耗

### Step 1 · 跨线程记忆闭环

**做了什么**
- 预测 Q1-1~Q1-4 全 A（启动加载金丝雀 / Store 含偏好且金丝雀保留 / 新线程请求含偏好 / 回答守约）
- 运行 `python step1_cross_thread.py`：判定器 **5/5 PASS**
- thread A=`906bd541-…` 写入偏好；thread B=`10762e6a-…`（全新 `thread_id`）读取并使用

**学到什么**
- **跨线程闭环成立**：同一 Store + 同一 user namespace，换 `thread_id` 仍能加载到偏好；thread B 的排序函数确实按「中文注释 / 英文变量名」输出（观察项兑现）
- **双证据链兑现**：写入压 `store.get`（content=两条偏好），加载压**请求文本**（thread B 的 system 提示含偏好）——与「模型口头说已记住」彻底分离
- **edit_file 实测**：写入后文件为「两条偏好 + 保留的金丝雀注释 `<!-- MEM-CANARY-LOAD-7f3a91 -->`」→ 模型走的是局部修改，不是整文件覆盖

**遇到什么问题**
- 无报错
- 观察项待记：thread B 把代码写到 `/home/user/sort.py`（StateBackend **线程内**路径），换线程即失效——与「长期记忆」无关，别混淆
- Q1-2 的「金丝雀保留」依赖模型选 `edit_file` + 提示词强调「保留其他条目」，属**行为依赖项**，非框架保证

### Step 2 · 作用域（隔离 / 共享）

**做了什么**
- 预测：Q2-1=A、Q2-2=C、Q2-3=A
- 首次运行撞 429 `rpm exhausted`（见「遇到什么问题」）；加限速+重试后重跑 `step2_scopes.py`：判定器 **7/7 PASS**

**学到什么**
- **Q2-2 预测错（C→A）是本章题眼**：agent-scoped 是**故意跨用户共享**的——namespace 固定 `(assistant_id,)`，不掺 `user_id`，所以 A、B 看到同一份 `SHARED-AGENT-77`。押「都看不到」是把「不隔离」误当成了「都不共享」
- user-scoped 隔离实锤：A 的请求不含 B 金丝雀、B 的反之 → `(user_id, 'memories')` 真隔离
- 作用域选错的两个方向：掺了 user_id = 隐私泄露；该共享却按用户隔离 = 知识不共享
- 一句话：**作用域 = namespace 的写法**（`(user_id,)` 隔离 / `(assistant_id,)` 共享 / `(org_id,)` 组织级）

**遇到什么问题**
- 上一轮的 429 已由 `CH08_CALL_INTERVAL` + 退避重试修复，本次顺利跑完
- 小观察：脚本只断言请求、不打印模型回答；如需看回答可加打印（可选改进）

### Step 3 · CompositeBackend 路由

**做了什么**
- 预测：Q3-1=A、Q3-2=A、Q3-3=B、Q3-4=A
- 运行 `step3_routing.py`：判定器 **4/4 PASS**

**学到什么**
- **Q3-3 预测错（B→A）**：`StateBackend` 的文件是**线程内**的——thread1 `files keys=['/workspace/route-scratch.md']`，thread2 `files keys=[]`，workspace 文件随线程消失。押「写进 state 就一直在」是把 Checkpointer 的「线程内持久」误当成了「全局持久」
- **路由实锤**：`/memories/route-note.md` 落 Store（`store.get` content=`ROUTE-MEM-1123`）；`/workspace/route-scratch.md` 落 thread1 的 `state.files`
- **模型侧零感知**：同一套 `write_file`/`read_file`，前缀不同 → 新线程里 `/memories/` 读得到、`/workspace/` 报 `not found`
- 一句话：**Composite = 按 path 前缀选 Backend，前缀决定「活多久」**

**遇到什么问题**
- 无（限速生效）
- 观察项符合预期：对同一个文件，不可能同时既在 Store 又在 state.files

### Step 4 · 初始化 / 缺失文件 / 覆盖

**做了什么**
- 预测：Q4-1=B（不会创建）、Q4-2=B（不会注入）、Q4-3=A（会）、Q4-4=保留 —— **全对**
- 首跑 `step4_init_missing.py`：判定器 3/4，Q0-2 判别误报 FAIL（判定器设计失误，见下）
- 修 B 组为**中性问题** + 打印「命中角色」做诊断后重跑：判定器 **4/4 PASS**，`result 命中角色=无`

**学到什么**
- `memory=` 只声明**读取**：缺失文件**跳过、不创建、不注入**（A 组 2 项 PASS）
- 外部预填 `store.put(ns, key, create_file_data(...))` 生效 → 金丝雀进入新线程请求（B 组）
- **Q0-2 实证兑现**：金丝雀在请求里、`result["messages"]` 命中角色=无 → memory 注入是**请求级、不回写 state**（与 ch07 观测点一致）
- `edit_file` 追加 vs `write_file` 覆盖：C 组写入后三条偏好齐全（前两条保留）→ 模型走 `edit_file`；覆盖风险由提示词「保留已有条目」规避

**遇到什么问题**
- **判定器误报**：B 组原问题「请说明你记得什么」**诱导模型复述金丝雀**，使其合法出现在 assistant 消息里，被判成「注入回写 state」→ 误报 FAIL
- 修法：改用中性问题，并打印金丝雀命中的消息**角色**，用于区分「框架回写」还是「模型复述」
- 教训（ch07 遗产复现）：**判定器必须与实验设计匹配**；金丝雀出现在 result，要先问「是谁写进去的」

---

## 待办 / 下一步

- [x] 预测：在 `predictions.md` 作答（Step 0 已作，A/B/B）
- [x] Step 0：仪器单测 + 判定器体检（零模型调用，10/10 PASS）
- [x] Step 1：跨线程闭环（thread A 写 → Store 断言 → thread B 加载，5/5 PASS）
- [x] Step 2：作用域（user-scoped 隔离 / agent-scoped 共享，7/7 PASS；Q2-2 预测错=C→实际A）
- [x] Step 3：CompositeBackend 路由（持久 vs 线程内，4/4 PASS；Q3-3 预测错=B→实际A）
- [x] Step 4：缺失文件 / 外部预填 / 覆盖 vs 追加（4/4 PASS；首跑误报1项已修）
- [x] 收尾：`ch08-lab-summary.md` + 推送
