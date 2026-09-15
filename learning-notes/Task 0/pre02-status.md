# pre02 完成状态

## 已完成

| 项 | 状态 | 位置/说明 |
|----|------|-----------|
| 项目级安装 skills | 完成 | `research_deepagent\.agents\skills\langchain-dev-guide` |
| | | `research_deepagent\.agents\skills\langsmith-trace` |
| LangSmith CLI | 完成 | `langsmith 0.2.55`，已加入用户 PATH |
| skills 安全扫描 | 完成 | Socket 0 alerts；langsmith-trace Snyk Med Risk（可接受） |

## 待完成 / 可选

| 项 | 说明 |
|----|------|
| Trace 实操（pre02 §5） | 需在 `.env` 开启 `LANGSMITH_TRACING=true` 并配置 `LANGSMITH_API_KEY`，跑一次 research 后再用 CLI 分析 |
| Agents linked | `npx skills list` 显示 not linked；若用 Trae/Codex 可再 link；MiMo Desktop 读项目 `.agents/skills` 不依赖 link |

## 常用命令

```powershell
npx skills list
npx skills update -p
langsmith --version
langsmith project list
```
