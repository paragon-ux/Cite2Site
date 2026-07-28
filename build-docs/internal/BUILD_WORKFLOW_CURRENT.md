# Current Build Workflow

**Status:** active workflow authority.

## Active Gate

The active gate sequence is the replacement `R0` through `R9` sequence. The
current repository is completing `R0` and then proceeds gate-by-gate through
the replacement runtime foundations before `R9` integration work.

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
| R0 | External archive and replacement authority spine. | `Cite2Site-Archival/` copy, archived files removed from repo, replacement docs in active slots, gate prompts R0-R9. | Docs link/schema checks; stale active-reference search; archive folder existence check. | Mark archival separation Done only after old files are absent from repo. |
| R1 | Repository identity and fail-closed archived-format detection. | Replacement `project.json`, `init`, schema validation, archived-format error before writes. | New repo initializes; v0.3/v1 repo rejects before replay or mutation; no archive writes. | Runtime rejection Done. |
| R2 | Atomic operations and idempotency. | Operation ledger, completed marker, semantic payload hash, idempotency index. | Same-key retry no-op; key conflict fails; incomplete operation rejected or ignored before replay. | Authority rows Done or Partial. |
| R3 | Record-instance citations and fingerprints. | Citation creation, source observation, deterministic `target_fingerprint`. | Identical evidence in distinct operations receives distinct citation IDs; source bytes unchanged. | Citation rows Done or Partial. |
| R4 | Groups and memberships. | Default Inbox group, group create/rename/move, memberships, group tallies. | Group IDs stable; same-name groups ambiguous; group tallies complete. | Group rows Done or Partial. |
| R5 | Handles and bindings. | Group-owned handle IDs, handle create/rename/merge, bindings, handle tallies. | Handle IDs stable; same-name handles ambiguous; handle tallies complete. | Handle rows Done or Partial. |
| R6 | Scoped duplicate policy and supersession. | `handle`, `group`, `none` policies and scoped supersession events. | Dominance by canonical citation ID; scoped supersession does not globally retract. | Duplicate rows Done or Partial. |
| R7 | Semantic reconciliation. | Replacement-only reconcile command/engine and structural conflict detection. | Merge-direction-independent reconciliation; invalid/archived histories stop before writes. | Reconciliation rows Done or Partial. |
| R8 | Projections and publication. | Status, export, site projections, metadata-only default, derived-regeneration rules. | Metadata-only no-leak; deterministic export; source-clean publication. | Publication rows Done or Partial. |
| R9 | Replacement integration and Chrome extension. | Replacement-aware native-host message contract, extension UI, package build. | Fixture tests, native-host smokes, package build, manual Chrome validation. | Integration rows Done only after manual milestone validation. |

## Historical Workflows

The old create, handle, lookup, recovery, export, and Gate 0 through v1
workflows are historical v0.3/v1 material stored outside this repository in
`Cite2Site-Archival/`. They may be consulted for audit, but must not be used
as active implementation contracts.
