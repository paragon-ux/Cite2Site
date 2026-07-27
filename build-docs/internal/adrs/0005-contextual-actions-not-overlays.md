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

## Alternatives Considered

- Build and maintain a universal C2S overlay. This creates an unbounded set of
  editor, browser, and document integrations.
- Persist per-integration citation state. This permits conflicting views of the
  same artifact.
- Require a CLI for every human action. This preserves authority but fails the
  intended low-friction human experience.

## Consequences

- One interaction pattern can work across many tools.
- Integrations stay thin.
- Mutating actions must name a concrete citation ID when overlaps exist.
- C2S remains responsible for deterministic action availability.

## Implementation Implications

- `lookup-actions` is a read-only contract over replayed state.
- A matching UI must present an ordered picker before an overlapping mutation.
- Native context menus are Target integrations until an adapter implements and
  tests the transport.

## Validation Hooks

- DR-001 through DR-004 and BR-004 through BR-005.
- Lookup response fixtures, overlap-order tests, and ambiguous-target refusal
  tests.
- Integration fixtures that prove no authoritative overlay state is written.
