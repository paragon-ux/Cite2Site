# Phase 05: Integration Examples

**Status:** authorized after Phase 04 adapter hardening is accepted.

## Purpose

Prove the intended one-gesture human experience without making Cite2Site own
editor overlays, browser state, or document-tool internals. The integration is
a thin client over the already stable CLI/core contract.

## Required Reading

Read `AGENTS.md`, `DOCUMENTATION_STANDARD.md`, ADR 0005, DRD contextual-menu
requirements, the protocol section for `lookup-actions`, and the status matrix.

## Scope

Deliver one minimal, reproducible integration example and transport-neutral
examples for editor, browser, and document-tool implementers. Demonstrate
selection citation, existing-citation lookup, overlap picking, handle editing,
and clear unavailable-action behavior.

## Non-Goals

- Do not build a universal overlay or a separate C2S UI database.
- Do not make the integration responsible for replay, collision resolution, or
  authority history.
- Do not expose unimplemented recovery commands as enabled actions.
- Do not treat a single editor plugin as a universal artifact adapter.

## Required Interaction Contract

1. An uncited selection maps to a prepared citation request.
2. A cited region calls `lookup-actions` with artifact and range.
3. One match can show direct actions; multiple matches must show an ordered
   picker before mutation.
4. Every mutation includes the selected `citation_id`.
5. The client displays structured errors without parsing prose.
6. The client stores no authoritative overlay state; it may cache only
   disposable display information.

## Required Changes

- Publish an integration contract fixture for request/response examples.
- Add a minimal reference implementation or executable mock for one supported
  host surface.
- Document range encoding, artifact identity, selection normalization, action
  labels, cancellation, and error presentation.
- Add integration-specific accessibility expectations: keyboard path, visible
  text labels, focus behavior, and picker ordering.
- Update external documents only after the example is reproducible.

## Required Tests

- Fixture tests for uncited, single-match, overlapping, changed, missing, and
  unsupported states.
- Tests proving mutations always include a selected citation ID.
- Tests proving the client does not modify the cited artifact or persist
  authority outside `.c2s`.
- Contract compatibility tests against `lookup-actions` schemas and error
  envelopes.

## Acceptance Criteria

The phase is accepted only when a user can perform the demonstrated interaction
end to end, every integration action maps to an implemented command, and the
example remains a thin client rather than a competing state system.

