# Current Status Matrix

**Status:** active current-state authority.

The active Cite2Site protocol is the replacement model defined by the refined
reconciliation RFC and clean archival boundary. The v0.3/v1 implementation was
historically completed through its prior gates, but those completion claims are
not active replacement-protocol conformance.

Status meanings:

- **Done**: implemented under the active replacement protocol and covered by
  tests or smoke checks.
- **Partial**: implemented in a limited replacement-compatible form, with clear
  gaps.
- **Planned**: accepted replacement design direction, not implemented.
- **Archived**: historical v0.3/v1 behavior preserved for audit, unsupported by
  the active runtime.
- **Blocked**: cannot proceed until a named prerequisite is complete.

## Practical Status Statement

Gate 9 / Phase 7 Part 2 Chrome-extension work is blocked. The duplicate
behavior exposed a protocol-level conflict: evidence-derived citation IDs and
global duplicate suppression are incompatible with the replacement requirement
that every intentional citation receives a distinct record-instance
`citation_id`, while retries are suppressed only by operation idempotency.

The active immediate gate is the **Replacement Protocol and Archival Separation
Gate**.

## Replacement Capability Matrix

| Area | Capability | Status | Current Evidence | Gap | Next Action |
|---|---|---:|---|---|---|
| Authority | Clean archival boundary | Partial | `MIGRATION_DIRECTIVE.md`, `OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md`, `OFFICIAL_PROTOCOL_MIGRATION_V2.md`, `ARCHIVAL_BOUNDARY.md`, ADR 0011. | Historical docs and tests still need full exclusion/label sweep. | Complete archive-boundary documentation pass. |
| Authority | Active replacement RFC | Done | `OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md` defines groups, handles, tallies, scoped supersession, atomic operations, idempotency, and reconciliation. | None for policy authority. | Keep RFC as active protocol source. |
| Authority | Runtime rejects archived repositories | Partial | `src/c2s/replacement.py` rejects archived v0.3/v1 repository shape with `E_ARCHIVED_PROTOCOL_UNSUPPORTED`; `tests/test_replacement_archival_boundary.py` proves no writes occur. | The default `c2s` CLI still exposes transitional v0.3/v1 behavior and must be replaced before claiming active runtime conformance. | Wire replacement repository identity into the active CLI/runtime entry point. |
| Authority | Atomic completed operations | Planned | Required by RFC sections 11, 13, 14 and replacement implementation spec. | No replacement operation ledger exists. | Implement new repository identity and operation envelope. |
| Citation | Record-instance citation IDs | Planned | RFC section 3. | Current runtime derives citation IDs from evidence identity. | Replace citation allocation before accepting creation commands. |
| Groups | Stable `group_id` objects and memberships | Planned | RFC sections 4 and 6. | Current grouping is derived indexes only. | Implement default Inbox group and membership authority. |
| Handles | Stable group-owned `handle_id` objects | Planned | RFC section 5. | Current handles are raw strings over citation IDs. | Implement handle objects and name ambiguity behavior. |
| Duplicate policy | Scoped supersession | Planned | RFC sections 8, 9, and 12. | Current runtime has no scoped supersession events. | Implement handle/group/none duplicate policies. |
| Reconciliation | Deterministic semantic branch reconciliation | Planned | RFC section 14. | No replacement reconciliation command exists. | Implement after operation, group, handle, and tally foundations. |
| Publication | Metadata-only default | Planned | Existing invariant remains conceptually valid; RFC section 16 preserves default. | Replacement projection shapes are not specified or implemented. | Define replacement projection schemas and no-leak tests. |
| Gate 9 | Chrome extension Phase 7 Part 2 | Blocked | `REPLACEMENT_PROTOCOL_ARCHIVAL_SEPARATION_GATE.md` blocks Gate 9 until replacement foundations exist. | Current extension protocol assumes archived lookup/action shapes. | Rewrite Gate 9 objective after replacement foundations pass. |

## Historical V0.3/V1 Status

The v0.3/v1 CLI/core, schemas, guides, and Gate 0 through v1 stabilization work
are **Archived**. Historical completion remains inspectable through Git history
and historical documents, but it is not active protocol conformance and must not
drive new implementation.

## Known Current Gaps

1. The active runtime still contains transitional v0.3/v1 behavior.
2. Replacement schemas and examples are indexed as required but not yet written.
3. Active tests still contain old-model assertions and must be separated before
   replacement implementation can be accepted.
4. Gate 9 is blocked until the replacement protocol foundation is implemented
   and tested.
