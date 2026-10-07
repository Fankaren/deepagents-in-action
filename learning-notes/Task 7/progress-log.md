# Task 7 · 学习过程记录（ch07 Skills）

> 惯例：每次会话收尾追加一节，三段式——做了什么 / 学到了什么 / 经验教训。
> 对应课程：https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/

---

## 会话 1 · 材料搭建 + Step1 仪器两连修

**做了什么**
- 抓取课程 ch07 原文，核实本机 middleware/skills.py（1058 行）：SKILL.md frontmatter 规范（name 与父目录同名、description 不超 1024 且唯一路由）、wrap_model_call 里 append_to_system_message 注入清单
- 搭建 labs/ch07：两个真磁盘技能（report-writer 正样本 + general-helper 模糊负样本）+ 4 个实验脚本 + WORKSHOP + Task 7 模板；回到无服务轻量模式
- **step1 仪器两连修后跑通**：v1 读 result 里的 SystemMessage，什么都没有（观测点错：清单在 wrap_model_call 的 request 里，不回写 state）；v2 自定义 callback 没继承 BaseCallbackHandler，AttributeError；v3（RequestCapture(BaseCallbackHandler) + on_chat_model_start 拦截真请求）跑通：**对照组 13 字符 vs 实验组 2278 字符**，两个技能的 name+description+读取指引全在请求里，正文标记 SKILL-LOADED 不在——渐进披露 L1 实锤

**学到了什么**
- **L1 的确切代价**：两个技能 2265 字符（随技能数线性增长）；清单里每个技能带「Read /skills/xxx/SKILL.md」读取指引
- **注入的清单自带操作纪律**：包括「read_file 要传 limit=1000，默认 100 行会截断大多数技能文件」——中间件把实现层的坑直接写进了给模型的说明书
- **观测点教训第三次现身**：wrap_model_call 改的是模型请求，不是 graph state——result 里的 SystemMessage 永远是原版
- 多源预告：清单里出现「Sources labeled Deepagents vs Agents（本机所有 agent 工具共享）」——技能注册表的跨工具视角

**经验教训**
- 自定义 callback handler 必须继承 BaseCallbackHandler（回调管理器依赖 raise_error 等属性）
- 观测点自检要写清两边各是什么（state 字符数 vs 请求字符数），别让判定标签和条件脱节
- shell heredoc 传中文长文本会被截断——写文件用 Write 工具，不赌 shell 的引号处理



---

## 会话 2 · Step 1+2 对答案（渐进披露闭环）

**做了什么**
- 用户跑 step1：P1 元数据进请求 ✓、P2 押 stuffing 错（SKILL-LOADED 不在 2278 字符请求里）、P3 对照组干净 ✓；观测点自检兑现（state 18 字符 vs 请求 2278）
- 用户跑 step2：P1 read_file(/skills/report-writer/SKILL.md) ✓、P2 FINAL 第一行精确命中 ✓、P3 全守（结论先行/数字原样/三行/85 字≤120——比用户「大部分」和我「字数可能超」的预测都好）

**学到了什么**
- **金丝雀双角色**：SKILL-LOADED 没进提示（L1 只发菜单）却出现在 FINAL 第一行（L2 读过正文并执行纪律）——一进一出证明「正文是读进来的」
- L2 的 read_file 是模型**自主决策**（用户没要求读文件）——「按需」的「按」是模型判断
- 渐进披露闭环：菜单进请求 → description 匹配 → 正文按需进场 → 纪律生效，两步实验全部有物证

**经验教训**
- 用户 P2 押 stuffing 是大众直觉——「装了=全塞」正是渐进披露要消灭的做法；数字反证（SKILL-LOADED 零出现）比讲道理有力
- 小观察待办：清单教的 limit=1000 模型听没听，需打印 args 或看 trace（脚本只打了路径）



---

## 会话 3 · Step 3 两轮对照（糊描述误召回实锤 + 两行改动精确翻转）

**做了什么**
- 第一轮（糊描述）：任务 A 读 report-writer + **误读 general-helper**（P2 押「不会」错——误召回实锤）；任务 B 零召回 ✓
- 用户改 general-helper 的 description（具体触发词 + Do NOT 边界）重跑：任务 A 只读 report-writer（误召回消失）、任务 B 读 general-helper——**脚本判「误召回」，实为正召回**

**学到了什么**
- **糊 description 的代价被量化**：不提供「不相关」信号 → 模型无法在清单层排除 → 只能读正文确认 → 每次白付一次 read_file 往返 + 正文占上下文
- **两行改动同时修好两件事**：误召回消失（A 组）+ 该召回时召回（B 组）——description 是双向闸门
- 与 ch05 合并成同一设计原则：路由信号（子 agent description / skill description）的写法决定召回质量
- **判定器标签绑死实验设计**：实验改了（技能变好），判定器的「误召回」标签就成过期新闻——改实验必须同步改判定

**经验教训**
- 判定器不仅要体检，还要随实验设计**版本化**——这次脚本把正召回标成了误召回，是判定器过时不是模型错了
- 改一处再跑的第四拍在这一章威力最大：两行 YAML 换来路由行为的精确翻转



---

## 会话 4 · Step 4 只读知识库（P3 埋了 delete 后门）

**做了什么**
- 用户跑 step4：P1 新建被拒 ✓（`Error: permission denied for write on /skills/my-skill/SKILL.md`）、P2 读正常 ✓（返回前两行 + v0.7 分页标记，模型精确执行「读开头两行」）
- P3（delete 会不会被拦）留作改一处实测——脚本权限配置只有 `operations=["write", "edit"]`，**delete 未列**

**学到了什么**
- 权限在**工具层**硬拒绝（ToolMessage 原文即 `permission denied`），模型没有「自觉不写」的机会——ch03 Step6 结论跨两章复现
- **权限粒度 = 路径 × 操作的乘积**：锁了路径不等于锁了全部操作；漏一个操作就是一个后门（ch03 原话「自定义策略记得同时保护 write/edit/delete」——这次由我自己的脚本验证了它多容易忘）
- 只读知识库的产品形态：CompositeBackend 路由（共享 /skills/ 只读 + 个人空间可写）

**经验教训**
- 写权限配置时应以「操作清单对照表」逐项核对（write/edit/delete），不凭记忆写两三行完事
- 埋陷阱（delete 未锁）与疏忽（同一条配置）这次是同一个东西——好在它变成了实验素材

---

## 待办 / 下一步

- [x] 材料搭建 + step1 验证通过（v3）
- [x] Step 1：L1 实锤（13 vs 2278 字符；用户 P2 押 stuffing 错即题眼）
- [x] Step 2：渐进披露闭环（read_file 精确命中 + 全纪律遵守）
- [ ] Step 2：渐进披露实测（read_file + SKILL-LOADED 纪律）
- [x] Step 3：两轮对照——糊描述误召回实锤，改两行 description 后路由精确翻转（含判定器过时教训）
- [x] Step 4：只读知识库（写被拒 ✓ 读正常 ✓；delete 未锁待改一处实测）
- [ ] 收尾：ch07-lab-summary.md + 推送
