# ADR 0004: Handles As Editable Refs

## Status

Accepted

## Context

Users and agents need friendly names, but names should not become citation
identity. People may cite third-party work that has no embedded handle.

## Decision

Citation IDs are immutable. Handles are editable aliases over citation IDs and
are changed by appending handle-binding events.

## Consequences

- Users can add or rename handles after citation creation.
- Old handles remain aliases by default.
- Published links can remain durable across handle renames.
- Handle collisions need explicit policy.
