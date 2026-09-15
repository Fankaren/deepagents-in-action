# 问题说明与经验教训

## 1. 飞书文章抓不到正文

- **现象**：`magicyang.feishu.cn/share/base/...` 返回登录壳。  
- **处理**：改用 Datawhale 仓库与 LangChain 官方文档对齐实现。  
- **教训**：课程正文以 GitHub 源为准。

## 2. 日日新 API 地址

- **错误尝试**：`api.sensenova.cn/compatible-mode/...` → 403/404。  
- **正确**：`https://token.sensenova.cn/v1`（文档站 JS 里可找到）。  
- **教训**：先 `GET /v1/models` 探活，再写客户端。

## 3. 中文 Windows 下 `.bat` 乱码/命令被截断

- **现象**：`'nul' 不是内部或外部命令`、路径变 `nt_study`。  
- **原因**：UTF-8 保存的中文 bat 被 GBK 解析。  
- **处理**：脚本改为 GBK，或使用英文 `start_env.bat`。  

## 4. RPM 限流（429）

- **现象**：`rpm exhausted` / `inference exceeds tpm/rpm limit`。  
- **处理**：`max_retries` + 退避；复杂任务改 `glm-5.2`；`switch_model.py` 切换。  

## 5. PowerShell 中文命令行编码

- **现象**：HTTP 探针中文变成 `???`。  
- **处理**：业务逻辑放 Python 文件（UTF-8），PS 只做编排；`PYTHONIOENCODING=utf-8`。  

## 6. SeekDB 嵌入式仅 Linux

- **现象**：`pylibseekdb is not available`（Windows）。  
- **处理**：`SEEKDB_EMBED=false` + SQLite。  
- **长期**：开 SVM 虚拟化并升 WSL2 后再用官方推荐路径。  

## 7. WSL 实际是 v1

- **现象**：`wsl -l -v` 显示 VERSION 1；内核 `4.4.0-...-Microsoft`。  
- **原因**：BIOS 未开 AMD SVM。  
- **教训**：先查版本再按 WSL2 文档操作。  

## 8. GitHub 访问

- **处理**：`codeload.github.com` / `ghproxy.net` 下载 zip，再用本地模板路径 create。  
- **教训**：`agentseek create <local-template-path> --no-input` 可离线脚手架。  

## 9. API Key 安全

- Key 只放在 `.env`（已 gitignore）。  
- 文档与提交材料中不要粘贴完整 Key。  

## 10. UI 发了消息但 Smith 网页看不到 Trace

- **现象**：在 `http://127.0.0.1:5174/?thread=...` 发了 `hi` / `你好`，Smith 项目里仍只有旧 Trace。  
- **原因**：`agentseek-api` 进程在改 `.env`（新 Key / `LANGSMITH_TRACING=true`）**之前**就已启动；服务端不会热加载环境变量。  
- **证据**：API `StartTime` 早于 `.env` 的 `LastWriteTime`；重启后同脚本 `invoke('hi')` 立刻多出一条 Trace。  
- **处理**：改完 `research_deepagent\.env` 后必须 **重启** `agentseek-api`（关掉 `agentseek dev` 再起，或结束进程再 `start_research.bat`）。  
- **教训**：Env 变更 → 重启后端 → 再在 UI 触发；排查时对比进程启动时间与文件修改时间。  

---

## 会话收尾模板（已写入全局记忆）

每次完成任务后固定回复：

1. **做了什么**（结果 + 路径）  
2. **学到了什么**（概念）  
3. **经验教训**（坑）  
