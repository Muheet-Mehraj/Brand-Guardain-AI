# Brand Guardian AI

### Azure Multi-Modal Compliance Ingestion Engine Using LangGraph

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green)](https://langchain-ai.github.io/langgraph/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI%20%7C%20AI%20Search%20%7C%20Video%20Indexer-0078D4)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-teal)](https://fastapi.tiangolo.com)

---

## Overview

Brand Guardian AI is a production-grade multi-modal compliance auditing system that analyzes video content against regulatory guidelines using large language models and retrieval-augmented generation (RAG). The system automates video ingestion, extracts transcripts and on-screen text using Azure Video Indexer, retrieves relevant compliance rules from a vector knowledge base, and generates structured audit reports that classify violations by category and severity.

A typical use case involves reviewing sponsored influencer content before publication. Instead of manual review, a brand team can submit a YouTube URL and receive a structured PASS/FAIL compliance report with detailed findings.

---

## Architecture

![Architecture Diagram](./docs/architecture.png)

```text
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

## Key Capabilities

* Multi-modal ingestion of both spoken content and on-screen text from videos
* Retrieval-augmented compliance auditing grounded in regulatory documents
* Structured JSON output with typed fields for category, severity, and description
* Dual execution paths via CLI and REST API
* End-to-end observability using Azure Monitor and LangSmith
* Graceful error handling across indexing and auditing stages

---

## System Design Notes

* Workflow orchestration is handled using LangGraph to maintain deterministic execution
* RAG architecture ensures outputs are grounded in compliance documents
* Separation of ingestion, retrieval, and auditing improves modularity
* Typed state management ensures reliable data flow between nodes
* Cloud-native design using Azure managed services

---

## Prerequisites

* Python 3.12+
* `uv` package manager
* Azure account with:

  * Azure OpenAI (`gpt-4o`, `text-embedding-3-small`)
  * Azure AI Search
  * Azure Video Indexer
  * Azure Blob Storage
  * Azure Application Insights (optional)

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

```bash
cp .env.example .env
```

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=brand-guardian-index

AZURE_VI_ACCOUNT_ID=your-account-id
AZURE_VI_LOCATION=trial
AZURE_VI_NAME=your-vi-resource-name
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
```

---

## Index the Knowledge Base

```bash
uv run python scripts/index_documents.py
```

---

## Running the Application

### CLI

```bash
uv run python main.py
```

### API

```bash
uv run uvicorn backend.src.api.server:app --reload
```

Available endpoints:

| Endpoint  | Method | Description            |
| --------- | ------ | ---------------------- |
| `/audit`  | POST   | Submit video for audit |
| `/health` | GET    | Health check           |
| `/docs`   | GET    | Swagger UI             |

---

## Example Response

```json
{
  "status": "FAIL",
  "final_report": "The video contains violations related to sponsorship disclosure and unsupported claims.",
  "compliance_results": [
    {
      "category": "FTC Disclosure",
      "severity": "CRITICAL",
      "description": "Missing sponsorship disclosure."
    }
  ]
}
```

---

## Project Structure

```text
brand-guardian-ai/
├── backend/
│   └── src/
│       ├── graph/
│       ├── services/
│       └── api/
├── data/
├── docs/
│   └── architecture.png
├── scripts/
├── tests/
├── main.py
├── pyproject.toml
└── Dockerfile
```

---

## Knowledge Base

Compliance rules are sourced from documents in `data/`, including FTC guidelines and YouTube advertising specifications. Additional documents can be added and indexed as needed.

---

## Graph State

```python
class VideoAuditState(TypedDict):
    video_url: str
    transcript: Optional[str]
    ocr_text: List[str]
    compliance_results: List
    final_status: str
    final_report: str
```

---

## Observability

* Azure Application Insights for monitoring and tracing
* LangSmith for workflow-level debugging and LLM tracing

---

## Limitations

* Video processing is synchronous and may take several minutes
* Only YouTube URLs are supported
* Knowledge base updates require manual re-indexing

---

## Future Improvements

* Asynchronous processing pipeline
* Batch video auditing
* Multi-platform video support
* Human review interface

---

## Tech Stack

| Layer            | Technology               |
| ---------------- | ------------------------ |
| Orchestration    | LangGraph                |
| LLM              | Azure OpenAI             |
| Vector DB        | Azure AI Search          |
| Backend          | FastAPI                  |
| Video Processing | Azure Video Indexer      |
| Observability    | Azure Monitor, LangSmith |
| Package Manager  | uv                       |
