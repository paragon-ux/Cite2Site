# ADR 0011: Clean Protocol Replacement And Archival Boundary

**Status:** Accepted

## Context

The v0.3/v1 Cite2Site model uses evidence-derived citation IDs, string handles
as editable aliases, two append-only ledgers, and global citation state. The
refined grouping and reconciliation RFC requires record-instance citation IDs,
stable groups, group-owned handle IDs, complete rolling tallies, scoped
supersession, atomic completed operations, idempotency, and deterministic
semantic reconciliation.

Those models are incompatible as active runtime contracts.

## Decision

Cite2Site will make a clean protocol replacement. The v0.3/v1 protocol,
implementation specs, schemas, examples, tests, guides, and stable contract are
historical material. They remain preserved, but are removed from the active
authority chain.

The replacement runtime will reject archived-format repositories before replay,
mutation, reconciliation, projection, or publication. This decision does not
authorize runtime migration, transparent import, a compatibility bridge, or
dual reducers.

## Consequences

- The old Gate 9 / Phase 7 Part 2 checkpoint is superseded. Replacement Gate
  R9 is actionable only against the replacement integration contract.
- Active docs must be rewritten around groups, handles, tallies, idempotency,
  scoped supersession, and reconciliation.
- Old tests that assert evidence-derived IDs or string-handle identity cannot
  remain active conformance tests.
- A future import utility requires separate design and security review.

## Validation Hooks

- Active reading order excludes archived protocol specs and schema index.
- Status matrix marks replacement implementation as pending or partial until
  tests exist.
- Archived-format repository fixtures fail closed before writes.
- Replacement Gate R9 requires package evidence and user manual Chrome
  validation before it can be marked Done.
- Reconciliation tests operate only on replacement-protocol repositories.
