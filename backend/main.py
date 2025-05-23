from fastapi import FastAPI, UploadFile, File, HTTPException
import json
from pathlib import Path
import shutil
import os
from dotenv import load_dotenv

# Carga variables de entorno (OPENAI_API_KEY, etc.)
load_dotenv()

from backend.loaders.ingest import extract_raw_json
from backend.agents import (
    classify_tool,
    get_orchestrator_agent,
    summarize_tool,
)
from backend.schemas import AggregateRequest


from backend.tools import splitter_tool


app = FastAPI(
    title="Financial Diagnostics API",
    version="0.1.0",
    description="Sube documentos y obtén JSON crudo + clasificación con LangChain",
)

# === Carpetas donde guardaremos datos ===
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Instantiate the orchestrator agent once at startup
orchestrator_agent = get_orchestrator_agent()


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
    """Clasifica y divide un documento si es un paquete de EEFF."""
    try:
        output = orchestrator_agent.invoke({"input": json_path})
        if isinstance(output, str):
            try:
                result = json.loads(output)
            except json.JSONDecodeError:
                result = {"result": output}
        else:
            result = output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")
    return result


@app.post("/aggregate")
async def aggregate(request: AggregateRequest):
    """Aggrega la información de varios documentos."""
    try:
        summary = summarize_tool.run(request.json_paths)
        result = {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aggregation error: {e}")
    return result
