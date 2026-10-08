"""Task 9-1 · 生成公众号首图（模板填充 + 自动断行 + 无头 Chrome 渲染 PNG）

既可命令行用，也可被 Agent 的 make_cover 工具 / run_daily 调用：
    python make_cover.py --series 底层逻辑 --title "Q4第一天…" --subtitle "把时间存进银行"
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "brand", "cover-primary.svg")
DEFAULT_OUTDIR = os.path.join(HERE, "workspace", "drafts")
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


def generate(title: str, series: str = "底层逻辑", subtitle: str = "", out: str = "") -> dict:
    """生成封面，返回 {"svg":..., "png":...(可能为 None)}。"""
    out = out or os.path.join(DEFAULT_OUTDIR, slugify(title) + "-cover.png")
    if not os.path.isabs(out):
        out = os.path.join(HERE, out)
    out = out.replace(".svg", ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    line1, line2 = split_title(title)
    svg = open(TEMPLATE, encoding="utf-8").read()
    svg = (
        svg.replace("{{TITLE1}}", html.escape(line1))
        .replace("{{TITLE2}}", html.escape(line2))
        .replace("{{SERIES}}", html.escape(series))
        .replace("{{SUBTITLE}}", html.escape(subtitle))
    )
    out_svg = out[:-4] + ".svg"
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg)

    chrome = find_chrome()
    if not chrome:
        return {"svg": out_svg, "png": None}
    url = "file:///" + os.path.abspath(out_svg).replace("\\", "/")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
         "--no-default-browser-check", "--user-data-dir=" + os.path.join(HERE, "workspace", ".chrome"),
         "--window-size=900,383", "--force-device-scale-factor=2", "--screenshot=" + os.path.abspath(out), url],
        check=False,
    )
    return {"svg": out_svg, "png": out if os.path.isfile(out) else None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="底层逻辑")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    res = generate(args.title, args.series, args.subtitle, args.out)
    print("SVG:", res["svg"])
    print("PNG:", res["png"] if res["png"] else "(未渲染，需 Chrome/Edge 或在线转换)")


if __name__ == "__main__":
    main()
