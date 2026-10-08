"""Task 9-1 · 生成公众号首图（从模板填充标题/S系列，输出 SVG，并尽量用 Chrome 渲染 PNG）

用法：
    python make_cover.py --series 底层逻辑 --title "Q4第一天…" --subtitle "把时间存进银行" 
    python make_cover.py --series 习惯复利 --title "每天20分钟" --out workspace/drafts/cover.png
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "brand", "cover-primary.svg")
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def slugify(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text).strip("-")[:40] or "cover"


def split_title(title: str, max_len: int = 11) -> tuple[str, str]:
    """把长标题断成两行：优先在标点处断，否则按长度对半。"""
    title = title.strip()
    if len(title) <= max_len + 2:
        return title, ""
    puncts = "，。、；：！？,;:!? "
    mid = len(title) // 2
    best = -1
    for i, ch in enumerate(title):
        if ch in puncts and abs(i - mid) < max_len:
            if best == -1 or abs(i - mid) < abs(best - mid):
                best = i
    cut = best + 1 if best != -1 else mid
    return title[:cut].strip(), title[cut:].strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="底层逻辑")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    line1, line2 = split_title(args.title)
    svg = open(TEMPLATE, encoding="utf-8").read()
    svg = (
        svg.replace("{{TITLE1}}", html.escape(line1))
        .replace("{{TITLE2}}", html.escape(line2))
        .replace("{{SERIES}}", html.escape(args.series))
        .replace("{{SUBTITLE}}", html.escape(args.subtitle))
    )

    out_svg = args.out or os.path.join("workspace", "drafts", slugify(args.title) + "-cover.svg")
    if out_svg.lower().endswith(".png"):
        out_svg = out_svg[:-4] + ".svg"
    os.makedirs(os.path.dirname(out_svg) or ".", exist_ok=True)
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg)
    print("SVG:", out_svg)

    chrome = find_chrome()
    if not chrome:
        print("未找到 Chrome/Edge，跳过 PNG 渲染（可直接用上面的 SVG 或在线转换）。")
        return
    out_png = (args.out[:-4] + ".png") if args.out.lower().endswith(".png") else out_svg[:-4] + ".png"
    url = "file:///" + os.path.abspath(out_svg).replace("\\", "/")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
         "--no-default-browser-check", "--user-data-dir=" + os.path.join(HERE, "workspace", ".chrome"),
         "--window-size=900,383", "--force-device-scale-factor=2", "--screenshot=" + os.path.abspath(out_png), url],
        check=False,
    )
    print("PNG:", out_png if os.path.isfile(out_png) else "(渲染失败)")


if __name__ == "__main__":
    main()
