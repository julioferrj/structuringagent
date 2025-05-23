"""Simple aggregator for processed documents."""

from pathlib import Path
from typing import List, Dict

from langchain_core.tools import Tool

from backend.schemas.raw_doc import RawDocument


def aggregate_results(paths: List[str]) -> Dict[str, int | List[dict]]:
    """Load raw documents and aggregate basic statistics."""
    docs = [
        RawDocument.model_validate_json(Path(p).read_text(encoding="utf-8"))
        for p in paths
    ]
    summary: Dict[str, int] = {}
    for doc in docs:
        summary[doc.doc_type] = summary.get(doc.doc_type, 0) + 1
    return {
        "documents": [d.model_dump() for d in docs],
        "summary": summary,
    }


aggregate_tool = Tool(
    name="aggregate_documents",
    func=aggregate_results,
    description="Aggregate information from multiple raw documents",
)
