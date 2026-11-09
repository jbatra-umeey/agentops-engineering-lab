# AgentOps Engineering Lab

**An original, executable FDE course companion: 25 concepts, 25 labs, one coherent incident-response domain.**

This is an educational reference implementation, **not a certified production service**. It runs without API keys using deterministic simulated telemetry; a live model adapter is an extension exercise. It intentionally does not execute remediation actions on infrastructure.

## What runs today

- FastAPI API with incident investigation, checkpoint inspection, human approval and audit events
- Bounded plan/act/observe loop, deterministic specialist routing, typed tool registry, idempotency keys, injection checks, retry budgets, state transitions, SQLite checkpointing, basic evaluation
- Tests, Dockerfile, Docker Compose, GitHub Actions CI, and original Mermaid architecture and sequence diagrams
- 25 individually authored learning chapters with design trade-offs, workflows, failure modes, exercises, and review questions

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn agentops.api:app --reload
```

Try:
```bash
curl -s -X POST http://localhost:8000/incidents/investigate -H 'Content-Type: application/json' -d '{"incident_id":"INC-1042","service":"checkout-api","symptom":"Elevated 5xx error rate"}'
curl -s http://localhost:8000/incidents/INC-1042
curl -s -X POST http://localhost:8000/incidents/INC-1042/approve -H 'Content-Type: application/json' -d '{"approved":true,"reviewer":"oncall@example.test"}'
pytest -q
```

API docs: `http://localhost:8000/docs`. Checkpoints are stored in `./data/agentops.db` by default.

## Illustrated workflows and real-world examples

Every module includes an additional scenario-driven sequence diagram, decision flowchart, step-by-step explanation, example input/output, safety note, and interview challenge. Start with [the end-to-end illustrated workflow guide](docs/illustrated-workflows.md) for incident triage, approval, prompt injection, and evaluation. The diagrams describe learning patterns and may show target capabilities not yet implemented.

## Course map

See [the 25-module index](course/INDEX.md), [architecture](docs/architecture.md), [operational readiness](docs/production-readiness.md), [threat model](docs/threat-model.md), [evaluation guide](docs/evaluation.md), and [learning path](docs/learning-path.md).

## Honest implementation boundary

The demo implements a deterministic agent workflow, not autonomous LLM reasoning, a real MCP transport, vector retrieval, real external telemetry, or hardened multi-tenant security. The course teaches those patterns and provides implementation exercises. Do not deploy this reference API publicly without authentication, authorization, secret management, tenant isolation, and durable queue infrastructure.

## Originality

All instructional text, scenarios, and Mermaid diagrams in this repository were created for this course. The 25-item syllabus is based on commonly used industry terminology; the explanation, design, exercises, and artifacts are original.
