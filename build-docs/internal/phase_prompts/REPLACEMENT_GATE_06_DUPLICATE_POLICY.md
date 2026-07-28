# R6: Duplicate Policy And Scoped Supersession

**Status:** planned.

## Objective

Implement group duplicate policies and scoped supersession without global
retraction or history loss.

## Deliverables

- `handle`, `group`, and `none` duplicate policies.
- Scoped supersession events for group memberships and handle bindings.
- Duplicate-bucket reevaluation inside the same completed operation.

## Acceptance

- Under `handle`, only `handle_id` plus `target_fingerprint` supersedes.
- Under `group`, `group_id` plus `target_fingerprint` supersedes across handles.
- Under `none`, matching targets remain independently active.
- Dominance uses canonical citation-ID order, not timestamps.
