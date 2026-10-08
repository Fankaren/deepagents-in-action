"""Task 9-1 · 记忆管理 CLI（读写持久化 Store）

用法：
  python memory_cli.py show
  python memory_cli.py set-direction "主方向：<...>；系列：A/B/C/D；篇幅：1800-2600字/6-9分钟"
  python memory_cli.py add-plan "《底层逻辑》选题：..."
  python memory_cli.py record --series 底层逻辑 --title "..." --reads 3200 --likes 120 [--finish 0.42] [--note "标题偏长"]
  python memory_cli.py --editor-id editor-001 show
"""
from __future__ import annotations

import argparse

from _common import append_memory, build_store, read_memory, today

FILES = {
    "content-strategy.md": "内容战略（锁定方向）",
    "content-plan.md": "内容规划（系列选题库）",
    "knowledge-base.md": "知识沉淀",
    "performance.md": "阅读量台账",
    "topic-ledger.md": "已发选题台账",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--editor-id", default="editor-001")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show", help="打印全部记忆文件")
    d = sub.add_parser("set-direction", help="锁定/更新主方向（覆盖 content-strategy）")
    d.add_argument("text")
    p = sub.add_parser("add-plan", help="向内容规划追加一条选题")
    p.add_argument("text")
    r = sub.add_parser("record", help="记录一篇的阅读量数据")

    r.add_argument("--series", default="")
    r.add_argument("--title", required=True)
    r.add_argument("--reads", type=int, default=0)
    r.add_argument("--likes", type=int, default=0)
    r.add_argument("--finish", default="")
    r.add_argument("--note", default="")

    args = ap.parse_args()
    store = build_store()
    eid = args.editor_id

    if args.cmd == "show":
        for fname, label in FILES.items():
            print("\n" + "=" * 62 + f"\n# {label}   /memories/{fname}\n" + "-" * 62)
            print(read_memory(store, eid, "/" + fname))

    elif args.cmd == "set-direction":
        from deepagents.backends.utils import create_file_data

        content = (
            "# 内容战略（锁定方向 · 请勿自行更改）\n"
            "<!-- CONTENT-STRATEGY-LOADED -->\n"
            + args.text.strip()
            + "\n"
        )
        store.put((eid, "memories"), "/content-strategy.md", create_file_data(content))
        print("已更新并锁定方向（写入 /memories/content-strategy.md）。")

    elif args.cmd == "add-plan":
        append_memory(store, eid, "/content-plan.md", "- [ ] " + args.text.strip())
        print("已加入内容规划。")

    elif args.cmd == "record":
        line = (
            f"- {today()} | {args.series or '-'} | {args.title} | 阅读 {args.reads} | "
            f"点赞 {args.likes} | 完读 {args.finish or '-'} | {args.note or '-'}"
        )
        append_memory(store, eid, "/performance.md", line)
        print("已记录阅读量。下次规划时会读取 performance 调整策略（方向/系列不变）。")


if __name__ == "__main__":
    main()
