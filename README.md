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