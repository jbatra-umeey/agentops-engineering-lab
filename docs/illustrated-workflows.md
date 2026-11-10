# Illustrated end-to-end workflows

These diagrams are original instructional designs. They depict a target architecture; the current runnable baseline is deterministic and does not connect to live telemetry or execute remediation.

## Workflow A — Diagnose a failed checkout deployment

```mermaid
sequenceDiagram
    autonumber
    actor Oncall
    participant API
    participant Orchestrator
    participant Metrics
    participant Releases
    participant Knowledge
    participant State
    Oncall->>API: POST /incidents/investigate
    API->>Orchestrator: Validated incident
    Orchestrator->>State: Load checkpoint and budgets
    par Independent read-only diagnostics
        Orchestrator->>Metrics: Get 5xx trend
        Metrics-->>Orchestrator: Spike at 10:02 + source ID
    and
        Orchestrator->>Releases: Get recent deployments
        Releases-->>Orchestrator: Release at 10:00 + source ID
    and
        Orchestrator->>Knowledge: Search relevant runbooks
        Knowledge-->>Orchestrator: Runbook excerpt + citation
    end
    Orchestrator->>State: Save evidence and tentative finding
    Orchestrator-->>API: Diagnosis with uncertainty
    API-->>Oncall: Read-only incident report
```

**Walkthrough.** A deployment is temporally correlated with a spike in 5xx responses. That is a hypothesis, not proof of causation. The agent should request a discriminating signal (for example, compare healthy and unhealthy instances) before making a strong claim. If the metrics endpoint fails, the report is marked partial.

## Workflow B — Human-approved remediation

```mermaid
flowchart TD
    A[Evidence-backed rollback proposal] --> B[Capture exact release and target revision]
    B --> C[Policy check: actor, tenant, environment]
    C --> D{Eligible for approval?}
    D -->|No| E[Reject and audit]
    D -->|Yes| F[Pause at durable checkpoint]
    F --> G[On-call reviews blast radius and evidence]
    G --> H{Approve exact proposal?}
    H -->|No| I[Close as denied]
    H -->|Yes| J[Revalidate revision and permissions]
    J --> K{Still valid?}
    K -->|No| L[Expire approval and re-review]
    K -->|Yes| M[Reserve idempotency key]
    M --> N[Authorized executor with rollback verification]
    N --> O[Audit outcome and monitor]
```

**Walkthrough.** An on-call engineer approves rollback of a specific service and release. Approval is not a generic permission token. A deployment change after approval invalidates the proposal; the executor must re-check. **The current baseline only records approval; it does not execute rollback.**

## Workflow C — Prompt injection through retrieval

```mermaid
sequenceDiagram
    participant Agent
    participant Search as Retrieval tool
    participant Policy
    participant Executor
    Agent->>Search: Retrieve checkout runbook
    Search-->>Agent: Text including malicious command
    Agent->>Policy: Proposed action from retrieved content
    Policy-->>Agent: Denied: untrusted text cannot grant privileges
    Agent->>Executor: Read-only allowed diagnostics
    Executor-->>Agent: Bounded observation
```

**Walkthrough.** A retrieved runbook might contain instructions to export secrets. The agent may quote the suspicious text as evidence but must not treat it as an instruction. The authorization layer blocks secret access independently of model behavior.

## Workflow D — Reliability and evaluation loop

```mermaid
flowchart LR
    A[Golden incident fixture] --> B[Agent run]
    B --> C[Capture output and tool trajectory]
    C --> D[Schema and policy checks]
    D --> E[Evidence groundedness evaluation]
    E --> F[Cost and latency budget checks]
    F --> G{Release gate passes?}
    G -->|Yes| H[Canary and monitor]
    G -->|No| I[Fix prompt, policy, tool or orchestration]
    I --> B
```

**Walkthrough.** A correct root-cause guess is insufficient if the agent attempted an unauthorized call. Evaluate task outcome, safety, tool sequence, groundedness, latency and cost independently. Compare multiple runs where inference is nondeterministic.

## Suggested learner assessment

For each workflow, learners submit: a traced happy path, a failure path, a diagram annotated with trust boundaries, a runnable test, and a short design trade-off explanation.
