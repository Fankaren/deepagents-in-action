# pre02 完成状态

## 已完成

| 项 | 状态 | 位置/说明 |
|----|------|-----------|
| 项目级安装 skills | 完成 | `research_deepagent\.agents\skills\langchain-dev-guide` |
| | | `research_deepagent\.agents\skills\langsmith-trace` |
| LangSmith CLI | 完成 | `langsmith 0.2.55`，已加入用户 PATH |
| skills 安全扫描 | 完成 | Socket 0 alerts；langsmith-trace Snyk Med Risk（可接受） |
| 密钥泄露审计 | 完成 | 见 [secret-audit.md](./secret-audit.md)，**未泄露真实 Key** |
| Trace 实操尝试 | 部分 | SDK/CLI 可用；当前 API Key 返回 **403 Forbidden**，追踪未写入 |

## 待完成 / 可选

| 项 | 说明 |
|----|------|
| 重新创建 LangSmith Key | 到 [smith.langchain.com/settings/apikeys](https://smith.langchain.com/settings/apikeys) 新建；确认组织权限 |
| 写入正确 `.env` | 必须写在 `research_deepagent\.env`（研究应用读取处），不是根目录练习用 `.env` |
| 打开追踪 | `LANGSMITH_TRACING=true` 后 `agentseek dev` 跑一条 research |
| CLI 分析 | `langsmith project list` → `langsmith trace list --project deepagents-course --name research` |
| Agents linked | `npx skills list` 显示 not linked；MiMo Desktop 读项目 `.agents/skills` 不依赖 link |

## 排查 403 备忘

已测：`api.smith.langchain.com` / `apac` / `eu` 均 403。常见原因：

1. Key 复制不完整或过期  
2. 新建 Key 时选错 Workspace/Org  
3. 账号未完成邮箱验证  

## 常用命令

```powershell
npx skills list
langsmith --version
langsmith project list
langsmith trace list --project deepagents-course --limit 5
```
