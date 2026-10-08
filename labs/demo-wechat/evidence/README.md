# 证据备份（Evidence）· 实测快照

本目录是 `labs/demo-wechat` 一次真实运行的**测试数据备份**，用于佐证 Demo 端到端可用
（对应 `WORKSHOP.md` 的 Step 0–3）。运行日期：**2026-10-08**，模型：商汤日日新 `glm-5.2`。

## 内容

| 路径 | 内容 | 佐证什么 |
|------|------|----------|
| `drafts/*.md` | 主编生成的终稿（按 SKILL 骨架的体系化长文）| Skills 统一格式 + 篇幅/时长纪律达标；子 Agent 配图（免费图床 URL）|
| `memory/content-strategy.md` | 锁定方向 + 4 系列（`set-direction` 写入）| 需求①：方向锁定 |
| `memory/content-plan.md` | 系列选题库，已发布选题标记 | 需求①：体系化推进 |
| `memory/knowledge-base.md` | 三个系列累积的框架/金句 | 需求①：知识沉淀（跨篇复用）|
| `memory/performance.md` | 阅读量台账（`memory_cli record` 写入）| 需求②：数据留痕 |
| `memory/topic-ledger.md` | 已发选题去重台账 | HITL 审批通过后应用侧写入 |
| `store.snapshot.json` | **持久化 Store 完整快照**（`InMemoryStore` 子类落盘格式）| ch08 跨天记忆：关掉重开仍在 |

## 怎么复现这份证据

```powershell
start_env.bat demo-wechat
python step0_selftest.py                                   # 21/21
python memory_cli.py set-direction "主方向：男性成长与效率；系列：《底层逻辑》《习惯复利》《决策工具箱》《认知升级》"
python run_daily.py --auto-approve                         # 生成一篇 + 沉淀记忆
python memory_cli.py record --series 底层逻辑 --title "..." --reads 3200 --likes 120 --finish 0.42
python run_daily.py --auto-approve                         # 跨天：读 performance、推进下一系列
```

## 说明
- 本目录是**清理后的备份**（已移除并发保存的 `*.tmp`、统一了台账格式、去掉演示用的占位标题）。
- live 运行态（`workspace/.state/`、`workspace/drafts/`）不入库，用 `.gitignore` 排除；正式产物以本目录快照为准。
