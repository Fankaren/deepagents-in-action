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

## 待办 / 下一步

- [x] Step 1：盘点（task 默认在、general-purpose 同能力）
- [x] Step 2：首次委派（过程不可见 + 文件可见）
- [ ] Step 3：隔离的账本（主上下文账 vs 全局账）
- [ ] Step 4：description 路由 + 隔离中的约束
- [ ] Step 5（选做）：协调者模式（ch04 × ch05）
- [ ] 收尾：`ch05-lab-summary.md` + 推送
