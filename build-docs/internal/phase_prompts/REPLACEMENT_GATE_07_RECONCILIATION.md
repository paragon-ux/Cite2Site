# R7: Semantic Reconciliation

**Status:** planned.

## Objective

Implement deterministic semantic reconciliation for replacement repositories
only.

## Deliverables

- Reconcile command or engine that validates both inputs before writes.
- Shared-history validation and structural conflict reporting.
- Operation import preserving independent branch operations.
- Deterministic concurrent ordering by canonical `operation_id`.

## Acceptance

- Merge direction does not change the result.
- Archived or invalid repositories fail before writes.
- Same-name groups and handles remain distinct unless explicitly merged.
- Reconciliation leaves cited artifacts unchanged.
