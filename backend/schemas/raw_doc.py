from pydantic import BaseModel
from typing import Literal, Dict, Any


class RawDocument(BaseModel):
    """
    Representa el JSON crudo que almacenamos tras la ingesta.
    """
    id: str
    filename: str
    doc_type: Literal[
        "balance_general",
        "cuenta_resultados",
        "flujo_caja",
        "paquete_eeff",   # ← nuevo
        "otro",
    ]
    period: str | None  # 2024, 2024Q1, etc.
    content: Dict[str, Any]  # texto/tablas extraídos
