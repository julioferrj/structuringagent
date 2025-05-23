"""LangChain agent orchestrating document classification, retrieval and analysis."""

from __future__ import annotations

from typing import Any, Dict, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

from backend.agents.classifier import classify
from backend.tools import analysis_tool


# ──────────────────── Classification Tool ──────────────────── #

def _classify(json_path: str) -> Dict[str, Any]:
    return classify(json_path)


classify_tool = Tool(
    name="classify_document",
    func=_classify,
    description="Classify a RawDocument JSON file by type and period",
)


# ───────────────────── Retrieval Tool ──────────────────────── #

def _retrieve(query: str) -> str:
    return f"Retrieved information for: {query}"


retrieve_tool = Tool(
    name="retrieve_information",
    func=_retrieve,
    description="Retrieve additional information for a given query",
)


# ────────────────────── Analysis Tool ───────────────────────── #

def _analyze(text: str) -> str:
    return analysis_tool.run(text)


analyze_tool = Tool(
    name="analyze_text",
    func=_analyze,
    description="Analyze text and return a short summary",
)


_TOOLS: List[Tool] = [classify_tool, retrieve_tool, analyze_tool]

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un asistente para procesar documentos. Usa las herramientas disponibles y responde en español.",
        ),
        ("user", "{input}"),
    ]
)


def get_orchestrator_agent() -> AgentExecutor:
    """Return a LangChain AgentExecutor exposing the available tools."""
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    agent = create_tool_calling_agent(llm, _TOOLS, _PROMPT)
    return AgentExecutor(agent=agent, tools=_TOOLS)
