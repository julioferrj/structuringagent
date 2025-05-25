from langchain.tools import Tool


def db_search(query: str) -> str:
    """Placeholder internal DB search."""
    # In a real system, this would query a database.
    return f"DB results for: {query}"


# Exported tool

db_search_tool = Tool(
    name="db_search",
    func=db_search,
    description="Search internal database with a query string",
)

__all__ = ["db_search_tool", "db_search"]
