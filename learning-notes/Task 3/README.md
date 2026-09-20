# Task 3 · 虚拟文件系统（ch03）

**学习方式**：动手工作坊，不是只读笔记。

| 材料 | 路径 |
|------|------|
| 工作坊主文档（一步步怎么做） | `D:\agent_study\labs\ch03\WORKSHOP.md` |
| 实验脚本 step1–6 | `D:\agent_study\labs\ch03\step*.py` |
| 实验日志模板 | `learning-notes/Task 3/lab-journal.md` |

## 本章你将学会

1. 看见 Deep Agent **默认注入**的 7 个文件工具  
2. 观察 **write → read → 摘要** 的上下文外置  
3. 使用/区分 **grep** 三种 `output_mode`  
4. 用磁盘验证 **StateBackend vs FilesystemBackend**  
5. 用 **CompositeBackend** 按路径路由草稿纸/记忆库  
6. 理解 **FilesystemPermission** 是工具层强制而非“模型自觉”  

## 怎么开始（现在就做）

```powershell
D:\agent_study\start_env.bat
cd D:\agent_study\labs\ch03
# 先在 WORKSHOP.md 里写 Step1 预测，再：
python step1_list_tools.py
```

每步流程：**预测 → 运行 → 勾观察清单 → 做「你的任务」→ 写 lab-journal**。

## 课程原文

https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/

建议：**先做完 Step1–2 再回读原文**，概念会粘在你自己的实验现象上。
