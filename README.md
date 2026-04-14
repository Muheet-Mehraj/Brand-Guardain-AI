# Brand Guardian AI
### Azure Multi-modal Compliance Ingestion Engine using LangGraph

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green)](https://langchain-ai.github.io/langgraph/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI%20%7C%20AI%20Search%20%7C%20Video%20Indexer-0078D4)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-teal)](https://fastapi.tiangolo.com)

---

## What is Brand Guardian AI?

Brand Guardian AI is an end-to-end automated compliance auditing system that analyzes YouTube videos against regulatory guidelines (FTC Endorsement Rules and YouTube Ad Specs). It downloads a video, extracts speech and on-screen text using Azure Video Indexer, retrieves the most relevant compliance rules from a vector knowledge base, and uses an LLM to generate a structured audit report — flagging violations by severity.

**Example use case:** A brand team wants to verify that a sponsored influencer video is FTC-compliant before publishing. Instead of manually reviewing the video, they submit the YouTube URL to Brand Guardian AI and receive a structured PASS/FAIL report within minutes.

---

## Architecture

```
[YouTube URL]
     │
     ▼
[Entry Points]
  main.py (CLI) ──────────────────────────────────────────────┐
  FastAPI /audit (API) ───────────────────────────────────────┤
                                                               ▼
                                               [LangGraph Workflow]
                                               ┌───────────────────────┐
                                               │  index_video_node     │──► Azure Blob Storage (temp)
                                               │  (yt-dlp + Azure VI)  │──► Azure Video Indexer
                                               │                       │◄── Transcript + OCR
                                               └──────────┬────────────┘
                                                          │
                                               ┌──────────▼────────────┐
                                               │  audit_content_node   │──► Azure AI Search (Vector DB)
                                               │  (RAG + LLM Auditor)  │──► Azure OpenAI (GPT-4o)
                                               │                       │◄── Compliance Report
                                               └───────────────────────┘
                                                          │
                                               [Structured Audit Report]
                                               PASS/FAIL + Violations + Summary

[Observability]
  Azure Application Insights ── Logs, metrics, request tracing
  LangSmith ─────────────────── LangGraph node-level debugging
```

---

## Features

- **Multi-modal ingestion** — extracts both audio transcript (speech-to-text) and on-screen text (OCR) from videos
- **RAG-powered auditing** — retrieves the most relevant regulatory rules before querying the LLM, grounding the audit in real guidelines
- **Structured output** — violations returned as typed JSON with `category`, `severity`, and `description` fields
- **Dual entry points** — CLI (`main.py`) for development, REST API (`/audit`) for production
- **Full observability** — Azure Monitor for infrastructure telemetry, LangSmith for LangGraph execution traces
- **Graceful error handling** — failures in video processing or auditing return structured error states without crashing the graph

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- An Azure account with the following resources provisioned:
  - Azure OpenAI (deployments: `gpt-4o` for chat, `text-embedding-3-small` for embeddings)
  - Azure AI Search (index created)
  - Azure Video Indexer account
  - Azure Blob Storage account
  - Azure Application Insights (optional, for telemetry)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/brand-guardian-ai.git
cd brand-guardian-ai
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy the example env file and fill in your Azure credentials:

```bash
cp .env.example .env
```

Required variables:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=brand-guardian-index

# Azure Video Indexer
AZURE_VI_ACCOUNT_ID=your-account-id
AZURE_VI_LOCATION=trial
AZURE_VI_NAME=your-vi-resource-name
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

# Azure Application Insights (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# LangSmith (optional)
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
```

### 4. Index the knowledge base

**This step is required before running the auditor.** It reads the compliance PDFs, chunks them, generates embeddings, and loads them into Azure AI Search.

```bash
uv run python scripts/index_documents.py
```

Expected output:
```
INFO - Found 2 PDFs to process...
INFO - -> Split into 11 chunks.
INFO - -> Split into 26 chunks.
INFO - ✅ Indexing Complete! Total chunks indexed: 37
```

> This only needs to be run once, or whenever the knowledge base PDFs are updated.

---

## Running the Application

### CLI (Development)

Runs a single audit against a hardcoded YouTube URL. Useful for testing the full pipeline end-to-end.

```bash
uv run python main.py
```

### API Server (Production)

```bash
uv run uvicorn backend.src.api.server:app --reload
```

The server starts at `http://localhost:8000`.

| Endpoint | Method | Description |
|---|---|---|
| `/audit` | POST | Submit a YouTube URL for compliance audit |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive Swagger UI |

**Example request:**

```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtu.be/your-video-id"}'
```

**Example response:**

```json
{
  "session_id": "ce6c43bb-c71a-4f16-a377-8b493502fee2",
  "video_id": "vid_ce6c43bb",
  "status": "FAIL",
  "final_report": "The video contains 2 critical violations related to undisclosed sponsorship and absolute guarantee claims.",
  "compliance_results": [
    {
      "category": "FTC Disclosure",
      "severity": "CRITICAL",
      "description": "No sponsored content disclosure detected despite product endorsement language."
    },
    {
      "category": "Claim Validation",
      "severity": "WARNING",
      "description": "Use of absolute language ('guaranteed results') without substantiation."
    }
  ]
}
```

---

## Project Structure

```
brand-guardian-ai/
├── backend/
│   └── src/
│       ├── graph/
│       │   ├── nodes.py          # index_video_node, audit_content_node
│       │   ├── state.py          # VideoAuditState, ComplianceIssue TypedDicts
│       │   └── workflow.py       # LangGraph DAG definition
│       ├── services/
│       │   └── video_indexer.py  # Azure Video Indexer client
│       └── api/
│           ├── server.py         # FastAPI app, /audit endpoint
│           └── telemetry.py      # Azure Monitor OpenTelemetry setup
├── data/
│   ├── ftc-influencer-guide.pdf
│   └── youtube-ad-specs.pdf
├── scripts/
│   └── index_documents.py        # One-time knowledge base indexer
├── tests/
├── main.py                       # CLI entry point
├── pyproject.toml
└── Dockerfile
```

---

## Knowledge Base

The auditor's compliance rules are sourced from two documents in `data/`:

| Document | Source | Coverage |
|---|---|---|
| FTC Disclosures 101 for Social Media Influencers | U.S. Federal Trade Commission | Sponsorship disclosures, material connections, endorsement honesty |
| YouTube Ad Specs 2025 | Mega Digital / Google | Ad format specs, resolution, length, safe zones, CTA rules |

To add new compliance documents, place PDFs in `data/` and re-run `scripts/index_documents.py`.

---

## Graph State

The LangGraph workflow passes a single typed state object between nodes:

```python
class VideoAuditState(TypedDict):
    video_url: str
    video_id: str
    transcript: Optional[str]         # Populated by index_video_node
    ocr_text: List[str]               # Populated by index_video_node
    video_metadata: Dict[str, Any]    # Duration, platform, etc.
    compliance_results: Annotated[List[ComplianceIssue], operator.add]  # Append-only
    final_status: str                 # PASS | FAIL
    final_report: str                 # LLM-generated markdown summary
    errors: Annotated[List[str], operator.add]  # Append-only error log
```

`operator.add` on `compliance_results` and `errors` means multiple nodes can append to these lists without overwriting each other — the correct LangGraph pattern for accumulating results.

---

## Observability

| Tool | Purpose | Access |
|---|---|---|
| Azure Application Insights | HTTP request traces, latency, error rates, dependency calls (Azure Search, OpenAI) | Azure Portal → Application Insights |
| LangSmith | Node-level LangGraph execution traces, LLM input/output, token usage | smith.langchain.com |

Telemetry is optional — the application runs normally if `APPLICATIONINSIGHTS_CONNECTION_STRING` is not set.

---

## Running Tests

```bash
uv run pytest tests/
```

---

## Known Limitations

- Video processing via Azure Video Indexer typically takes 2–5 minutes per video. The current API call is synchronous and will hold the connection open during this time. For production, consider an async job queue pattern (submit → poll for results).
- Only YouTube URLs are currently supported as video sources.
- The knowledge base must be manually re-indexed when compliance documents are updated.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM + Embeddings | Azure OpenAI (GPT-4o + text-embedding-3-small) |
| Vector Store | Azure AI Search |
| Video Processing | Azure Video Indexer + yt-dlp |
| API | FastAPI + Uvicorn |
| Observability | Azure Application Insights + LangSmith |
| Package Management | uv |
