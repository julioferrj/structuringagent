from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import os
from dotenv import load_dotenv

# Carga variables de entorno (OPENAI_API_KEY, etc.)
load_dotenv()

from backend.loaders.ingest import extract_raw_json
from backend.agents import classify_tool, orchestrate, aggregate as aggregate_analyses


from backend.tools import splitter_tool




app = FastAPI(
    title="Financial Diagnostics API",
    version="0.1.0",
    description="Sube documentos y obtén JSON crudo + clasificación con LangChain",
)

# === Carpetas donde guardaremos datos ===
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



@app.post("/split")
def split(json_path: str):
    """
    Ejecuta el splitter sobre el paquete_eeff indicado.
    """
    return {"children": splitter_tool(json_path)}
# ---------- ENDPOINTS ---------------------------------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Sube un archivo (Excel, CSV, PDF) y devuelve la ruta del JSON crudo."""
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        json_path = extract_raw_json(dest)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "raw_json": str(json_path)}


@app.post("/classify")
async def classify(json_path: str):
    """
    Clasifica un JSON crudo usando un LLM:
    - tipo de documento (balance_general | cuenta_resultados | flujo_caja | otro)
    - periodo
    """
    try:
        result = classify_tool.run(json_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")
    return result


@app.post("/analyze")
async def analyze(json_path: str):
    """Run the orchestrator agent on a raw JSON document."""
    try:
        result = orchestrate(json_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")
    return {"analysis": result}


from pydantic import BaseModel
from typing import List


class AggregateRequest(BaseModel):
    analyses: List[str]


@app.post("/aggregate")
async def aggregate(req: AggregateRequest):
    """Aggregate multiple analysis strings into a summary."""
    try:
        summary = aggregate_analyses(req.analyses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aggregation error: {e}")
    return {"summary": summary}
