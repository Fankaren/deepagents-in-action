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

## 待办 / 下一步

- [x] Step 1：盘点（task 默认在、general-purpose 同能力）
- [x] Step 2：首次委派（过程不可见 + 文件可见）
- [x] Step 3：隔离的账本（A 16533 vs B 8207 输入 tok；P3 全局账不可判定，可用 LangSmith 补测）
- [ ] Step 4：description 路由 + 隔离中的约束
- [ ] Step 5（选做）：协调者模式（ch04 × ch05）
- [ ] 收尾：`ch05-lab-summary.md` + 推送
