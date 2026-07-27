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

## Consequences

- Existing events are never rewritten.
- Status can change without changing accepted history.
- Recovery actions append compensating events.
- Replay and export must be deterministic.
