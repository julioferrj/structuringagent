"""Simple orchestrator agent using LangChain."""

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

from backend.agents.classifier import classify
from backend.tools import (
    analysis_tool,
    db_search_tool,
    web_search_tool,
)

from langchain.tools import Tool

# Wrap classify function as a tool for the agent
classify_tool = Tool(
    name="classify_document",
    func=classify,
    description="Classify a raw document JSON and return {doc_type, period}",
)

# LLM for the agent
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

# Initialize the agent with available tools
_orchestrator = initialize_agent(
    [classify_tool, analysis_tool, db_search_tool, web_search_tool],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
)

def orchestrate(json_path: str) -> str:
    """Run the orchestrator agent on the given JSON path."""
    task = f"Analyze the document at {json_path}"
    return _orchestrator.run(task)

__all__ = ["orchestrate"]
