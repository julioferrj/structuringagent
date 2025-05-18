"""
splitter.py  –  Divide un RawDocument 'paquete_eeff' en balance, PyG, CF.
Ahora se apoya en el mismo YAML de alias que usa el clasificador.
"""

from pathlib import Path
from uuid import uuid4
import unicodedata, re, yaml
from typing import List

from backend.schemas.raw_doc import RawDocument

# ────────────────────── cargar alias del YAML ────────────────────── #
with open("config/aliases.yml", encoding="utf-8") as f:
    ALIAS = yaml.safe_load(f)

TARGET_TYPES = {"balance_general", "cuenta_resultados", "flujo_caja"}

# Normalizador igual que en classifier.py
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())

# Construye un diccionario {doc_type: [alias_norm, …]}
ALIAS_NORM = {
    t: [_norm(a) for a in aliases]
    for t, aliases in ALIAS.items()
    if t in TARGET_TYPES
}

def _guess_doc_type(text: str) -> str | None:
    n = _norm(text)
    for doc_type, aliases in ALIAS_NORM.items():
        if any(al in n for al in aliases):
            return doc_type
    return None

# ───────────────────────── función pública ───────────────────────── #
def split_paquete_eeff(raw_json_path: str | Path) -> List[str]:
    raw_path = Path(raw_json_path)
    raw = RawDocument.model_validate_json(raw_path.read_text(encoding="utf-8"))

    if raw.doc_type != "paquete_eeff":
        return []

    sections: dict[str, list[str]] = {}
    current = None

    for page in raw.content.get("pages", []):
        snippet = "\n".join(page.split("\n")[:20])      # primeras 20 líneas
        maybe = _guess_doc_type(snippet)
        if maybe:
            current = maybe
            sections.setdefault(current, [])
        if current:
            sections[current].append(page)

    out_paths: list[str] = []
    for doc_type, pages in sections.items():
        child = raw.copy()
        child.id = str(uuid4())
        child.doc_type = doc_type
        child.content = {"pages": pages}

        out = Path("reports") / "raw" / f"{child.id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(child.model_dump_json(indent=2), encoding="utf-8")
        out_paths.append(out.as_posix())

    return out_paths
