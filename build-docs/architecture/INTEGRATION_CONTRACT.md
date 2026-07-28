# Cite2Site Replacement Integration Contract

**Status:** active R9 integration contract, dependent on R1-R8 foundations.

## Scope

This contract defines how browser, editor, and document-tool integrations
communicate with the replacement runtime. Integrations are transport clients,
not authority owners. They must not cache citation authority, infer duplicate
state, or write cited artifacts.

## Required Message Invariants

Every mutating integration message must provide:

- `schema_version: "c2s.integration.replacement.v1"`;
- `action`;
- `repository`;
- `idempotency_key`;
- actor metadata;
- the replacement object IDs it is mutating, or enough creation payload for the
  runtime to allocate those IDs atomically.

The runtime response must include:

- `ok`;
- `operation_id` for successful mutations;
- affected `citation_id`, `group_id`, and `handle_id` values when applicable;
- complete structured error information on failure.

## Lookup

`lookup-actions` is read-only. It must inspect the current artifact selection
and return replacement-aware actions:

- create a citation in the default group or selected group;
- bind to an existing handle ID;
- create a handle inside a group;
- show ambiguous group or handle names without guessing;
- target a concrete `citation_id`, `group_id`, `handle_id`, or membership when
  a mutation is offered.

Lookup responses may include display text, counts, and metadata-safe snippets
only when the repository privacy policy allows them. Default publication and
integration projections are metadata-only.

## Duplicate Behavior

Integrations must never reject duplicate evidence locally. Duplicate handling
belongs to the replacement runtime and is scoped by the target group's
duplicate policy:

- `handle`: duplicate bucket is `handle_id` plus `target_fingerprint`;
- `group`: duplicate bucket is `group_id` plus `target_fingerprint`;
- `none`: no automatic supersession.

The runtime must preserve every intentional citation and expose scoped
supersession state as projection data.

## Gate 9 Acceptance

Gate R9 is actionable when R1-R8 provide:

1. replacement repository identity and archived-format rejection;
2. completed atomic operation writes;
3. idempotency checks;
4. record-instance citation creation;
5. group and handle objects with stable IDs;
6. scoped duplicate policy;
7. replacement lookup/status/export projections;
8. native-host dispatch using this message contract;
9. package build evidence;
10. manual Chrome validation by the user.
