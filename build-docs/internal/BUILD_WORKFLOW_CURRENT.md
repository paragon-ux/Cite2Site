# Current Build Workflow

**Status:** active workflow authority.

## Active Gate

The active gate is **Replacement Protocol and Archival Separation Gate**.
Gate 9 / Phase 7 Part 2 Chrome-extension work is blocked until this prerequisite
gate passes.

## Workflow Principles

- Cited artifacts remain source-clean.
- Authority mutations are append-only.
- Replay uses completed atomic operations only.
- Status, exports, indexes, and MkDocs output are derived projections.
- Duplicate evidence does not suppress intentional citation creation.
- Idempotency suppresses only retries of the same logical operation.
- Semantic reconciliation applies only to replacement-protocol repositories.
- Archived v0.3/v1 repositories are rejected before replay, mutation,
  reconciliation, projection, or publication.

## Gate Validation Stack

During authority cleanup, run targeted documentation and schema checks:

1. active Markdown links resolve;
2. active JSON schemas and examples parse when present;
3. `AGENTS.md` reading-order targets exist;
4. active docs do not describe archived v0.3/v1 behavior as current;
5. status labels distinguish Done, Partial, Planned, Archived, and Blocked.

After replacement implementation begins, validation must also include:

1. archived-format repository rejection before writes;
2. source-clean regression tests;
3. atomic-operation integrity tests;
4. incomplete-operation rejection tests;
5. idempotency tests;
6. complete group and handle rolling-tally tests;
7. scoped-supersession tests;
8. same-name group and handle ambiguity tests;
9. deterministic reconciliation tests;
10. metadata-only no-leak tests;
11. authority hash-chain validation.

## Active Gate Table

| Gate | Objective | Required Deliverables | Acceptance Tests | Status Update |
|---|---|---|---|---|
| Replacement prerequisite | Establish clean replacement protocol authority and archive boundary. | Active RFC, migration policy, archival boundary, replacement implementation spec, replacement schema index, updated AGENTS/map/status/workflow/plan, interrupted Gate 9 preserved. | Docs link/schema checks; stale active-reference search; archived repository rejection test once runtime work begins. | Mark replacement boundary Partial or Done with evidence. |
| Foundation 1 | New repository identity and archived-format rejection. | Replacement project schema, init contract, fail-closed archived repo detection. | Archived v0.3/v1 repo rejected before replay or mutation; new replacement repo initializes. | Move runtime rejection from Planned to Done or Partial. |
| Foundation 2 | Atomic operation envelope and completed-operation replay. | Operation ledger, completed marker, idempotency index. | Duplicate idempotency retry no-op; conflicting idempotency key fails; incomplete operation ignored/rejected. | Update authority rows. |
| Foundation 3 | Record-instance citations and target fingerprints. | Citation creation with distinct IDs and deterministic fingerprints. | Identical evidence in distinct operations receives distinct citation IDs; retries return original operation result. | Update citation rows. |
| Foundation 4 | Groups, memberships, handles, and tallies. | Default Inbox group, group memberships, stable handle IDs, group/handle rolling tallies. | Complete tally tests, same-name ambiguity tests, rename preserves IDs. | Update group/handle rows. |
| Foundation 5 | Scoped duplicate policy and supersession. | `handle`, `group`, and `none` policies; scoped supersession events. | Dominance by canonical citation ID; scoped supersession does not globally retract. | Update duplicate rows. |
| Foundation 6 | Semantic reconciliation. | Reconcile command/engine for replacement repositories only. | Merge-direction-independent reconciliation, structural conflict tests, source-clean checks. | Update reconciliation rows. |
| Gate 9 | Chrome extension replacement integration. | Replacement-aware native host and extension protocol. | Manual Chrome tests plus replacement protocol fixture tests. | Resume only after foundations pass. |

## Historical Workflows

The old create, handle, lookup, recovery, export, and Gate 0 through v1
workflows are historical v0.3/v1 material. They may be consulted for audit, but
must not be used as active implementation contracts.
