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

## 待办 / 下一步

- [x] 材料搭建 + step1 验证通过（v3）
- [ ] Step 1：用户跑（预测已在脚本头）
- [ ] Step 2：渐进披露实测（read_file + SKILL-LOADED 纪律）
- [ ] Step 3：description 路由（好描述 vs 糊描述）
- [ ] Step 4（选做）：只读知识库
- [ ] 收尾：ch07-lab-summary.md + 推送
