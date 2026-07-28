# Design Requirements

**Status:** active replacement design requirements.

## Interaction Model

Cite2Site presents citations as replay projections over append-only authority.
Users may organize citations into groups and bind citations to stable handles
inside those groups. Names are display data; IDs are authority.

## Requirements

| ID | Requirement | Gate | Verification |
|---|---|---|---|
| DR-001 | Every repository has a default group presented as `Inbox`. | R1/R4 | Init and replay tests. |
| DR-002 | Same-name sibling groups remain distinct and are projected as ambiguous until explicitly renamed or merged. | R4/R7 | Ambiguity and reconciliation tests. |
| DR-003 | Handles are group-owned objects with stable `handle_id` values. | R5 | Rename and tally tests. |
| DR-004 | Same-name handles in one group remain distinct and name lookup reports ambiguity. | R5/R7 | Ambiguity tests. |
| DR-005 | Duplicate evidence does not block citation creation. | R3/R6 | Duplicate creation and scoped supersession tests. |
| DR-006 | Projections show complete group and handle rolling tallies, not only counts. | R4/R5/R8 | Projection schema and tests. |
| DR-007 | Integrations offer actions only for concrete replacement object IDs or explicit create payloads. | R9 | Integration fixtures and manual Chrome validation. |

## Display Rules

Projections may hide rows in a filtered view, but they must not replace
complete tallies with aggregate summaries. Metadata-only mode must not display
accepted evidence text.
