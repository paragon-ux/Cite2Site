# R4: Groups And Memberships

**Status:** planned.

## Objective

Implement stable groups, default Inbox, memberships, hierarchy validation, and
complete group rolling tallies.

## Deliverables

- `group_id` identity independent of name and path.
- Group create, rename, move, merge, retire, and alias operations.
- Membership add, remove, restore, and supersession state.
- Complete group tally projection.

## Acceptance

- Rename/move preserves `group_id` and tally.
- Same-name sibling groups remain distinct and ambiguous.
- Re-adding a citation restores the existing tally position.
