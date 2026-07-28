# R5: Handles And Bindings

**Status:** planned.

## Objective

Implement group-owned handle IDs, handle names and aliases, bindings, and
complete handle rolling tallies.

## Deliverables

- Stable `handle_id` owned by exactly one `group_id`.
- Handle create, rename, merge, retire, and alias operations.
- Binding add, remove, restore, and supersession state.
- Complete handle tally projection.

## Acceptance

- Rename preserves `handle_id` and tally.
- Same-name handles remain distinct and name lookup reports ambiguity.
- Binding a different intentional citation creates a new tally entry.
