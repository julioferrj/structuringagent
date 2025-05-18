"""
Registro central de herramientas (Tools) reutilizables.
Aquí se exponen para que los Agents o FastAPI las importen.
"""

from langchain_core.tools import Tool

# ───────── Splitter Tool ───────── #
from .splitter import split_paquete_eeff

splitter_tool = Tool(
    name="split_paquete_eeff",
    func=split_paquete_eeff,
    description=(
        "Divide un RawDocument cuyo doc_type sea 'paquete_eeff' en "
        "sub-documentos balance_general, cuenta_resultados y/o flujo_caja. "
        "Devuelve una lista de rutas JSON hijas."
    ),
)

# ───────── DB Search Tool ───────── #
from .db_search_tool import db_search

db_search_tool = Tool(
    name="db_search",
    func=db_search,
    description="Search structured data from the internal database.",
)

# ───────── Web Search Tool ───────── #
from .web_search_tool import web_search

web_search_tool = Tool(
    name="web_search",
    func=web_search,
    description="Perform a web search for the given query.",
)

# ───────── Analysis Tool ───────── #
from .analysis_tool import analyze_text

analysis_tool = Tool(
    name="analyze_text",
    func=analyze_text,
    description="Analyze text and return a short summary.",
)

# ───────── Exports ───────── #
__all__ = [
    "splitter_tool",
    "db_search_tool",
    "web_search_tool",
    "analysis_tool",
]
