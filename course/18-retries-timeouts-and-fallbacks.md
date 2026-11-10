# Module 18 — Retries, timeouts and fallbacks

## Learning objective

Explain the concept, implement its control boundary, identify its failure mode, and defend the trade-off in a production architecture review.

## Technical explanation

Retries and fallbacks improve resilience when failure modes are classified. In the reference incident-response workflow, the operational question is not only whether the agent can produce a diagnosis, but whether the system can prove which evidence and permissions led to that diagnosis. Use exponential backoff with jitter for transient errors.

## Workflow diagram

```mermaid
flowchart LR
    A[Input and state] --> B[Module 18: Retries, timeouts and fallbacks]
    B --> C{Validate result}
    C -->|Pass| D[Checkpoint and trace]
    C -->|Fail| E[Safe stop or escalation]
```

## Implementation touchpoint

Inspect `src/agentops/core.py`, `src/agentops/api.py`, and `docs/architecture.md`. The baseline demonstrates typed state, tool observations, bounded execution, persistence, and approval. **This module's complete production capability may be an extension exercise rather than implemented functionality.** Check the [readiness register](../docs/production-readiness.md) before making deployment claims.

## Failure analysis

Retries can duplicate irreversible writes. Design a negative test that proves the workflow stops or escalates rather than silently proceeding.

## Hands-on lab

1. Run the baseline incident `INC-1042` and inspect the returned `trace_id`, `audit`, `steps`, and `evidence`.
2. Draw the trust boundary relevant to **Retries, timeouts and fallbacks** and annotate which transitions need validation.
3. Implement one additional typed policy or test in `core.py` / `tests/`, keeping default behavior backwards compatible.
4. Introduce a failure (malformed tool result, unavailable dependency, duplicate request, or unauthorized action) and verify the safe outcome.
5. Record before/after test output, execution cost proxy (step count), and architectural trade-offs.

## Architecture review questions

- What is the source of truth and who may mutate it?
- What should happen when this component times out or returns an invalid result?
- How would you prove that no unauthorized side effect occurred?
- Which signals would you monitor after a canary rollout?

## Completion criteria

A passing automated negative test, a documented decision, a revised sequence diagram, and a concise explanation of when this pattern should **not** be used.


---

## Illustrated real-world walkthrough: Retries Timeouts And Fallbacks

**Scenario.** Metrics API times out during a checkout outage.

### Sequence of events

1. **Trigger:** A request or event is recorded with a stable incident identifier and trace context.
2. **Decision and execution:** Apply per-call timeout, exponential backoff with jitter for transient reads, circuit breaker on persistent failure, then degrade to an explicitly partial diagnosis.
3. **Verification:** Compare each returned observation with the requested schema, evidence provenance, and policy constraints.
4. **Exit:** Record the resulting state, trace, and an explicit outcome: success, partial result, denied, or escalated.

```mermaid
sequenceDiagram
    autonumber
    participant U as Incident operator
    participant O as Orchestrator
    participant P as Policy and state
    participant T as Tool or specialist
    U->>O: Investigate incident INC-1042
    O->>P: Load state and validate scope
    P-->>O: Allowed actions and budget
    O->>T: Execute bounded M18 operation
    alt Valid observation
        T-->>O: Typed result with evidence ID
        O->>P: Commit evidence and state revision
        P-->>O: Revision accepted
        O-->>U: Explain finding and next action
    else Timeout, rejection or malformed result
        T-->>O: Explicit failure
        O->>P: Record failure and apply policy
        O-->>U: Partial result or escalation
    end
```

### Decision workflow

```mermaid
flowchart TD
    A[Incident event and context] --> B[Validate scope and budget]
    B --> C{Authorized and within budget?}
    C -->|No| D[Stop and audit denial]
    C -->|Yes| E[Run M18 workflow]
    E --> F{Evidence valid and sufficient?}
    F -->|Yes| G[Checkpoint and report]
    F -->|No| H{Safe retry or follow-up available?}
    H -->|Yes| E
    H -->|No| I[Partial report and escalation]
```

### Example inputs and outputs

| Artifact | Example |
|---|---|
| Incident | `INC-1042`, service `checkout-api`, 5xx alert |
| Input evidence | Error-rate window, release revision, and runbook IDs (where applicable) |
| Successful output | Structured finding with evidence references and next-step recommendation |
| Safe failure output | Typed error, reason for stop, and retained prior evidence |

**Production safeguard:** Do not blindly retry non-idempotent write actions.

**Practice task:** Trace this scenario on paper and implement a negative test proving the safeguard; distinguish what is already in the deterministic baseline from a proposed extension.

**Interview challenge:** How do you distinguish transient from permanent failures?
