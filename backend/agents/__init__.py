from langchain.tools import Tool
from .classifier import classify

# Exponemos el tool para que otros módulos puedan importarlo
classify_tool = Tool(
    name="classify_document",
    func=classify,
    description=(
        "Clasifica un documento crudo (JSON) y devuelve dict "
        "{doc_type, period}. Input: ruta del JSON."
    ),
)

__all__ = ["classify_tool"]
