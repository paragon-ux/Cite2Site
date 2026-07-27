# ADR 0008: Session Gates Define Rigor, Not A Hard Stop

## Status

Accepted

## Context

The project plan sequences G0 through G8, while execution requests may ask an
agent to continue through every remaining gate in one uninterrupted run. The
repository describes one normal coding session as one acceptance gate. That
phrase sets the expected scope and rigor of a gate; it does not require a
long-lived execution task to stop after the first accepted gate. Each gate
changes a distinct contract surface and requires implementation, documentation,
validation, and independent review before the next surface is attempted.

## Decision

Treat each gate as a session-sized acceptance unit. A persistent task may run
multiple gates sequentially, but it must complete the full acceptance loop for
one gate before selecting the next authorized gate from the status matrix.

## Alternatives Considered

- Complete several gates without individual acceptance. This reduces handoff
  overhead, but makes defects, contract drift, and review findings harder to
  isolate.
- Treat a gate as an informal milestone and advance after tests alone. This
  weakens the required agreement among runtime behavior, specifications,
  status, and independent review.
- Split each gate into arbitrary time-boxed fragments. This makes status
  evidence ambiguous and permits partially delivered public contracts.

## Consequences

- A long-lived objective may require several gates in one or several sessions.
- Each accepted gate has a narrow, auditable change set and review packet.
- The status matrix remains the handoff record for selecting the next gate.

## Implementation Implications

- Gate runners must select the first incomplete gate and produce an acceptance
  report before advancing to the next one.
- A later gate must not be implemented solely because it is listed in the
  same phase prompt.
- Incomplete work is recorded as Partial or Target rather than carried forward
  as an undocumented assumption.

## Validation Hooks

- `AGENTS.md` session-gate rule.
- `BUILD_WORKFLOW_CURRENT.md` gate order and acceptance stack.
- Gate report contains one gate identifier, its local validation evidence, and
  independent review result.
