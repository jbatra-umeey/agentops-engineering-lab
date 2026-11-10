# Original reference architecture

```mermaid
flowchart TD
    U[Incident API] --> V[Input validation and injection screening]
    V --> P[Deterministic plan builder]
    P --> G{Step budget remaining?}
    G -->|Yes| T[Typed tool registry]
    T --> M[Metrics fixture]
    T --> L[Logs fixture]
    T --> R[Runbook fixture]
    M --> O[Observation + audit event]
    L --> O
    R --> O
    O --> C[(SQLite checkpoint)]
    C --> G
    G -->|Plan complete| A[Approval required]
    A --> H{Human decision}
    H -->|Approve| X[Approved proposal; no execution]
    H -->|Reject| Z[Rejected proposal]
    G -->|No| F[Fail closed]
```

## Incident sequence

```mermaid
sequenceDiagram
    actor Operator
    participant API
    participant Agent
    participant Tools
    participant Store
    Operator->>API: POST /incidents/investigate
    API->>Agent: validate incident and check idempotency
    loop For each bounded tool step
        Agent->>Tools: call typed tool
        Tools-->>Agent: simulated observation
        Agent->>Store: checkpoint and audit
    end
    Agent-->>API: awaiting_approval
    API-->>Operator: proposed action + trace ID
    Operator->>API: POST /approve
    API->>Store: persist decision
    API-->>Operator: approved/rejected (no side effects)
```

## Design constraints

State is a validated Pydantic model. The checkpoint store persists per incident ID. Tool results are simulation fixtures and should be treated as untrusted if replaced with live data. Approval never executes a real remediation. SQLite is for a local single-process lab, not a horizontally scaled deployment.
