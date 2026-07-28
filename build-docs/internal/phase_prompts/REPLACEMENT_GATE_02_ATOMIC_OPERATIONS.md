# R2: Atomic Operations

**Status:** planned.

## Objective

Implement completed atomic operation authority and idempotency.

## Deliverables

- `operations.jsonl` with completed operation records.
- Stable `operation_id` and required `idempotency_key` for every mutation.
- Semantic payload hash and idempotency conflict detection.
- Completed-operation-only replay.

## Acceptance

- Same idempotency key and same payload returns original operation result.
- Same idempotency key with different payload fails with
  `E_IDEMPOTENCY_CONFLICT`.
- Incomplete operations do not become replay authority.
