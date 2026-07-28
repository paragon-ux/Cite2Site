# Current Status Matrix

**Status:** active current-state authority.

The active Cite2Site protocol is the replacement model defined by the refined
reconciliation RFC and clean archival boundary. The v0.3/v1 implementation was
historically completed through its prior gates, but those files now belong in
the sibling `Cite2Site-Archival/` folder, not in the active repository.

Status meanings:

- **Done**: implemented under the active replacement protocol and covered by
  tests or smoke checks.
- **Partial**: implemented in a limited replacement-compatible form, with clear
  gaps.
- **Planned**: accepted replacement design direction, not implemented.
- **Actionable**: prerequisites are sufficiently present to begin the gate,
  but acceptance evidence is still required.
- **Archived**: historical v0.3/v1 behavior preserved for audit, unsupported by
  the active runtime.
- **Blocked**: cannot proceed until a named prerequisite is complete.

## Practical Status Statement

The active work is the replacement `R0` through `R9` gate sequence. Gate 9 is
not an old checkpoint continuation; it is the replacement-aware integration
gate that depends on gates R1-R8.

## Replacement Capability Matrix

| Area | Capability | Status | Current Evidence | Gap | Next Action |
|---|---|---:|---|---|---|
| Authority | Clean archival boundary | Done | Archived package moved to `../Cite2Site-Archival/from-integration-gate9-finalization-b4b741d/`; old tracked docs/tests/examples removed from active repo; replacement docs, schemas, examples, and R0-R9 prompts exist. | Remote CI not yet run. | Commit and push for remote evidence when ready. |
| Authority | Active replacement RFC | Done | `OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md` defines groups, handles, tallies, scoped supersession, atomic operations, idempotency, and reconciliation. | None for policy authority. | Keep RFC as active protocol source. |
| Authority | Runtime rejects archived repositories | Done | `src/c2s/replacement.py`, `src/c2s/cli.py`, and `tests/test_replacement_archival_boundary.py`; active CLI no longer exposes old mutation commands. | Remote CI not yet run. | Keep rejection fixture in active suite. |
| Authority | Atomic completed operations | Done | `operations.jsonl`, completed operation records, idempotency hash checks, and `tests/test_replacement_runtime.py`. | Concurrent writer locking remains future hardening. | Add locking before multi-process release claims. |
| Citation | Record-instance citation IDs | Done | Duplicate-evidence test creates distinct `cit_` IDs and idempotent retry returns the original result. | Current adapter is UTF-8 text only. | Extend adapters under replacement contract later. |
| Groups | Stable `group_id` objects and memberships | Partial | `init` creates default Inbox group; citation creation appends group membership and complete tally. | Group rename/move/merge commands not implemented. | Implement full R4 management commands. |
| Handles | Stable group-owned `handle_id` objects | Partial | Citation creation creates or reuses group-owned handles and maintains handle tallies. | Handle rename/merge/alias commands not implemented. | Implement full R5 management commands. |
| Duplicate policy | Scoped supersession | Partial | Handle-scoped duplicate supersession events are emitted and tested. | Group/none policy mutation and full reevaluation commands are not implemented. | Complete R6 policy commands. |
| Reconciliation | Deterministic semantic branch reconciliation | Partial | `reconcile` imports completed operations from same replacement repository identity and rejects mismatches/conflicts. | Full structural conflict catalog and hash-chain rehashing remain incomplete. | Expand R7 fixtures. |
| Publication | Metadata-only default | Partial | `export` writes metadata-only status/site projections without evidence text. | Full status/site navigation and no-leak matrix incomplete. | Expand R8 projection tests. |
| Gate 9 | Replacement integration and Chrome extension | Actionable | Native host accepts `c2s.integration.replacement.v1`; extension sends replacement cite/lookup messages with idempotency; `dist/cite2site-2.0.0a2-py3-none-any.whl` built and installed; native host registered to `C:\Users\USER\.c2s-replacement`; framed native-message duplicate precheck produced distinct `citation_id`s. | Manual Chrome validation still required before Done. | Stop for user manual validation before marking R9 Done. |

## Historical V0.3/V1 Status

The v0.3/v1 CLI/core, schemas, guides, tests, examples, and Gate 0 through v1
stabilization work are **Archived** in `Cite2Site-Archival/`. Historical
completion remains inspectable through that folder and Git history, but it is
not active protocol conformance and must not drive new implementation.

## Known Current Gaps

1. Group, handle, duplicate-policy, reconciliation, and projection management
   are foundation-level implementations, not full release-grade feature sets.
2. Gate 9 cannot be marked Done until user manual Chrome validation passes.
