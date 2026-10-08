# Task 9-1 · 预测题（先作答，再执行）

> **本 Demo 按需求跳过预测题**，保留文件仅作参考；记录以 `progress-log.md` 三段式为准。

---

## Step 0 · 仪器单测（零模型）

**Q0-1** 预计通过率？ A 全 PASS / B 个别失败 / C 大量 FAIL
**Q0-2** 无 `PEXELS_API_KEY` 时图床回退到？ A 报错 / B picsum.photos / C 空列表

## Step 1 · 跑通主流程

**Q1-1** 主编会委派 `trend-researcher` 子 Agent 吗？ A 会 / B 不会
**Q1-2** 终稿会按 SKILL 骨架（3 标题候选 + 3 小节 + 结尾引导）吗？ A 会 / B 不会
**Q1-3** 草稿会落盘到 `workspace/drafts/` 吗？ A 会 / B 只在对话里
**Q1-4** 会触发 `publish_article` 审批中断吗？ A 会 / B 不会

## Step 2 · 人工审批

**Q2-1** 中断发生时，选题台账是否**已被写入**？ A 已写 / B 未写
**Q2-2** approve 后账本 `publish_article` 笔数？ A 0 / B 1
**Q2-3** edit（改标题）后发布用的是？ A 原始标题 / B 改后标题
**Q2-4** reject 后账本笔数？ A 0 / B 1

## Step 3 · 记忆跨日累积

**Q3-1** 第二次运行时，模型请求里能看到上次写入的台账吗？ A 能 / B 不能

## Step 4 · 图床 MCP（预览）

**Q4-1** 未装 `mcp`/`langchain-mcp-adapters` 时 `--mcp` 会？ A 直接报错 / B 打印回退信息并用本地工具

---

## 作答方式

```text
Step0: Q0-1=  Q0-2=
Step1: Q1-1=  Q1-2=  Q1-3=  Q1-4=
...
```
