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

# ───────── Exports ───────── #
__all__ = [
    "splitter_tool",
]
