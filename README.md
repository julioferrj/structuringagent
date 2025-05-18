# Financial Documents Processing API

A FastAPI application for processing financial documents using LangChain.

## Features

- Upload financial documents (PDF, Excel, CSV)
- Extract structured data from documents
- Classify documents by type and period
- Split financial packages into constituent parts

## Setup

1. Clone the repository
2. Create a virtual environment:
```
python -m venv venv
```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
```
pip install -r requirements.txt
```
5. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

Start the FastAPI server:
```
uvicorn backend.main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

## API Endpoints

- `POST /upload`: Upload a financial document
- `POST /classify`: Classify a processed document
- `POST /split`: Split a financial package into constituent parts
- `POST /orchestrate`: Full pipeline – upload, classify and split in one call
- `POST /aggregate`: Combine several classified documents into one dataset

## Orchestrator

The orchestrator endpoint chains together the standard ingestion steps. A file
is uploaded, converted to a raw JSON document, classified by type/period and
then split if it is a financial package. The response is a list of JSON files
ready for analysis.

Example request:

```bash
curl -X POST -F "file=@/path/to/report.pdf" \
     http://localhost:8000/orchestrate
```

The service requires the `OPENAI_API_KEY` variable in your `.env` file just as
the other endpoints.

## Aggregation

The aggregation endpoint collects multiple processed documents and merges their
data. Pass a JSON array with the paths returned by the orchestrator or the
upload endpoint. The result is a consolidated structure that can be consumed by
other tools.

Example request:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"sources": ["reports/raw/1.json", "reports/raw/2.json"]}' \
     http://localhost:8000/aggregate
```

This operation also relies on the `OPENAI_API_KEY` environment variable.
