# Phase 03: Workflow Completeness

**Status:** authorized after Phase 02 privacy and publication is accepted.

## Purpose

Complete the append-only command vocabulary needed to correct, review, and
organize citations without rewriting authority history. This is not a mutable
lifecycle engine: it adds explicit compensating events and review operations.

## Required Reading

Read `AGENTS.md`, `DOCUMENTATION_STANDARD.md`, the status matrix, current
workflow, BRD/DRD/TRD, Phase 02 results, and both v0.3 specifications.

## Scope

Implement `preflight-selection`, `accept-current`, `retract`, `restore`,
`relocate`, `note`, and the approved first-line handle mode. Define the command
and event contracts before implementation, including idempotency and ambiguity
rules where they apply.

## Non-Goals

- Do not edit an existing citation or handle event in place.
- Do not accept current evidence or relocate a citation through fuzzy matching.
- Do not call a changed projection "stale" or silently refresh accepted
  evidence.
- Do not add a right-click plugin; it belongs to Phase 05.

## Required Design Decisions

1. Define each new event type, required payload, hash-chain placement, and
   replay reduction rule.
2. Define whether undo/redo are explicit commands, contextual labels for
   compensating events, or deferred. Do not promise either without a contract.
3. Define preflight output, including canonical range, evidence hash, adapter,
   and refusal behavior.
4. Define first-line handle parsing as explicit user-selected behavior; it must
   not infer a handle from arbitrary content.

## Required Changes

### Core and CLI

- Add parser and core handlers for the approved commands.
- Require a concrete `citation_id` for every mutation of an existing citation.
- Preserve source cleanliness for preflight and all mutations.
- Update replay to reduce compensating events deterministically.
- Add idempotency behavior where requests can be safely retried.

### Protocol, Schema, and Documentation

- Add event/request/response schemas and realistic fixtures where public shapes
  change.
- Expand the error-code catalog with stable errors for review, relocation, and
  policy refusals.
- Update workflow recovery paths and contextual-action vocabulary only for
  commands that are now implemented.
- Update status rows and external narratives to avoid presenting targets as
  available before tests pass.

## Required Tests

- Success, malformed-input, missing-citation, and ambiguous-target tests for
  every command.
- Source-byte preservation tests for all artifact-touching commands.
- Replay tests proving retraction/restoration, acceptance, relocation, and
  notes are append-only and deterministic.
- Preflight tests for valid selection, invalid range, hash mismatch, unsupported
  adapter, and empty evidence.
- First-line handle tests proving opt-in behavior, collision handling, and no
  accidental parsing from ordinary content.

## Acceptance Criteria

The phase is accepted only when compensating actions are auditable, all new
errors are structured, recovery workflow documentation maps one-to-one to
implemented commands, and the full gate validation stack passes.

