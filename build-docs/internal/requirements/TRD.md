# Technical Requirements

**Status:** active replacement technical requirements.

## Authority Files

Replacement repositories use:

- `project.json` for repository identity and schema;
- `operations.jsonl` for completed atomic operations;
- derived projection files under `exports/` and `site/`.

The archived v0.3/v1 files are not valid active authority.

## Requirements

| ID | Requirement | Gate | Verification |
|---|---|---|---|
| TR-001 | `project.json` must declare `schema_version: "c2s.project.replacement.v1"`. | R1 | Schema and init tests. |
| TR-002 | Mutations must append completed operation records with `operation_id`, `idempotency_key`, command, semantic payload hash, and events. | R2 | Operation replay tests. |
| TR-003 | Replay must reject or ignore incomplete operations before state projection. | R2/R7 | Incomplete-operation tests. |
| TR-004 | Citation IDs must not be derived solely from target fingerprints. | R3 | Duplicate-evidence citation tests. |
| TR-005 | Group and handle tallies must use canonical citation-ID order, not timestamps. | R4/R5/R6 | Tally-order tests. |
| TR-006 | Scoped supersession events must belong to the same completed operation that applied duplicate policy. | R6 | Supersession operation tests. |
| TR-007 | Reconciliation must reject archived repositories before writes. | R7 | Conflict fixture tests. |
| TR-008 | Native-host and extension messages must use replacement schemas. | R9 | Integration schema tests. |
