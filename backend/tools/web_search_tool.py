"""Simple web search utility."""

from __future__ import annotations

import re
import urllib.parse
import urllib.request


def web_search(query: str) -> str:
    """Perform a basic DuckDuckGo search and return the first result title."""
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Web search failed: {e}"

    match = re.search(r'class="result__a"[^>]*>(.*?)<', html)
    if match:
        title = re.sub("<.*?>", "", match.group(1))
        return title.strip()
    return "No results found."
