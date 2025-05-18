"""
Extrae el contenido de Excel, CSV y PDF (vector o escaneado)
y guarda un JSON crudo en  reports/raw/<uuid>.json
"""

from pathlib import Path
from uuid import uuid4
from typing import List

import pandas as pd
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    CSVLoader,
    PyMuPDFLoader,        # texto vectorial rapidísimo
)
from backend.loaders.ocr_pdf import ocr_pdf
from backend.schemas.raw_doc import RawDocument

# ───────────────────────── Excel helper ───────────────────────── #
def _extract_excel(path: Path) -> dict:
    wb = pd.ExcelFile(path)
    preview = {}
    for sheet in wb.sheet_names:
        df = wb.parse(sheet, nrows=10, header=None)
        preview[sheet] = df.to_csv(index=False)
    return {"sheet_names": wb.sheet_names, "preview": preview}


# ─────────────────────── PDF loader helper ────────────────────── #
MIN_CHARS = 30  # umbral de texto útil por página


def _is_meaningful(pages: List) -> bool:
    """True si alguna página tiene > MIN_CHARS caracteres."""
    return any(len(d.page_content.strip()) > MIN_CHARS for d in pages)


def _load_pdf(path: Path):
    """
    1) PyMuPDF  → texto vectorial
    2) OCR local (pdf2image + pytesseract) si quedó vacío / casi vacío
    """
    # 1️⃣  PyMuPDF
    docs = PyMuPDFLoader(path.as_posix()).load()
    if _is_meaningful(docs):
        return docs

    # 2️⃣  OCR – último recurso (400 dpi)
    return ocr_pdf(path, dpi=400)


# ─────────────────────── Loader selector ─────────────────────── #
def _detect_loader(path: Path):
    ext = path.suffix.lower()
    if ext in {".xlsx", ".xls"}:
        return UnstructuredExcelLoader(path.as_posix())
    if ext == ".csv":
        return CSVLoader(path.as_posix())
    if ext == ".pdf":
        # devolvemos un closure para PDF
        return lambda: _load_pdf(path)
    raise ValueError(f"Formato no soportado: {ext}")


# ─────────────────────── Pipeline principal ───────────────────── #
def extract_raw_json(file_path: Path) -> Path:
    """
    Devuelve la ruta absoluta del JSON crudo generado.
    """
    suffix = file_path.suffix.lower()

    # 1. Metadatos Excel
    excel_meta = (
        _extract_excel(file_path) if suffix in {".xlsx", ".xls"} else None
    )

    # 2. Cargar documento
    loader = _detect_loader(file_path)
    docs = loader() if callable(loader) else loader.load()

    # 3. Verificación: ¿obtuvimos texto?
    if all(not d.page_content.strip() for d in docs):
        raise ValueError(
            "EXTRACTION_FAILED: No se pudo extraer texto del documento. "
            "Comprueba la calidad del archivo o usa un servicio OCR externo."
        )

    # 4. Empaquetar
    raw = RawDocument(
        id=str(uuid4()),
        filename=file_path.name,
        doc_type="otro",  # se clasificará luego
        period=None,
        content={
            "pages": [d.page_content for d in docs],
            **({"excel": excel_meta} if excel_meta else {}),
        },
    )

    # 5. Persistir
    out_path = Path("reports") / "raw" / f"{raw.id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(raw.model_dump_json(indent=2), encoding="utf-8")

    return out_path
