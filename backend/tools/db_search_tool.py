"""Simple DB search utility."""

from __future__ import annotations

import json
from pathlib import Path

_DB_PATH = Path(__file__).with_name("sample_db.json")


def _load_db() -> list[dict[str, str]]:
    if _DB_PATH.exists():
        return json.loads(_DB_PATH.read_text(encoding="utf-8"))
    return []


def db_search(query: str) -> str:
    """Search the local JSON database for records containing the query."""
    data = _load_db()
    q = query.lower()
    matches = [row for row in data if q in row.get("text", "").lower()]
    return json.dumps(matches[:5], ensure_ascii=False)
