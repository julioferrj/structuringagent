from pathlib import Path
from langchain.tools import Tool
from backend.schemas.raw_doc import RawDocument


def analyze_document(json_path: str) -> str:
    """Perform a simple analysis on a RawDocument."""
    raw = RawDocument.model_validate_json(Path(json_path).read_text(encoding="utf-8"))
    num_pages = len(raw.content.get("pages", []))
    return f"Analysis for {raw.filename}: {num_pages} pages"


analysis_tool = Tool(
    name="analyze_document",
    func=analyze_document,
    description="Analyze a raw document and return a brief summary",
)

__all__ = ["analysis_tool", "analyze_document"]
