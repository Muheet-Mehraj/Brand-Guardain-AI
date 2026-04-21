# Brand Guardian AI

### Azure Multi-Modal Compliance Ingestion Engine Using LangGraph

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green)](https://langchain-ai.github.io/langgraph/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI%20%7C%20AI%20Search%20%7C%20Video%20Indexer-0078D4)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-teal)](https://fastapi.tiangolo.com)
[![Deploy](https://img.shields.io/badge/Deployed-Render-purple)](https://brand-guardain-ai.onrender.com)

---

## Demo

🎬 **[Watch Full Demo](https://www.loom.com/share/82143d4ffb42488986fbbfdfc6356827)**

> The live deployment requires active Azure trial credentials (Video Indexer, OpenAI, AI Search).
> To run locally, clone the repo, configure `.env` with your Azure keys, and follow the setup instructions below.

## Overview

Brand Guardian AI is a production-grade multi-modal compliance auditing system that analyzes video content against regulatory guidelines using large language models and retrieval-augmented generation (RAG).

The system automates video ingestion, extracts transcripts and on-screen text using Azure Video Indexer, retrieves relevant compliance rules from a vector knowledge base, and generates structured audit reports that classify violations by category and severity.

A typical use case involves reviewing sponsored influencer content before publication. Instead of manual review, a brand team submits a YouTube URL and receives a structured PASS/FAIL compliance report with detailed findings in minutes.

---

## Architecture

![Architecture Diagram](./docs/Architecture.png)

**Pipeline:** `YouTube URL → yt-dlp Download → Azure Video Indexer (OCR + Transcript) → Azure AI Search (RAG) → GPT-4o Audit → Structured Report`

---

## Key Capabilities

- Multi-modal ingestion of both spoken content and on-screen text from videos
- Retrieval-augmented compliance auditing grounded in regulatory documents
- Structured JSON output with typed fields for category, severity, and description
- Dual execution paths via CLI and REST API
- End-to-end observability using Azure Monitor and LangSmith
- Graceful error handling across indexing and auditing stages
- CI/CD deployment via GitHub Actions

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Azure OpenAI (GPT-4o) |
| Embeddings | Azure OpenAI (text-embedding-3-small) |
| Vector DB | Azure AI Search |
| Video Processing | Azure Video Indexer |
| Backend | FastAPI |
| Frontend | Vanilla HTML/CSS/JS |
| Observability | Azure Monitor, LangSmith |
| Deployment | Render (app), GitHub Actions (CI/CD) |
| Package Manager | uv |

---

## System Design Notes

- Workflow orchestration via LangGraph maintains deterministic execution order
- RAG architecture grounds outputs in actual compliance documents — not hallucinations
- Separation of ingestion, retrieval, and auditing improves modularity and testability
- Typed state management (`VideoAuditState`) ensures reliable data flow between nodes
- Cloud-native design using Azure managed services throughout

---

## Prerequisites

- Python 3.11+
- `uv` package manager
- Azure account with:
  - Azure OpenAI (`gpt-4o`, `text-embedding-3-small`)
  - Azure AI Search
  - Azure Video Indexer
  - Azure Application Insights (optional)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Muheet-Mehraj/Brand-Guardain-AI.git
cd Brand-Guardain-AI
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

```env
# Azure OpenAI (GPT-4o)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

# Azure OpenAI (Embeddings - can be separate resource)
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-embedding-resource.cognitiveservices.azure.com/
AZURE_OPENAI_EMBEDDING_API_KEY=your-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=brand-compliance-rules

# Azure Video Indexer
AZURE_VI_ACCOUNT_ID=your-account-id
AZURE_VI_LOCATION=eastus
AZURE_VI_NAME=your-vi-resource-name
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

# Observability (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=brand-guardian-prod
```

---

## Index the Knowledge Base

Place compliance PDFs in `backend/data/` then run:

```bash
uv run python scripts/index_document.py
```

---

## Running the Application

### CLI

```bash
uv run python main.py
```

### API Server

```bash
uv run uvicorn backend.src.api.server:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Frontend UI |
| `/audit` | POST | Submit video for audit |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

---

## Example Response

```json
{
  "session_id": "c11dc65f-660a-4c91-aa24-ba07a8601530",
  "video_id": "vid_c11dc65f",
  "status": "FAIL",
  "final_report": "The advertisement contains critical compliance issues including potentially misleading claims and lack of transparency regarding celebrity endorsement.",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "The claim 'Sunscreen you can't see' could be misleading as it implies invisibility without scientific substantiation."
    },
    {
      "category": "Endorsement Transparency",
      "severity": "MEDIUM",
      "description": "No clear disclosure of paid partnership, which may violate FTC guidelines."
    }
  ]
}
```

---

## Project Structure

```text
Brand-Guardain-AI/
├── backend/
│   └── src/
│       ├── graph/
│       │   ├── nodes.py        # Indexer & Auditor nodes
│       │   ├── state.py        # VideoAuditState schema
│       │   └── workflow.py     # LangGraph DAG
│       ├── services/
│       │   └── video_indexer.py # Azure VI connector
│       └── api/
│           ├── server.py       # FastAPI app
│           └── telemetry.py    # Azure Monitor setup
├── frontend/
│   └── index.html              # Single-page UI
├── scripts/
│   └── index_document.py       # PDF ingestion pipeline
├── docs/
│   └── Architecture.png
├── main.py                     # CLI entry point
├── pyproject.toml
├── requirements.txt
└── .github/
    └── workflows/
        └── deploy.yml          # GitHub Actions CI/CD
```

---

## Graph State

```python
class VideoAuditState(TypedDict):
    video_url: str
    video_id: str
    transcript: Optional[str]
    ocr_text: List[str]
    compliance_results: Annotated[List[ComplianceIssue], operator.add]
    final_status: str
    final_report: str
    errors: Annotated[List[str], operator.add]
```

---

## Observability

- **Azure Application Insights** — HTTP request tracking, latency metrics, error logging
- **LangSmith** — node-level tracing, token usage, LLM call debugging
- **Render Logs** — real-time deployment and runtime logs

---

## Limitations

- Video processing is synchronous and takes ~2 minutes end to end
- Only YouTube URLs are currently supported
- Knowledge base updates require manual re-indexing
- Free tier hosting sleeps after inactivity

---

## Future Improvements

- Async processing with webhook callbacks
- Batch video auditing
- Multi-platform video support (Instagram Reels, TikTok)
- Human review interface with annotation tools
- Automated knowledge base updates from regulatory feeds

---

## Knowledge Base

Compliance rules are sourced from PDFs in `backend/data/`, including FTC guidelines and platform-specific advertising specifications. Additional documents can be added and re-indexed at any time.