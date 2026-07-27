# ADR 0005: Contextual Actions, Not Overlay Authority

## Status

Accepted

## Context

Right-click citation management is the simplest human UX, but C2S cannot own
every editor, browser, document, or PDF overlay.

## Decision

C2S exposes `lookup-actions` for artifact plus cursor/selection/range. Tool
integrations render native menus from that response. Overlay state is not
authority.

## Consequences

- One interaction pattern can work across many tools.
- Integrations stay thin.
- Mutating actions must name a concrete citation ID when overlaps exist.
- C2S remains responsible for deterministic action availability.
