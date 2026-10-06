# Task 4 · 学习过程记录（ch04 任务规划）

> 惯例：每次会话收尾追加一节，三段式——做了什么 / 学到了什么 / 经验教训。
> 对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/>

---

## 会话 1 · 材料搭建 + Step 1（规划默认关）

**做了什么**
- 通读课程 ch04 原文，并在本机（deepagents 0.7.14 + langchain 1.4.0）核实 API：`TodoListMiddleware` 来自 `langchain.agents.middleware`（deepagents 包不再自带）；deepagents `graph.py` 默认中间件里没有它；`Todo` schema = `{content: str, status: "pending"|"in_progress"|"completed"}`；状态存 State 的 `todos` 键、文件存 `files` 键
- 搭建 `labs/ch04` 五步工作坊（step1~5 脚本 + WORKSHOP.md）与 `learning-notes/Task 4`（README + lab-journal 模板），提交 `2869484`
- 本机验证 Step1（纯内省，不调模型）：FS 工具 7/7 默认在，`write_todos` 不在

**学到了什么**
- **v0.7 规划不再默认开启**（实证）。同一个 `create_deep_agent`，不同能力默认档位不同：文件工具在默认层（Harness 的 Context Engineering 离不开它），规划在条件层（有代价，按需开）
- `TodoListMiddleware` 做三件事：注入 `write_todos` 工具 + `todos` 状态字段 + 规划引导提示词
- 规划提示词本身有代价：每次调用是一整轮模型推理，整表覆盖还重复带全量清单

**经验教训**
- 写实验脚本前先在本机版本核实签名——课程示例的 import 路径和包归属会随版本漂移
- 「对照组」设计（有无规划对照、摘要幸存）比单点演示更能回答「这个能力买到了什么」

---

## 会话 2 · Step 2（打开开关，首次看见流转）

**做了什么**
- 跑 `step2_enable_planning.py`：3 文件任务，押 C（多次调用、逐步流转）——中

**学到了什么**
- **接力棒节奏**：`write_todos → write_file → write_todos → …`，状态更新发生在两次实际工具之间；首次快照就把第 1 项标 in_progress（中间件引导词生效）
- `result['todos']` = 最后一次快照，**state 里没有历史**；查进度读 state，审计过程看消息轨迹里的快照序列
- completed 是 Agent 写的**标记**，`state['files']` 才是**证据**；两者这次恰好一致，但验收逻辑必须依赖后者
- FINAL 出现在最后一次 `write_todos` 之后——「最终答案不在 write_todos 同轮」也是被注入的纪律

**经验教训**
- 验收看产物（state），不听口头（FINAL）——ch03 教训在规划场景的直接复用

---

## 会话 3 · Step 3（生命周期 + 一个彩蛋）

**做了什么**
- 跑 `step3_todo_lifecycle.py`：4 步任务（写→写→edit_file→写汇报），三个预测（首次有 in_progress / 末次全 completed / 条目数不变）全中

**学到了什么**
- `edit_file` 被模型当成清单里的**独立一项**——「改」和「写」分开规划
- **彩蛋：`read_file` 混进序列**（`write_todos → read_file → edit_file`）：模型明明自己写的文件，编辑前仍先读回——`edit_file` 需要精确 `old_string`，模型选择 ground 在真实内容上而非信任记忆（ch03「读真数据」在模型侧的自觉版本）
- 计划稳定与否取决于任务有没有喂新信息：边界清晰的任务天然不修订；修订是**应急机制**不是标配（提示词写的是 "Don't be afraid to revise"——许可，不是义务）
- 本步 10 次工具调用中 5 次是 `write_todos`——**50% 开销买可观测性**

**经验教训**
- 没有「计划修订」≠ 运气好，可能是任务里没有意外

---

## 会话 4 · 概念问答（修订能力归属）+ Step 3b（陷阱实验）

**做了什么**
- 回答「报错后往清单加排查项」是模型能力还是 agent 侧优化 → 结论：三层合力（工具机制 × 提示词 × 模型判断），并给出可证伪实验
- 写并跑 `step3b_revision_on_error.py`：埋陷阱——先写单空格文件 `alpha beta`，再命令替换双空格 `alpha  beta` → `edit_file` 必然报错 String not found
- 实际结果：**「半 C 半 A」**——模型把失败原因改写进条目内容（`——失败：文件中是一个空格，匹配不到两个空格的字符串`，诊断完全正确），但条目数不变、没有重试、gamma 未替换却最终标了 completed

**学到了什么**
- 修订的真实形态是**内容级**的（改写条目如实记录失败），不只是数量级（增删条目）
- 提示词的修订要求有原文可查：`langchain/agents/middleware/todo.py` 默认 system prompt 含 "When blocked, create a new task describing what needs to be resolved"、"Never mark a task as completed if…errors"——**「会修订」是提示词的要求，不是模型天性**（需要长篇禁止「有错标 completed」恰恰证明这点）
- **spec-following vs intent-seeking 张力**：用户规格写明「两个空格」，模型选择如实上报差异而不是擅自改成单空格重试——「听话」压过了「办成事」
- **软约束会被合理解释绕开**：两道提示词禁令（我的 system_prompt + 中间件默认）都被突破；模型在「原任务失败」与「记录失败的任务完成了」之间滑动。程序侧验收（state['files'] 内容检查 gamma 不在）一票否决了 completed 标记
- 提示词每条禁令都是已知失败模式的补丁；模型能力是下限（诊断、取证都做了，只缺「带修正参数再试」一步）

**经验教训**
- **判定器也是预测，也会漏**：脚本判定器只盯条目数 +1，漏掉了内容级修订——观察清单要盯 diff，不能只数数
- prompt 是自觉、门禁要程序做：todos 给人看进度，产物验收永远在代码层
- 失败实验比顺利实验教得多：一个「四不像」结果一次演示了服从性张力、软约束漏洞、能力下限三个知识点

---

## 待办 / 下一步

- [ ] Step 4：有规划 vs 无规划对照实验（四个预测已押）
- [ ] 加餐 2（可选）：把陷阱改成「不指定空格数」——错误由环境造成而非用户规格，验证归因（预期 A→B）
- [ ] 加餐 3（可选）：`switch_model.py` 换更强模型重跑 step3b，验证「模型能力是变量」
- [ ] Step 5（选做）：摘要压缩后 todos 幸存
- [ ] 收尾：`ch04-lab-summary.md`（提交主文档）+ 推送
