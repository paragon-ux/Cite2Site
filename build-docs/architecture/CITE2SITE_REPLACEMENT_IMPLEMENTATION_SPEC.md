# Cite2Site Replacement Implementation Specification

**Status:** active implementation specification, foundation pending.

## Scope

This specification translates the replacement protocol RFC into implementation
requirements. It deliberately does not define an in-place migration or
dual-protocol compatibility bridge.

## Authority Model

The replacement implementation must use completed atomic operations as replay
authority. Each mutating command must produce one durable operation identified
by:

- `operation_id`;
- `idempotency_key`;
- command name;
- canonical semantic payload;
- completed-operation marker.

Replay must ignore incomplete operations and reject histories where an
operation is structurally incomplete or conflicts with an existing
idempotency key.

## Required Authority Objects

The active runtime must represent:

- record-instance `citation_id`;
- deterministic `target_fingerprint`;
- stable `group_id` with hierarchy and duplicate policy;
- stable group-owned `handle_id`;
- group membership events;
- handle binding events;
- scoped supersession events;
- global citation state events;
- explicit group and handle merge operations;
- reconciliation operations and conflicts.

## Archived Repository Detection

Before replay or mutation, the active runtime must inspect repository identity
and schema. A repository whose project schema or authority files match the
archived v0.3/v1 model must fail before writes with
`E_ARCHIVED_PROTOCOL_UNSUPPORTED`.

The runtime must not partially read archived ledgers to build replacement
state, and must not modify archived repositories while reporting the error.

## Duplicate Semantics

Duplicate evidence is not an idempotency key. Two distinct intentional
citation operations with the same target fingerprint must receive distinct
citation IDs and must remain visible in complete group and handle tallies.

Only a retry with the same `idempotency_key` and same canonical semantic
payload may return an existing operation result without appending authority.

Duplicate policy is scoped by group:

- `handle`: `handle_id` plus `target_fingerprint`;
- `group`: `group_id` plus `target_fingerprint`;
- `none`: no automatic supersession.

Scoped supersession must append explicit events and must not globally retract
or delete any citation.

## Reconciliation

Git must not text-merge authority ledgers. Semantic reconciliation applies only
to replacement-protocol repositories with valid shared replacement ancestry.

Reconciliation must validate both sides, preserve every independent operation,
order concurrent operations by canonical `operation_id`, rehash destination
events, rebuild complete tallies, reapply duplicate policy, and regenerate
derived projections.

Archived-format repositories are rejected before reconciliation and are not
converted.

## Transitional Implementation Status

The checked-in Python runtime still contains archived v0.3/v1 behavior. Until
replacement foundation work lands, it must be treated as transitional code and
must not be cited as replacement-protocol conformance.
