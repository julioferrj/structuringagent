"""Aggregate multiple analyses into a summary."""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Eres un analista financiero. Resume los siguientes analisis"),
        ("human", "{analyses}"),
    ]
)


def aggregate(analyses: list[str]) -> str:
    """Return a summary of all analyses."""
    payload = "\n".join(analyses)
    return (PROMPT | llm).invoke({"analyses": payload}).content

__all__ = ["aggregate"]
