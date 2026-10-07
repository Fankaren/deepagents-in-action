# Task 7 · ch07 Skills（可复用能力包 / SkillsMiddleware）

对应课程：<https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/>

## 怎么学

沿用四拍工作坊 + 判定器体检。**无需起服务**（回到 ch03-05 的轻量模式）。技能是**真磁盘文件**（FilesystemBackend root = `labs/ch07/workspace`，接 ch03 的地气），用户可直接 `cat` 查看。

## 材料清单

| 文件 | 说明 |
|------|------|
| `lab-journal.md` | 实验日志模板 |
| `progress-log.md` | 会话过程记录 |
| `ch07-lab-summary.md` | **实测小结（提交主文档，已完成）** |
| `labs/ch07/workspace/skills/report-writer/SKILL.md` | 正样本：description 具体 + 正文含观测标记 SKILL-LOADED |
| `labs/ch07/workspace/skills/general-helper/SKILL.md` | 负样本：模糊 description（"A helpful skill."） |
| `labs/ch07/step1_level1_probe.py` | Level 1 现场：系统提示只有元数据没正文（含无技能对照） |
| `labs/ch07/step2_progressive.py` | 渐进披露：description 命中 → read_file 正文 → 纪律生效 |
| `labs/ch07/step3_routing.py` | description 路由：召回/误召回/零召回 |
| `labs/ch07/step4_readonly.py` | 选做：FilesystemPermission deny 写 /skills/**（只读知识库） |

## 本机版本基线

- deepagents 0.7.14：SkillsMiddleware（`middleware/skills.py`，1058 行）；`skills=["/skills/"]` 路径相对 Backend 根；name 须与父目录同名（1-64 字符小写连字符）；description ≤1024 字符且为唯一路由信号；同名技能 last wins
- 三级渐进披露：L1 元数据进系统提示（`append_to_system_message`）/ L2 正文经 read_file / L3 资源再按需
- pre02 装的编码助手 skills（`research_deepagent\.agents\skills\`）与本章运行时 skills 同规范、不同消费者——「两层之辨」在本章兑现

（2026-10 收官：Step 1–4 + 改一处翻转全部完成，见 ch07-lab-summary.md）
