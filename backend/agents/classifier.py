"""
Clasificador de estados financieros
-----------------------------------
Entrada : RawDocument
Salida  : {"doc_type": <enum>, "period": <str|null>}
"""

from pathlib import Path, PurePath
import json, re, yaml, unicodedata
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from backend.schemas.raw_doc import RawDocument


# ────────────────────────── Alias y utilidades ──────────────────────────── #
with open("config/aliases.yml", encoding="utf-8") as f:
    ALIAS_MAP: Dict[str, list[str]] = yaml.safe_load(f)

VALID_TYPES = list(ALIAS_MAP.keys())

YEAR_RE = re.compile(r"20\d{2}")
Q_RE = re.compile(r"(20\d{2})[ _-]?(?:q|t)([1-4])", re.I)


def _norm(s: str | int | float) -> str:
    """
    Normaliza: convierte a str, quita tildes y caracteres no alfanuméricos,
    pasa a minúsculas.
    """
    s = str(s)                                     # ← convierte números a texto
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())



def _period_from_name(name: str) -> str | None:
    stem = PurePath(name).stem.lower()
    if (m := Q_RE.search(stem)):
        y, q = m.groups()
        return f"{y}Q{q}"
    if (m := YEAR_RE.search(stem)):
        return m.group(0)
    return None


def _alias_scan(text: str) -> str | None:
    norm_text = _norm(text)
    hits = {
        t: sum(_norm(alias) in norm_text for alias in aliases)
        for t, aliases in ALIAS_MAP.items() if aliases
    }
    found = [t for t, c in hits.items() if c > 0 and t != "paquete_eeff"]
    if len(found) == 1:
        return found[0]
    if len(found) >= 2:
        return "paquete_eeff"
    return None


# ────────────────────────── LLM few-shot ──────────────────────────── #
FEW_SHOTS = [
    ('{"doc_type":"balance_general","period":"2024"}',
     "FILENAME: BALANCE_2024.pdf\nCONTENT:\nBALANCE GENERAL al 31-12-2024"),
    ('{"doc_type":"cuenta_resultados","period":"2023"}',
     "FILENAME: PyG 2023.pdf\nCONTENT:\nPyG 2023 – Cuenta de Resultados"),
    ('{"doc_type":"flujo_caja","period":"2022"}',
     "FILENAME: CASH FLOW 2022.pdf\nCONTENT:\nCASH FLOW STATEMENT 2022"),
    ('{"doc_type":"paquete_eeff","period":"2021"}',
     "FILENAME: EEFF completos 2021.pdf\nCONTENT:\nBALANCE SHEET …\nINCOME STATEMENT …\nCASH FLOW STATEMENT …"),
]

_base = [SystemMessage(content="Eres analista contable. Devuelve SOLO JSON {doc_type, period}")]
for ans, usr in FEW_SHOTS:
    _base.extend([HumanMessage(content=usr), SystemMessage(content=ans)])

PROMPT = ChatPromptTemplate.from_messages(_base + [HumanMessage(content="{payload}")])

llm = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
)


# ────────────────────────── Función pública ──────────────────────────── #
def classify(raw_json_path: str | Path) -> Dict[str, Any]:
    raw = RawDocument.model_validate_json(Path(raw_json_path).read_text(encoding="utf-8"))

    # ---------- 1) alias por nombre de archivo -------------------------- #
    alias_name = _alias_scan(_norm(raw.filename))
    if alias_name:
        return {
            "doc_type": alias_name,
            "period": _period_from_name(raw.filename)
        }

    # ---------- 2) alias por texto corto -------------------------------- #
    pages: List[str] = raw.content.get("pages", [])
    text_short = "\n".join(pages[:2] + pages[-2:])[:15_000]
    alias_text = _alias_scan(text_short)
    if alias_text:
        return {
            "doc_type": alias_text,
            "period": _period_from_name(raw.filename)
        }

    # ---------- 3) LLM few-shot ---------------------------------------- #
    cand_period = _period_from_name(raw.filename)
    payload = (
        f"FILENAME: {raw.filename}\n"
        f"candidate_period: {cand_period}\n\n"
        f"CONTENT_EXCERPT:\n{text_short}"
    )
    response_txt = (PROMPT | llm).invoke({"payload": payload}).content
    try:
        out = json.loads(response_txt)
    except json.JSONDecodeError:
        out = {}

    # Garantiza claves
    doc_type = out.get("doc_type", "otro")
    period = out.get("period")

    # ---------- 4) fallback alias sobre TODO el texto ------------------- #
    if doc_type == "otro":
        alias_full = _alias_scan("\n".join(pages))
        if alias_full:
            doc_type = alias_full

    if period in (None, "", "null"):
        period = cand_period

    if doc_type not in VALID_TYPES:
        doc_type = "otro"

    return {"doc_type": doc_type, "period": period}
