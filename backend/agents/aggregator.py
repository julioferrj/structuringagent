"""Summarization utilities for multiple documents."""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

from backend.schemas.raw_doc import RawDocument


_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Eres un asistente que resume documentos."),
        ("user", "{text}"),
    ]
)


def summarize_documents(json_paths: List[str]) -> str:
    """Return a short summary for all provided document JSON files."""
    texts: List[str] = []
    for path_str in json_paths:
        path = Path(path_str)
        raw = RawDocument.model_validate_json(path.read_text(encoding="utf-8"))
        pages = raw.content.get("pages", [])
        texts.append("\n".join(pages))

    combined = "\n\n".join(texts)
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    chain = _SUMMARY_PROMPT | llm
    return chain.invoke({"text": combined}).content


summarize_tool = Tool(
    name="summarize_documents",
    func=summarize_documents,
    description="Summarize multiple document JSON files into a short paragraph",
)
