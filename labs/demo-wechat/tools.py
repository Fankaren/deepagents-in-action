"""Task 9-1 · 工具集（本地）

- web_search：免费热度搜索（DuckDuckGo，`ddgs`/`duckduckgo_search`），无依赖时回退为提示。
- search_free_images：图床本地回退（Pexels 有 key 时用 Pexels，否则 picsum.photos）——
  MCP 图床（mcp/image_server.py）不可用时用它。
- publish_article：HITL 敏感工具（触发审批后才真正执行，写入副作用账本）。
"""
from __future__ import annotations

import os
from urllib.parse import quote_plus

from langchain_core.tools import tool

from _common import ToolLedger, today


def _ddgs_search(query: str, max_results: int) -> str:
    try:
        try:
            from ddgs import DDGS  # 新版包名
        except Exception:
            from duckduckgo_search import DDGS  # 旧版包名
    except Exception:
        return (
            f"[web_search 未安装] 未找到 ddgs/duckduckgo_search。"
            f"请基于你掌握的「男性向爆款内容」规律，围绕关键词「{query}」自行脑暴若干选题与角度。"
        )
    rows = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = r.get("title", "")
            href = r.get("href", "")
            body = (r.get("body", "") or "")[:120]
            rows.append(f"- {title} | {href}\n  {body}")
    return "\n".join(rows) if rows else f"（无搜索结果，请基于通识脑暴关键词「{query}」的选题）"


def build_tools(ledger: ToolLedger) -> dict:
    @tool
    def web_search(query: str, max_results: int = 5) -> str:
        """搜索网上的热点资讯（免费 DuckDuckGo），返回标题+链接+摘要列表。"""
        return _ddgs_search(query, max_results)

    @tool
    def search_free_images(query: str, count: int = 3) -> str:
        """在免费图床搜索配图，返回图片 URL 列表（一行一个）。"""
        return "\n".join(_free_image_urls(query, count))

    @tool
    def publish_article(title: str, draft_path: str, cover_image: str = "") -> str:
        """【敏感】把终稿标记为可发布。需人工审批通过后才真正执行。"""
        ledger.record("publish_article", {"title": title, "draft_path": draft_path, "cover_image": cover_image})
        return f"PUBLISH-READY :: {title} :: {draft_path} :: {today()}"

    return {
        "web_search": web_search,
        "search_free_images": search_free_images,
        "publish_article": publish_article,
    }


# --------------------------------------------------------------------------- #
# 图床逻辑（MCP 与本地回退共用）
# --------------------------------------------------------------------------- #
def _free_image_urls(query: str, count: int) -> list[str]:
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        try:
            return _pexels(query, count, key)
        except Exception as exc:  # noqa: BLE001
            print(f"[images] Pexels 失败，回退 picsum：{exc}")
    seed = quote_plus(query)[:40] or "wechat"
    return [f"https://picsum.photos/seed/{seed}-{i}/800/600" for i in range(1, max(1, count) + 1)]


def _pexels(query: str, count: int, key: str) -> list[str]:
    import json
    import urllib.request

    url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page={count}&orientation=landscape"
    req = urllib.request.Request(url, headers={"Authorization": key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [p["src"]["large"] for p in data.get("photos", [])][:count]


def image_markdown(urls: list[str], caption: str = "") -> str:
    lines = []
    for i, u in enumerate(urls, 1):
        lines.append(f"![{caption or '配图'}{i}]({u})")
    return "\n\n".join(lines)
