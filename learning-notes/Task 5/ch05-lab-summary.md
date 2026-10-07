# Task 5 · ch05 子 Agent 与上下文隔离 —— 实验小结

**对应课程**：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/>
**环境基线**：deepagents 0.7.14 / langchain 1.4.0 / 日日新 `glm-5.2`
**实验方法**：四拍工作坊 + 判定器体检 + 双仪器交叉验证（本机 callback × 云端 LangSmith）
**材料**：`D:\agent_study\labs\ch05\`（WORKSHOP.md + step1~5 + step3b）；过程日志 `progress-log.md`（8 会话）

---

## 一、实验总览与实测结果

| Step | 问题 | 预测 vs 实测 | 关键证据 |
|------|------|--------------|----------|
| 1 | task 默认在吗 | 1 个默认子 agent ✓ | task 属默认层（对照 ch04：规划属条件层）；general-purpose "has access to all tools as the main agent" |
| 2 | 委派后过程/文件去哪了 | P1 0 次 ✓、P2 会 ✓ | 主轨迹仅 `task`；inner.md 经 state 合并出现在主 `files`——**隔离的是对话，不是文件** |
| 3 | 隔离省谁的账 | P1 A 大✓ P2 都写✓ P3 不可判定 | 主上下文输入 A 16533 vs B 8207；全局账主账本看不见 |
| 3b | 本地子账本 | v1 仪器翻车→v2 三预测全 PASS | 子账 13144 ≈ LangSmith ~13.2k，**双仪器交叉验证一致**；B 全局 21347 > A 16533 |
| 4 | 路由与约束 | P1 summarizer ✓、P2 47 字 ✓ | description 驱动路由；子 agent 的 system_prompt 在隔离中独立生效 |
| 5 | 协调者模式 | P1/P3/P4 ✓、P2 分层判 | 串行编排（task 之间隔着 write_todos）；主轨迹 0 次 write_file/read_file——**主 agent 只是路由器** |

---

## 二、知识主线（实测支撑）

### 1. 隔离的机制

- **委派属默认层、规划属条件层**：两者都是每轮重付的固定税，但 task 描述 ~400 tok 换高确定性收益，规划提示词 ~1250 tok 且短任务纯亏
- 默认 general-purpose = 「另一个我」：同能力（整栈继承）、不同上下文（"stateless by default: sees only the prompt"）
- **边界流量清单**：进 = 一个 description（主 agent 自动完整打包任务规格——委派第一课：**prompt 就是子 agent 的整个世界**）；出 = 一份最终报告 + 文件改动（走 state 合并，不走消息）
- **隔离的是对话，不是文件**：共享 Backend 上数据可以完全绕开主 agent 在子 agent 间流动（Step 5：collector 写 → reporter 读，主上下文全程无数据经过）

### 2. 隔离的账（token 口径 vs 费用口径）

- 主账省一半：16533 → 8207（大文件全文只在子 agent 上下文）
- 全局反而多付：B 21347 > A 16533——**隔离是搬运上下文的成本，不是消除它**
- **并行委派被实测发现**：两次 task 同轮发出，子账孪生结构（2193/2193、4379/4379，2193+2186≈4379=一份文件）为证
- cache 精修 ch04b 固定税模型：全局 75% 输入走 cache 折扣价（子 agent #2 首轮 93% 命中共享栈前缀）——token 口径的差距在费用口径收窄，**两本账要分开记**

### 3. 继承规则（本机源码佐证）

| 能力 | general-purpose | 自定义子 agent |
|------|-----------------|----------------|
| tools（含 MCP） | 全部继承 | 默认继承；**显式指定 = 完全替换**（忘列 MCP 工具就静默消失） |
| middleware | 整栈继承 | 不继承（ch04 的 TodoListMiddleware 要自带） |
| skills | 随栈继承 | 不继承，`SubAgent.skills` 独立字段；`mode="fork"` 强制继承父 skills |
| system_prompt | 继承主 agent | 永不继承（必填） |

- **description 是自定义子 agent 的唯一路由信号**（继承的工具不会列进 task 描述）——动作导向 + 边界声明 + 关键约束
- 约束各归各的宪法：50 字规则只套住子 agent 报告，主 agent 的 FINAL 不受管

### 4. 编排判断（模型行为观察）

- 无依赖 → 并行（Step 3b：同轮两个 task）；有依赖 → 串行（Step 5：task 之间隔着 write_todos）——同一模型两种编排都对，"concurrently when their tasks are independent" 的 **when** 被读进去了
- 工作分解示例：委派读取（上下文重活）、自留轻活（写摘要）
- ch04 的 todos 锚点在多 agent 场景照常工作（协调者模式全程逐格翻转）

---

## 三、仪器与判定器全记录（本章方法论主遗产）

1. **观测点决定可见性**：usage 在每次 API 返回里都存在，隔离挡住的是「最终 state」这个观测点；换运行时拦截（父 callback 自动传给子 agent——源码明示）本地就能看到子账。云端 LangSmith 的定位是便利（零代码/树状全景/历史），不是唯一性
2. **双仪器交叉验证**：云端 trace 与本地 callback 独立得出一致子账（13144 ≈ 13.2k）——测量置信度的黄金标准
3. **仪器需要单测**：v1 提取层取错对象（usage 在 `generations[*].message.usage_metadata`，不在 LLMResult 顶层）静默记 0——构造检查 ≠ 运行时验证，**仪器要在花模型调用之前用假数据离线单测**
4. **荒谬值内建报警**：子账 −8291 这种物理不可能值应自动拒绝出结论，不能靠人眼
5. **验收条件从目标语句推导**（ch04 教训的延续）：本章又出现两次代理指标翻车——关键字验收被「甲文件」误报、关键词验收放过「三行 vs 一行」规格偏差；验收清单要有内容、规格（行数/格式/边界）两栏
6. **证言与物证**：模型 FINAL 自述「浓缩为一行」是主动交底，验收器没接住；子 agent 的报告也是 FINAL，物证永远是 state 检查

---

## 四、经验教训速查

- 委派 prompt 必须自带全部上下文（文件路径/要求/输出格式）
- 依赖任务串行、独立任务并行——模型会判断，但 description 里的依赖信息要写清
- 验收含规格维度，不只查关键词存在性
- 负账、记录数低于已知下界 = 仪器故障，先修仪器再谈结论
- 解析渲染文本按分段切，不猜格式；抄 trace 数据先问清「一个分支还是全部」

---

## 五、与课程原文对应

| 工作坊 | 课程 ch05 知识点 |
|--------|------------------|
| Step 1 | 默认 general-purpose、task 默认工具 |
| Step 2 | Context Quarantine（上下文隔离）、共享 Backend |
| Step 3 + 3b | token 节省收益、并行委派（扩展：三层账本、双仪器验证） |
| Step 4 | 自定义子 agent 字典形式、description 路由、隔离中的 system_prompt |
| Step 5 | 多子 Agent 协作（协调者模式）、规划×委派（扩展：依赖感知编排） |

自测题见 `labs/ch05/WORKSHOP.md` 文末；逐会话过程记录见 `progress-log.md`。
