from fastapi import FastAPI, HTTPException

from .core import (
    TOOL_SCHEMAS,
    ApprovalRequest,
    Checkpoints,
    IncidentRequest,
    approve,
    investigate,
)

app = FastAPI(title="AgentOps Engineering Lab", version="0.1.0")
db = Checkpoints()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tools")
def tools():
    return TOOL_SCHEMAS


@app.post("/incidents/investigate")
def start(req: IncidentRequest):
    try:
        return investigate(req, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@app.get("/incidents/{incident_id}")
def get(incident_id: str):
    state = db.load(incident_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Not found")
    return state


@app.post("/incidents/{incident_id}/approve")
def decide(incident_id: str, req: ApprovalRequest):
    try:
        state = approve(incident_id, req, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    if state is None:
        raise HTTPException(status_code=404, detail="Not found")
    return state
