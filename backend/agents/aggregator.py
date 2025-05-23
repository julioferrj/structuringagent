"""Utilities to aggregate information from multiple documents."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from langchain_core.tools import Tool

from backend.schemas.raw_doc import RawDocument


def aggregate_results(json_paths: List[str]) -> Dict[str, str]:
    """Merge several RawDocument JSON files by document type."""
    combined: Dict[str, List[str]] = {}
    for path_str in json_paths:
        path = Path(path_str)
        raw = RawDocument.model_validate_json(path.read_text(encoding="utf-8"))
        pages = raw.content.get("pages", [])
        combined.setdefault(raw.doc_type, []).extend(pages)

    return {doc_type: "\n".join(pages) for doc_type, pages in combined.items()}


aggregate_tool = Tool(
    name="aggregate_results",
    func=aggregate_results,
    description="Combine multiple document JSON files into one structure",
)
