# 密钥泄露审计（推送后）

**时间**：2026-09-16  
**仓库**：https://github.com/Fankaren/deepagents-in-action  
**提交**：`978232c`（learning-notes/Task 0）

## 结论

**未发现真实 API Key 泄露。**

| 扫描项 | 结果 |
|--------|------|
| 日日新 Key `sk-nMsCQlwt...` | 仓库中无 |
| Tavily 完整 Key `tvly-dev-...` | 仓库中无（仅文档占位 `tvly-...`） |
| LangSmith Key `lsv2_...` | 仓库中无 |
| `.env` 文件 | 未纳入 git |
| 课程正文中的 `OPENAI_API_KEY=sk-...` | 上游示例占位符，非你的 Key |

学习笔记里出现的都是**变量名说明**或**占位符**，例如：

- `TAVILY_API_KEY=tvly-...`
- `LANGSMITH_API_KEY=<你的 key>`
- `SENSNOVA_API_KEY`（仅提及环境变量名）

## 建议

1. 继续用 `**/.env` gitignore；提交前用下面命令复查：
   ```powershell
   git grep -nE 'sk-[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9]{20,}|lsv2_[A-Za-z0-9]{10,}'
   ```
2. 若未来误提交密钥：立刻在平台轮换 Key，并 `git filter-repo` / 重写历史后再 force push（需评估协作影响）。
