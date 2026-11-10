"""Deterministic teaching harness. No live model or real production actions."""

from __future__ import annotations

import os
import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    incident_id: str = Field(pattern=r"^[A-Za-z0-9_-]{3,64}$")
    service: str = Field(min_length=1, max_length=100)
    symptom: str = Field(min_length=3, max_length=500)


class ApprovalRequest(BaseModel):
    approved: bool
    reviewer: str = Field(min_length=3, max_length=120)


class AgentState(BaseModel):
    incident_id: str
    service: str
    symptom: str
    status: Literal[
        "investigating", "awaiting_approval", "approved", "rejected", "failed"
    ] = "investigating"
    steps: int = 0
    evidence: list[dict] = Field(default_factory=list)
    proposed_action: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit: list[dict] = Field(default_factory=list)


class Checkpoints:
    def __init__(self, path: str | None = None):
        self.path = path or os.environ.get("AGENTOPS_DB", "data/agentops.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, state TEXT NOT NULL)"
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def save(self, state: AgentState):
        with self._connect() as db:
            db.execute(
                "INSERT INTO incidents(id,state) VALUES (?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state",
                (state.incident_id, state.model_dump_json()),
            )

    def load(self, incident_id: str) -> AgentState | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT state FROM incidents WHERE id=?", (incident_id,)
            ).fetchone()
        return AgentState.model_validate_json(row[0]) if row else None


TOOL_SCHEMAS = {
    "metrics": {
        "description": "Read simulated service error rate and latency; no side effects",
        "required": ["service"],
    },
    "logs": {
        "description": "Read sanitized simulated error log samples",
        "required": ["service"],
    },
    "runbook": {
        "description": "Retrieve a trusted internal diagnostic runbook excerpt",
        "required": ["service"],
    },
}


def tool_call(name: str, service: str) -> dict:
    if name not in TOOL_SCHEMAS:
        raise ValueError("Unknown tool")
    fixtures = {
        "metrics": {
            "error_rate_pct": 12.5,
            "p95_latency_ms": 1900,
            "baseline_error_rate_pct": 0.5,
        },
        "logs": {
            "samples": ["upstream timeout", "connection pool saturation"],
            "sample_count": 2,
        },
        "runbook": {
            "document_id": "RB-CHECKOUT-01",
            "guidance": "Check upstream saturation and rollback eligibility; require on-call approval for changes",
        },
    }
    return {"tool": name, "service": service, "result": fixtures[name]}


def suspicious(text: str) -> bool:
    return bool(
        re.search(
            r"ignore (all )?(previous|prior) instructions|reveal (the )?(system prompt|secrets)|disable (all )?guardrails",
            text,
            re.IGNORECASE,
        )
    )


def record(state: AgentState, event: str, **details):
    state.audit.append({"event": event, "timestamp": round(time.time(), 3), **details})


def investigate(
    request: IncidentRequest, db: Checkpoints, max_steps: int = 6
) -> AgentState:
    previous = db.load(request.incident_id)
    if previous:
        if previous.service != request.service or previous.symptom != request.symptom:
            raise ValueError("Incident ID already exists with different payload")
        return previous  # idempotent replay
    state = AgentState(**request.model_dump())
    if suspicious(request.symptom):
        state.status = "failed"
        record(state, "policy_rejected", reason="Potential prompt injection")
        db.save(state)
        return state
    plan = ["metrics", "logs", "runbook"]
    record(state, "plan_created", tools=plan)
    for name in plan:
        if state.steps >= max_steps:
            state.status = "failed"
            record(state, "step_budget_exceeded")
            break
        state.steps += 1
        try:
            evidence = tool_call(name, request.service)
            state.evidence.append(evidence)
            record(state, "tool_observed", tool=name, step=state.steps)
        except (ValueError, TimeoutError) as exc:
            record(state, "tool_failed", tool=name, error=str(exc))
            state.status = "failed"
            break
        db.save(state)  # checkpoint after each tool
    if state.status != "failed":
        state.proposed_action = "Investigate upstream saturation; consider rollback only after on-call review"
        state.status = "awaiting_approval"
        record(state, "approval_requested", action=state.proposed_action)
    db.save(state)
    return state


def approve(
    incident_id: str, decision: ApprovalRequest, db: Checkpoints
) -> AgentState | None:
    state = db.load(incident_id)
    if not state:
        return None
    if state.status != "awaiting_approval":
        raise ValueError("Incident is not awaiting approval")
    state.status = "approved" if decision.approved else "rejected"
    record(
        state, "human_decision", reviewer=decision.reviewer, approved=decision.approved
    )
    # Approval authorizes a proposal only; NO infrastructure changes are executed.
    db.save(state)
    return state
