"""
OCR helper sin Poppler
----------------------
Usa PyMuPDF (fitz) para rasterizar páginas a PNG y pytesseract para OCR.
"""

from pathlib import Path
from typing import List
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from langchain_core.documents import Document
import io
# backend/loaders/ocr_pdf.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def ocr_pdf(path: Path, dpi: int = 400, lang: str = "spa+eng") -> List[Document]:
    """Rasteriza con PyMuPDF page.get_pixmap y pasa Tesseract."""
    doc_mupdf = fitz.open(path.as_posix())
    docs: List[Document] = []

    zoom = dpi / 72  # 72 dpi es 1:1 en PyMuPDF
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc_mupdf, 1):
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang)
        docs.append(Document(page_content=text, metadata={"page": i}))

    return docs
