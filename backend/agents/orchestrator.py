from pathlib import Path
from typing import Any, Dict, List

from backend.agents.classifier import classify
from backend.tools import splitter_tool


def analyze(raw_json_path: str | Path) -> Dict[str, Any]:
    """Classify the document and split if it's a package."""
    raw_path = Path(raw_json_path)
    classification = classify(raw_path)
    children: List[str] = []
    if classification.get("doc_type") == "paquete_eeff":
        try:
            children = splitter_tool.run(str(raw_path))
        except Exception:
            children = []
    return {"classification": classification, "children": children}
