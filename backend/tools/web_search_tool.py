from langchain.tools import Tool


def web_search(query: str) -> str:
    """Placeholder web search."""
    # In a real system, this would call a search API.
    return f"Web results for: {query}"


web_search_tool = Tool(
    name="web_search",
    func=web_search,
    description="Search the web for additional context",
)

__all__ = ["web_search_tool", "web_search"]
