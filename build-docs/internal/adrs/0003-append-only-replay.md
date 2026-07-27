# ADR 0003: Append-Only Replay

## Status

Accepted

## Context

Mutable citation state would make audit history weaker and blur the distinction
between accepted evidence and current artifact observations.

## Decision

Mutating operations append events. Projected citation state is computed by
replaying citation history, handle bindings, current artifact observations, and
repository policy.

## Alternatives Considered

- Rewrite a mutable citation record in place. This hides the sequence of
  acceptance and correction decisions.
- Let UI state determine current citation meaning. This makes replay dependent
  on a particular integration.
- Infer accepted evidence from the current artifact. This replaces explicit
  acceptance with semantic or contextual guessing.

## Consequences

- Existing events are never rewritten.
- Status can change without changing accepted history.
- Recovery actions append compensating events.
- Replay and export must be deterministic.

## Implementation Implications

- History files use hash-chained JSONL events.
- Status and exports must be read-only projections.
- Recovery behavior, when implemented, appends compensating events rather than
  deleting or rewriting history.

## Validation Hooks

- `TR-102`, `TR-103`, `TR-105`, and `TR-106`.
- Event-chain corruption tests and deterministic replay tests.
- Status tests that distinguish accepted evidence from current observation.
