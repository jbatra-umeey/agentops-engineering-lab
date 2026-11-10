# Production readiness gap register

| Area | Current lab | Production implementation requirement |
|---|---|---|
| Reasoning | Deterministic planner | Provider abstraction, bounded LLM inference, JSON schema validation, model fallback |
| Tools | Local fixtures | Real authenticated adapters, rate limits, circuit breakers, strict allowlists |
| MCP | Course design | Version-pinned MCP client/server with capability and trust-boundary checks |
| Retrieval | Static runbook | Versioned source ingestion, hybrid retrieval, ACL filtering, citations |
| Auth | None | OIDC, RBAC/ABAC, tenant-scoped service identities |
| Persistence | SQLite | Postgres transactional state, optimistic concurrency, outbox, backups |
| Execution | Proposal only | Separate executor with signed approvals, change windows, dry run, rollback |
| Observability | Trace ID and audit list | OpenTelemetry spans, metrics, log correlation, redaction and retention |
| Evals | Deterministic assertions | Golden datasets, trajectory graders, adversarial red-team, drift monitoring |
| Deploy | Local Docker | Image signing, SAST/DAST, SBOM, IaC, autoscaling, SLOs, disaster recovery |

## Recommended release gates

1. Establish an incident golden set with success and prohibited-action assertions.
2. Demonstrate zero unauthorized writes in negative tests.
3. Load-test concurrent checkpoint updates and idempotency.
4. Verify trace propagation, PII redaction and incident audit completeness.
5. Run shadow mode before human-approved canary rollout.
