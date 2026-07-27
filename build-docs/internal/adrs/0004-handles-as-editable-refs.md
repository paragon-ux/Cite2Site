# ADR 0004: Handles As Editable Refs

## Status

Accepted

## Context

Users and agents need friendly names, but names should not become citation
identity. People may cite third-party work that has no embedded handle.

## Decision

Citation IDs are immutable. Handles are editable aliases over citation IDs and
are changed by appending handle-binding events.

## Alternatives Considered

- Use the handle as the citation identity. Renames would break references and
  conflate display with audit identity.
- Rewrite the original citation event during a rename. This violates append-only
  history.
- Forbid renames. This makes imported or third-party citations unnecessarily
  difficult to organize.

## Consequences

- Users can add or rename handles after citation creation.
- Old handles remain aliases by default.
- Published links can remain durable across handle renames.
- Handle collisions need explicit policy.

## Implementation Implications

- `set-handle` appends a binding, rename, alias, or retire event.
- Replay computes preferred handle and aliases without changing citation IDs.
- Contextual mutations must retain the concrete citation ID even when a handle
  is displayed to a person.

## Validation Hooks

- `TR-103` and handle command requirements.
- Rename/alias/collision unit tests.
- Grouped-index tests that prove old aliases remain discoverable.
