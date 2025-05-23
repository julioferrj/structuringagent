"""Simple orchestrator agent utilities."""

from pathlib import Path
from typing import Dict, Any

from langchain_core.tools import Tool

from backend.agents.classifier import classify
from backend.tools import splitter_tool, analysis_tool


def _classify_document(json_path: str) -> Dict[str, Any]:
    """Classify a raw JSON document."""
    return classify(json_path)


classify_tool = Tool(
    name="classify_document",
    func=_classify_document,
    description="Classify a raw document by type and period",
)


def _orchestrate(json_path: str) -> Dict[str, Any]:
    """Run a simple orchestration pipeline over the raw document."""
    result = {"classification": _classify_document(json_path), "children": []}
    if result["classification"].get("doc_type") == "paquete_eeff":
        run = getattr(splitter_tool, "run", splitter_tool)
        result["children"] = run(json_path)
    return result


orchestrator_tool = Tool(
    name="orchestrate_document",
    func=_orchestrate,
    description="Classify a document and split financial packages into parts",
)


def _retrieve(query: str) -> str:
    """Dummy retrieval function used as a placeholder."""
    return f"Retrieved information for: {query}"


retrieve_tool = Tool(
    name="retrieve_information",
    func=_retrieve,
    description="Retrieve additional information for a given query",
)


def _analyze(text: str) -> str:
    """Analyze text with a simple helper."""
    return analysis_tool(text)


analyze_tool = Tool(
    name="analyze_text",
    func=_analyze,
    description="Analyze text and return a short summary",
)


def get_orchestrator_agent():
    """Return the main orchestrator callable (placeholder)."""
    return orchestrator_tool
