# Task 7 · ch07 Skills —— 实验小结

**对应课程**：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/>
**环境基线**：deepagents 0.7.14（无需起服务，回到轻量模式）/ 日日新 `glm-5.2`
**实验方法**：四拍工作坊 + 判定器体检 + **金丝雀探针**（本章新增：只存在于正文的字符串）+ 请求级 callback 仪器
**材料**：`D:\agent_study\labs\ch07\`（workspace/skills/ 两个真磁盘技能 + step1~4 + WORKSHOP.md）；过程日志 `progress-log.md`（5 会话）

---

## 一、实验总览与实测结果

| Step | 问题 | 预测 vs 实测 | 关键证据 |
|------|------|--------------|----------|
| 1 | 启动时系统提示进了什么 | P1✓ P2✗（押 stuffing）P3✓ | 对照组请求 13 字符 vs 实验组 **2278**；两技能的 name+description+读取指引在请求里，**正文标记 SKILL-LOADED 零出现**= L1 只发菜单 |
| 2 | 正文何时进场 | P1✓ P2✓ P3 比预测更好（全守） | 序列 `read_file(/skills/report-writer/SKILL.md)`；FINAL 第一行精确 `SKILL-LOADED: report-writer`；结论先行/数字原样/85 字≤120 |
| 3 | 糊描述会怎样 | P1✓ P2✗（误召回实锤）P3✓ | 任务 A 读 report-writer **+ 误读 general-helper**；任务 B 零召回 |
| 3 改一处 | 改两行 description 再跑 | 精确翻转 | 任务 A 只读 report-writer（误召回消失）；任务 B 读 general-helper（**正召回**）——脚本判定器标签过时 |
| 4 | 只读知识库 | P1✓ P2✓ P3 用户✓我✗ | 写被拒（工具层硬拒绝）；读正常；**delete 也被拦**——`delete: "write"` 映射 |

---

## 二、知识主线（实测支撑）

### 1. 三级渐进披露（Level 1 的代价被量化）

| 级别 | 时机 | 进入上下文的东西 |
|------|------|------------------|
| L1 | 启动时 | 只有 name + description（两技能 2265 字符，随技能数**线性增长**） |
| L2 | description 命中后 | 正文，经 `read_file`（**模型自主决策**，用户不必要求） |
| L3 | 正文引用时 | references / assets |

- 注入的清单自带**操作纪律**：`-> Read /skills/xxx/SKILL.md` 指引 + 「read_file 传 limit=1000，默认 100 行会截断大多数技能文件」——中间件把实现层的坑写进了给模型的说明书
- L1/L2 的判定靠**金丝雀**：`SKILL-LOADED` 只在正文出现——不在提示里（L1 只发菜单）却出现在 FINAL 第一行（L2 读过并执行了纪律），一进一出完成证明

### 2. description：路由信号的三重身份

- **召回依据**：具体 description（含触发词）→ 一次命中；ch05 子 agent 的 description 是同一设计模式
- **误召回源头**：糊描述（"A helpful skill for developers."）不给「不相关」信号 → 模型无法在清单层排除 → **只能读正文确认**（白付一次 read_file + 正文占上下文）
- **漏召回的坑**：该召回时不召回 = 能力浪费
- 两轮对照（本章最漂亮的实验）：糊描述 → 任务 A 误召回 + 任务 B 零召回；改两行（具体触发词 + `Do NOT use for...` 边界）→ 任务 A 精确排除、任务 B 正确召回。**description 是双向闸门，写法决定召回质量**

### 3. 权限：路径 × 操作类别（不是工具名）

```python
FilesystemOperation = Literal["read", "write"]   # 只有两类！
_DEFAULT_FS_TOOL_OPS = {write_file/edit_file/delete: "write", ls/read_file/glob/grep: "read"}
```

- **delete 属 write 类**——保护 `write` 即覆盖 write_file / edit_file / delete（ch03 旧笔记「记得同时保护 write/edit/delete」已勘误）
- **fail-open 隐患**：非法类别值（如 `"edit"`）静默接受——`Literal` 是类型提示不做运行时校验，类别写错不报错、权限静默失效
- 拒绝发生在**工具层**（ToolMessage 原文 `Error: permission denied for write ...`），与模型自觉无关（ch03 Step6 跨两章复现）

### 4. 两层之辨（pre02 伏笔兑现）

编码助手 skill（给 IDE 里的 AI 用，pre02 装的 langchain-dev-guide 等）与运行时 skill（给跑起来的 agent 用，本章）**同规范（agentskills.io）、不同消费者**；Skills/Memory/Tools 光谱：所有对话都要 → Memory；特定任务才要 → Skills；原子操作 → Tools。

---

## 三、方法论遗产

1. **金丝雀探针**：把「某段内容有没有进上下文/有没有生效」转化为「一个只在特定位置出现的字符串在不在」——可观测、判定成本≈0；同一金丝雀可多角色复用（测注入范围 / 测执行效果）
2. **观测点第三次现身**：`wrap_model_call` 注技能清单只改**模型请求**、不回写 graph state——result 里的 SystemMessage 永远是原版；仪器要拦在请求上（`on_chat_model_start`，自定义 handler 必须继承 `BaseCallbackHandler`）
3. **判定器版本化**：判定标签绑死实验设计——技能改好后「误召回」标签变成过期新闻（把正召回标成误召回）；改实验必须同步改判定
4. **源码优先于直觉**：枚举/映射类配置（权限类别、工具→操作映射）先 grep 源码合法值；凭工具名直觉推论（我）会输给查表的直觉（用户）
5. **配置 fail-open 检查**：类型提示不等于运行时校验；枚举值/类别拼写错误可能静默失效，安全相关配置必须实测生效
6. 猜错的预测照样有教学值：我的「delete 后门」概念错误 vs 用户「路径锁=全锁」的正确直觉，构成一组对照

---

## 四、与课程原文对应

| 工作坊 | 课程 ch07 知识点 |
|--------|------------------|
| Step 1 | SKILL.md 规范、Level 1 元数据注入、skills= 参数与三种 Backend |
| Step 2 | Progressive Disclosure 三级、正文按需 read |
| Step 3 | description 唯一路由依据、最佳实践 1（具体 + 触发条件） |
| Step 4 | 只读知识库（FilesystemPermission）、Composite 路由（扩展：操作类别映射与 fail-open） |
| 全章 | 两层 skill 规范统一、Skills vs Memory vs Tools 光谱 |

自测题见 `labs/ch07/WORKSHOP.md` 文末；逐会话过程记录见 `progress-log.md`。
