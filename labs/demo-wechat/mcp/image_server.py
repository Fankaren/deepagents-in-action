"""Task 9-1 · 图床 MCP 服务（ch12 预览）

用官方 MCP Python SDK 暴露「免费图床」能力，stdio 方式供 Deep Agent 调用：
  - search_free_images(query, count)：返回免费图片 URL（Pexels 有 key 用 Pexels，否则 picsum.photos）
  - image_markdown(urls, caption)：把 URL 列表拼成 Markdown 图块

单独运行（stdio）：  python mcp/image_server.py
被 agents.py 通过 MultiServerMCPClient 以 stdio 拉起。
"""
from __future__ import annotations

import json
import os
import urllib.request
from urllib.parse import quote_plus

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("需要安装 MCP SDK：pip install mcp") from exc

mcp = FastMCP("free-image-host")


def _picsum(query: str, count: int) -> list[str]:
    seed = quote_plus(query)[:40] or "wechat"
    return [f"https://picsum.photos/seed/{seed}-{i}/800/600" for i in range(1, max(1, count) + 1)]


def _pexels(query: str, count: int, key: str) -> list[str]:
    url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page={count}&orientation=landscape"
    req = urllib.request.Request(url, headers={"Authorization": key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [p["src"]["large"] for p in data.get("photos", [])][:count]


@mcp.tool()
def search_free_images(query: str, count: int = 3) -> list[str]:
    """在免费图床按关键词搜索图片，返回图片 URL 列表。"""
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        try:
            return _pexels(query, count, key)
        except Exception:
            pass
    return _picsum(query, count)


@mcp.tool()
def image_markdown(urls: list[str], caption: str = "配图") -> str:
    """把图片 URL 列表拼成 Markdown 图块（用于插入推文）。"""
    return "\n\n".join(f"![{caption}{i}]({u})" for i, u in enumerate(urls, 1))


if __name__ == "__main__":
    mcp.run()
