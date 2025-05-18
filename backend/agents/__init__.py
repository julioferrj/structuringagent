from langchain.tools import Tool
from .classifier import classify
from .orchestrator import analyze
from .aggregator import aggregate

# Exponemos el tool para que otros módulos puedan importarlo
classify_tool = Tool(
    name="classify_document",
    func=classify,
    description=(
        "Clasifica un documento crudo (JSON) y devuelve dict "
        "{doc_type, period}. Input: ruta del JSON."
    ),
)

orchestrator_tool = Tool(
    name="analyze_document",
    func=analyze,
    description=(
        "Clasifica un RawDocument y, si corresponde, lo divide en sub-documentos. "
        "Input: ruta del JSON."
    ),
)

aggregator_tool = Tool(
    name="aggregate_documents",
    func=aggregate,
    description=(
        "Agrega metadatos de varios RawDocuments. "
        "Input: lista de rutas JSON."
    ),
)

__all__ = ["classify_tool", "orchestrator_tool", "aggregator_tool"]
