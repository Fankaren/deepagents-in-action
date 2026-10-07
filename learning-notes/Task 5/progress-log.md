# Task 5 · 学习过程记录（ch05 子 Agent 与上下文隔离）

> 惯例：每次会话收尾追加一节，三段式——做了什么 / 学到了什么 / 经验教训。
> 对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/>

---

## 会话 1 · 材料搭建 + Step 1 盘点 + Step 2 首次委派

**做了什么**
- 抓取课程 ch05 原文，核实本机 0.7.14 实现：`task(description, subagent_type)`，返回值把子 agent 最终报告作为 ToolMessage 交给主 agent，并**把子 agent 的文件改动合并回主 state**；工具描述明示 "stateless by default: sees only the prompt"
- 搭建 `labs/ch05` 五步工作坊（step1 盘点零模型调用已验证；step2–5 构造检查通过），提交 `0f1cedf`
- 用户跑 Step 1（预测 1 个子 agent ✓：默认仅 general-purpose，描述 "has access to all tools as the main agent"）和 Step 2（P1 主轨迹 write_file 0 次 ✓、P2 inner.md 进主 state ✓）

**学到了什么**
- **委派属默认层、规划属条件层**——两者都是每轮重付的固定税，但税额与收益确定性不同：task 描述 ~400 tok 换「上下文不被污染」的高确定性收益；规划提示词 ~1250 tok 且短任务纯亏（ch04b 实测 3 倍 token）
- **隔离的是对话，不是文件**：主轨迹只见 `task`（子 agent 的 write_file 不可见），但文件经 state 合并直接出现在主 agent 的 `state['files']`
- 边界流量清单：进 = 一个 description（主 agent 自动完整重述任务规格——"sees only the prompt" 生效）；出 = 一份最终报告 + 文件改动（走 state 不走消息）
- 子 agent 报告自带「经读取验证」声明——它的自检中间调用也没越过边界；且子 agent 的报告也是 FINAL（证言），物证仍是 state 检查

**经验教训**
- 委派的第一课：**prompt 就是子 agent 的整个世界**——文件路径、要求、输出格式必须全部打包进 description
- 解析渲染出来的工具描述要按分段切，不能猜格式（正则一把梭又没奏效）

---

## 会话 2 · Step 3 隔离的账本（+ MCP/skill 继承规则问答）

**做了什么**
- 用户提问「子 Agent 能看到 MCP、skill 吗」→ 查本机源码作答：general-purpose 整栈继承（model/tools/middleware，skills 随栈），自定义子 agent 的 tools 默认继承但**显式指定完全替换**（MCP 工具忘列就静默消失）、middleware 与 skills 不继承（`SubAgent.skills` 独立字段）；彩蛋：`mode="fork"` 强制继承父 skills 且禁止自设
- 跑 Step 3（两份 80 行大文件，A 自己干 vs B 委派）：用户 P1 A 大✓、P2 都写✓、P3 **不可判定**

**学到了什么**
- **P1 坐实**：A 16533 vs B 8207 输入 tok（轮次都是 3）——差距全部来自大文件全文有没有进主上下文
- **B 组策略惊喜**：`task ×2 → 自己 write_file`——委派读取（上下文重活）、自己写轻活；「为什么两次 task」物证不足（脚本没打 task args，观察盲区）
- **P3 的测量边界**：隔离把中间过程藏起来的同时也把子 agent 的账单藏起来了——主账本天然看不见子账本；子 agent 运行带 `ls_agent_type=subagent` 标签，**LangSmith trace 是看子账的唯一窗口**（pre02 技能的用武之地）
- 隔离省的是**主上下文预算**（对话还能继续多长），不是总花费（子 agent 自己也要读大文件）

**经验教训**
- **判定器第 4 次误报（我方）**：A 组验收用 `'文件' not in sum_text` 当检查条件，被摘要里合法的「甲文件」撞上误报 MISS——验收条件只能从目标语句推导，关键字代理指标已经是第四次被咬
- 委派 prompt 的禁令范围要写准：只禁 read_file 不禁 write_file，模型才能正确分解「外包重活、自留轻活」

---

## 会话 3 · LangSmith 补测 P3（全局账结案）

**做了什么**
- 用户去 LangSmith 抄回子 agent 的模型调用账：输入 2.191k（cache_read 2.048k）+ 4.377k（cache_read 2.376k）
- 合账判定 P3：B 全局 ≈ 8.2k(主) + 2×6.57k(子) ≈ 21.3k > A 16.5k → **用户原预测「B 大」正确**（待核对：两次调用属一个子 agent 分支还是两个，另一分支应有对称的一对）

**学到了什么**
- **P3 结案**：隔离省了主上下文一半的账（16533→8207），但子 agent 把读大文件的成本原样再付一遍，全局反而多 ~5k——「隔离是搬运上下文的成本，不是消除它」
- **cache_read 修正了 ch04b 的固定税模型**：两个子 agent 共享同一段 Harness 栈（system+工具定义），prompt cache 对重复前缀打折——「固定税×轮次」作为 token 量成立，计费口径下有折扣券；账本要分 token 口径与费用口径两本
- **完整账本 = 本机主账 + 云端 trace**：主账本天然看不见子账本（隔离把成本也藏了），跨工具取证才能结案；pre02 的 LangSmith 技能在 ch05 第一次成为必需品而非可选项

**经验教训**
- 子 agent 运行带 `ls_agent_type=subagent` 标签——trace 树就是组织架构图，量谁的账就展开谁的分支
- 用户抄回的数据先问清「这是全部分支还是一个分支」再合账（假设要写明才能被核对）

---

## 会话 4 · 观测点修正（用户推翻「必须云端 trace」）

**做了什么**
- 用户质疑「为什么一定要云端 trace，token/cache 不都在 API 返回里吗」——成立，我上一轮的「LangSmith 是唯一窗口」是过度声称
- 交付本地方案 `step3b_sub_ledger_local.py`：`UsageMetadataCallbackHandler` 子类逐调用记账，父 callback 自动传给子 agent（源码 task() 注释为证），主账从 result 消息求和，**子账 = callback 总账 − 主账**（减法拆分，无需区分调用归属），本地复算 P3

**学到了什么**
- usage 确实在每次 API 返回里；看不见子 agent 的账不是数据不存在，是**观测点**选错——最终 state 被隔离挡住，运行时拦截（本地 callback / stream subgraphs）则畅通
- LangSmith 的真实定位重新校准：不是唯一性，是便利性（零代码、树状全景、历史留存、可分享）；本地 callback 的优势是数据不出机器、可编程接入判定器
- 减法拆分是治理「调用归属不明」的通用技巧：总账好记、主账好记，中间量做差

**经验教训**
- 「唯一窗口」这类绝对化表述要当场自检——观测点换了，结论就翻；和「验收条件从目标语句推导」同族：**观测条件要从测量目标推导**
- 用户对测量方案的质疑和判定上诉同权——两次推翻都来自用户，说明「被质疑的应该是测量者」是常态

---

## 待办 / 下一步

- [x] Step 1：盘点（task 默认在、general-purpose 同能力）
- [x] Step 2：首次委派（过程不可见 + 文件可见）
- [x] Step 3：隔离的账本（A 16533 vs B 8207 输入 tok；P3 已由 LangSmith 补测结案：全局 B 大）
- [ ] Step 4：description 路由 + 隔离中的约束
- [x] Step 3b：本地子账本（callback 运行时拦截，子账=总-主）——待用户跑
- [ ] Step 5（选做）：协调者模式（ch04 × ch05）
- [ ] 收尾：`ch05-lab-summary.md` + 推送
