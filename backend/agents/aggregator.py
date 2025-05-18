from pathlib import Path
from typing import Any, Dict, List

from backend.schemas.raw_doc import RawDocument


def aggregate(json_paths: List[str]) -> Dict[str, Any]:
    """Return basic metadata for a list of raw documents."""
    docs = []
    counts: Dict[str, int] = {}
    for p in json_paths:
        raw = RawDocument.model_validate_json(Path(p).read_text(encoding="utf-8"))
        info = {"id": raw.id, "doc_type": raw.doc_type, "period": raw.period}
        docs.append(info)
        counts[raw.doc_type] = counts.get(raw.doc_type, 0) + 1
    return {"documents": docs, "counts": counts}
