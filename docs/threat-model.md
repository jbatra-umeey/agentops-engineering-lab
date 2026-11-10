# Threat model

**Assets:** credentials, incident metadata, operational tools, remediation privileges, runbook content.

**Trust boundaries:** user input -> agent; retrieved text -> model context; model decision -> tool invocation; approval -> execution; tenant -> tenant.

**Threats and mitigations:** prompt injection (taint retrieved content and prohibit instruction promotion), tool escalation (least privilege and typed allowlists), exfiltration (egress policy), replay (idempotency keys), forged approval (signed identity and server-side authorization), infinite loops (budgets), cross-tenant leakage (tenant-scoped retrieval and storage), tool-output poisoning (schema and provenance validation).

The demo's regex injection filter is deliberately incomplete and is **not** a production security control. Authentication, sandboxing and tenant isolation are not implemented.
