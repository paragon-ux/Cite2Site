# ADR 0012: Stable Groups And Handles

**Status:** Accepted

## Context

The archived model treated handles as editable aliases over citation IDs. The
replacement RFC requires stable groups and group-owned handles with immutable
IDs, complete tallies, scoped duplicate policy, and explicit merge behavior.

## Decision

Cite2Site will represent groups and handles as first-class authority objects.
Group names, paths, handle names, and aliases are mutable display data. The
immutable IDs are `group_id` and `handle_id`.

Duplicate evidence must not suppress citation creation. Duplicate policy is
evaluated inside a group and produces scoped supersession state.

## Consequences

- Same-name groups and handles are preserved as distinct objects until explicit
  merge or rename operations resolve ambiguity.
- Projections must expose complete group and handle rolling tallies.
- Integrations must address stable replacement IDs and must not infer identity
  from names.

## Validation Hooks

- Group and handle rename preserve IDs and tallies.
- Same-name ambiguity tests pass.
- Scoped supersession tests prove duplicate policy does not globally retract
  citations.
