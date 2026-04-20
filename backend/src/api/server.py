import uuid
import logging
from dotenv import load_dotenv

# STEP 1: Load env vars FIRST
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

# STEP 2: Create app
app = FastAPI(
    title="Brand Guardian AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"
)

# STEP 3: Add middleware (must be after app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# STEP 4: Telemetry
from backend.src.api.telementry import setup_telemetry
setup_telemetry()

# STEP 5: Import workflow
from backend.src.graph.workflow import app as compliance_graph

# STEP 6: Logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logger = logging.getLogger("api-server")
logger.setLevel(logging.INFO)


# ========== DATA MODELS ==========

class AuditRequest(BaseModel):
    video_url: str

class ComplianceIssue(BaseModel):
    category: str
    severity: str
    description: str

class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    final_report: str
    compliance_results: List[ComplianceIssue]


# ========== ENDPOINTS ==========

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Brand Guardian AI"}

@app.post("/audit", response_model=AuditResponse)
async def audit_video(request: AuditRequest):
    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    logger.info(f"Received Audit Request: {request.video_url} (Session: {session_id})")

    initial_inputs = {
        "video_url": request.video_url,
        "video_id": video_id_short,
        "compliance_results": [],
        "errors": []
    }

    try:
        final_state = compliance_graph.invoke(initial_inputs)

        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id", video_id_short),
            status=final_state.get("final_status", "UNKNOWN"),
            final_report=final_state.get("final_report", "No report generated."),
            compliance_results=final_state.get("compliance_results", [])
        )

    except Exception as e:
        logger.error(f"Audit Failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow Execution Failed: {str(e)}"
        )


#  STEP 9: RUN INSTRUCTIONS (IN COMMENTS) 
'''
To execute: 
uv run uvicorn backend.src.api.server:app --reload

Command breakdown:
- uv run          = Run with UV package manager
- uvicorn         = ASGI server (like Gunicorn but async)
- backend.src.api.server:app = Python path to FastAPI app object
- --reload        = Auto-restart server when code changes (dev mode)

Server starts at: http://localhost:8000

Access points:
- API Docs:    http://localhost:8000/docs (interactive Swagger UI)
- Health:      http://localhost:8000/health
- Main API:    POST http://localhost:8000/audit
'''

'''
## How the API Works (Request Flow)
```
1. Client sends POST request:
   POST http://localhost:8000/audit
   Body: {"video_url": "https://youtu.be/abc123"}
   
2. FastAPI receives request:
   - Validates request matches AuditRequest model
   - Calls audit_video() function
   
3. audit_video() executes:
   - Generates session ID
   - Prepares initial_inputs dict
   - Calls compliance_graph.invoke()
   
4. LangGraph workflow runs:
   START → Indexer → Auditor → END
   
5. Function returns AuditResponse:
   - FastAPI validates response matches model
   - Converts Pydantic object to JSON
   - Sends HTTP response to client
   
6. Azure Monitor captures:
   - Request duration
   - HTTP status code
   - Any errors
   - Graph execution trace

'''