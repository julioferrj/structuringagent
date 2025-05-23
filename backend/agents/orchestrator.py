from __future__ import annotations

"""Orchestrator agent with classification, retrieval and analysis tools."""

from typing import List

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from backend.agents.classifier import classify
from backend.tools import db_search_tool, web_search_tool, analysis_tool


# ----- Tool definitions ----------------------------------------------------
classify_tool = Tool(
    name="classify_document",
    func=classify,
    description="Classify a RawDocument JSON file into doc_type and period",
)


def _retrieve(query: str) -> str:
    """Retrieve data both from the DB and the web."""
    db_res = db_search_tool.run(query)
    web_res = web_search_tool.run(query)
    return f"DB:\n{db_res}\nWEB:\n{web_res}"


retrieve_tool = Tool(
    name="retrieve_data",
    func=_retrieve,
    description="Search internal DB and the web for the given query",
)

# analysis_tool is re-exported from backend.tools


# ----- Agent factory -------------------------------------------------------

def get_orchestrator_agent() -> AgentExecutor:
    """Return an AgentExecutor with access to the defined tools."""
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    tools: List[Tool] = [classify_tool, retrieve_tool, analysis_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    "You are a helpful assistant for processing financial documents."
                )
            ),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content="{input}"),
        ]
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


# Pre-created agent and Tool wrapper ---------------------------------------
_agent_executor = get_orchestrator_agent()


def _run_orchestrator(json_path: str) -> str:
    return _agent_executor.run(json_path)


orchestrator_tool = Tool(
    name="orchestrate",
    func=_run_orchestrator,
    description="Full pipeline: classify, retrieve info and analyze a document",
)
