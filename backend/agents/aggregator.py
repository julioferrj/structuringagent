"""Utility to summarize multiple analysis results using an LLM."""

from typing import List

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool


# LLM configuration shared across helpers
_llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

_SUMMARY_PROMPT = ChatPromptTemplate.from_template(
    "Eres analista financiero. Resume de forma concisa los siguientes\n"
    "análisis financieros:\n{analyses}"
)


def aggregate_results(analyses: List[str]) -> str:
    """Combine and summarize multiple analysis strings."""
    text = "\n\n".join(analyses)
    return (_SUMMARY_PROMPT | _llm).invoke({"analyses": text}).content


def _aggregate_from_str(text: str) -> str:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return aggregate_results(parts)


aggregate_tool = Tool(
    name="aggregate_analyses",
    func=_aggregate_from_str,
    description=(
        "Resume varios análisis de documentos financieros "
        "separados por dobles saltos de línea."
    ),
)

__all__ = ["aggregate_results", "aggregate_tool"]
