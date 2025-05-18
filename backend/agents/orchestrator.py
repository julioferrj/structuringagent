"""LangChain agent providing classification, retrieval and analysis tools."""

from pathlib import Path
import json

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool

from .classifier import classify


# ──────────────────── Retrieval helper ──────────────────── #

def retrieve_document(json_path: str | Path) -> dict:
    """Load a RawDocument JSON file and return it as a dict."""
    return json.loads(Path(json_path).read_text(encoding="utf-8"))


retrieve_tool = Tool(
    name="retrieve_document",
    func=retrieve_document,
    description="Carga un RawDocument desde su ruta JSON y devuelve dict",
)


# ──────────────────── Analysis helper ──────────────────── #
_llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

_ANALYSIS_PROMPT = ChatPromptTemplate.from_template(
    "Analiza el siguiente documento financiero y resume los puntos clave:\n{content}"
)


def analyze_document(json_path: str | Path) -> str:
    raw = retrieve_document(json_path)
    text = "\n".join(raw.get("content", {}).get("pages", []))[:15000]
    return (_ANALYSIS_PROMPT | _llm).invoke({"content": text}).content


analyze_tool = Tool(
    name="analyze_document",
    func=analyze_document,
    description=(
        "Analiza un RawDocument (ruta JSON) y devuelve un breve resumen"
    ),
)


# ──────────────────── Classification tool ──────────────────── #
classify_tool = Tool(
    name="classify_document",
    func=classify,
    description=(
        "Clasifica un documento crudo (JSON) y devuelve dict "
        "{doc_type, period}. Input: ruta del JSON."
    ),
)


# ──────────────────── Agent factory ──────────────────── #

def get_orchestrator_agent():
    """Return an agent with classification, retrieval and analysis tools."""
    tools = [classify_tool, retrieve_tool, analyze_tool]
    return initialize_agent(
        tools,
        _llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=False,
    )


__all__ = [
    "get_orchestrator_agent",
    "classify_tool",
    "retrieve_tool",
    "analyze_tool",
]
