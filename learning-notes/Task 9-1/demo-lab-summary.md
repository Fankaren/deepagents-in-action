# Task 9-1 · 综合 Demo —— 实验小结

**主题**：男性向内容微信公众号推文 Agent
**组合**：子 Agent（ch05）+ Skills（ch07）+ 长期记忆（ch08）+ HITL（ch09）+ 图床 MCP（ch12 预览）
**环境**：deepagents（>=0.6.8）/ langchain（>=1.3.3）/ 商汤日日新 `glm-5.2`（无需起服务）
**材料**：`labs/demo-wechat/`（`_common.py`/`tools.py`/`agents.py`/`run_daily.py`/`memory_cli.py`/`skills`/`mcp`/`step0_selftest.py`）

---

## 一、项目目标与交付
一条可跑的内容流水线：**读记忆 → 子 Agent 选题 → 按技能统一格式成稿（体系化长文）→ 子 Agent 配图 → 人工审批 → 入库（用户自行发布）**，每日≥1 篇。

## 二、能力落点与实测证据

| 能力 | 落点 | 实测证据 |
|------|------|----------|
| 子 Agent（ch05）| trend-researcher / image-scout | 主编 `task` 委派出 5 个候选选题 + 5 张配图 |
| Skills（ch07）| `/skills/wechat-article` | 成稿含系列标识、4-5 节、可复用框架；篇幅达标 |
| 长期记忆（ch08）| 5 个 `/memories/*` + 持久化 Store | `store.json` 跨进程保留；knowledge-base 跨 3 系列累积 |
| HITL（ch09）| `publish_article` 审批 | 暂停在写台账之前；edit 用改后标题、账本可区分 |
| MCP（ch12 预览）| `mcp/image_server.py` | 未跑（可选，已验证本地回退） |

## 三、实测结果

| Step | 问题 | 结果 | 关键证据 |
|------|------|------|----------|
| 0 | 仪器可信吗 | **21/21 PASS** | 技能/战略标记、4 系列、篇幅纪律、**持久化跨实例** |
| 1 | 主流程跑通吗 | **PASS** | 2200 字/7 分钟/4 节；草稿落 `workspace/drafts/`；knowledge-base 新增框架+金句 |
| 2 | 审批落点 | **PASS** | `edit` → `publish_article` 用改后标题（账本 `title=test`）；草稿文件名不变 |
| 3 | 跨天 + 调优 | **PASS** | 第三次主编推进《决策工具箱》，**引用完读率 0.42** 调整写法，并复用前文框架 |
| 4 | 图床 MCP | 未跑 | 本地回退可用（picsum） |

## 四、两条业务要求的落实

1. **锁定方向 + 体系化 + 知识沉淀 + 阅读时长**
   - 方向由应用侧 `memory_cli.py set-direction` 写死 `content-strategy.md`，提示词铁律「不得自换」；四系列轮转推进
   - `knowledge-base.md` 跨篇累积可复用框架/金句（实测：底层逻辑→习惯复利→决策工具箱三系列均沉淀）
   - `SKILL.md` 强制 1800-2600 字 / 6-9 分钟长文
2. **依据阅读量调优**
   - `performance.md` 台账（`memory_cli record` 录入）；提示词要求规划前必读
   - 实测：第三次运行主编**引用完读率数据**调整开头钩子与节奏，**未更换方向/系列**

## 五、工程要点与踩坑

1. **跨天记忆的关键是 Store 持久化**：`InMemoryStore` 进程结束即丢 → 用其子类拦截 `batch/abatch` 镜像到 `workspace/.state/store.json`（只抽象 `batch/abatch` 即可实现）
2. **Windows 并发保存冲突**：纯读也落盘 + 并行工具调用 → `store.json.tmp` 占用 `WinError 32`。修：仅含 PutOp 才落盘 + `threading.Lock` + 唯一 tmp + 重试
3. **虚拟路径前缀**：`FilesystemBackend(root_dir=workspace)` 下应为 `/drafts`、`/skills`，写成 `/workspace/...` 会嵌套成 `workspace/workspace/...`
4. **台账写入方要统一**：agent 与应用侧各写一套格式会混排（本 Demo 待收敛）

## 六、方法论遗产
- 观测点复用：请求级仪器（技能/记忆进没进上下文）+ 副作用账本（审批前有没有误执行）
- 综合项目 = 职责切分：**知识（记忆）/ 能力（技能）/ 侦察（子 Agent）/ 安全（审批）** 各归其位
- 「方向锁定」靠配置写死 + 提示词约束；「调优」靠数据沉淀 + 规划前读取——两者不矛盾

## 七、遗留 / 下一步
- Step 4 图床 MCP 未跑（`pip install mcp langchain-mcp-adapters` 后 `--mcp`）
- 台账格式收敛；`performance` 自动拉取（微信数据需人工/爬取）
- 可加：定时任务（每日自动跑一篇）、多平台分发（公众号/小红书）
