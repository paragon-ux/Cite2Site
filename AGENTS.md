# Agent Guidance

Welcome. You are working on Cite2Site, a source-clean, append-only citation
tool. Read this file before touching code or docs.

## Current Boundary

Cite2Site is in the **Replacement Protocol and Archival Separation Gate**.
The v0.3/v1 implementation and documents are historical material preserved by
Git history and by the archive index. They are no longer active protocol
authority.

Do not resume Gate 9 / Phase 7 Part 2 Chrome-extension work until the
replacement authority package and foundation implementation are complete.

## Start Here, In Order

1. `AGENTS.md`.
2. `build-docs/README.md`.
3. `build-docs/internal/CURRENT_STATUS_MATRIX.md`.
4. `build-docs/internal/BUILD_WORKFLOW_CURRENT.md`.
5. `build-docs/internal/CI_VALIDATION.md`.
6. `build-docs/internal/PROJECT_PLAN.md`.
7. `build-docs/architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md`.
8. `build-docs/architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md`.
9. `build-docs/architecture/ARCHIVAL_BOUNDARY.md`.
10. `build-docs/architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md`.
11. `build-docs/architecture/REPLACEMENT_SCHEMA_INDEX.md`.
12. Relevant ADRs in `build-docs/internal/adrs/`.
13. `build-docs/internal/phase_prompts/REPLACEMENT_PROTOCOL_ARCHIVAL_SEPARATION_GATE.md`.

If a historical summary or archived document disagrees with current source,
the status matrix, or active ADRs, trust the active source and docs.

## Non-Negotiable Invariants

- Cited artifacts stay source-clean. Do not add comments, bookmarks, IDs, or
  hidden markers to cited files.
- Authority remains append-only. Existing completed authority records are not
  rewritten or deleted.
- Status, exports, generated indexes, and MkDocs output are replay projections,
  not sources of truth.
- Publication defaults to metadata-only and must not expose evidence text
  unless explicitly authorized.
- The archived v0.3/v1 ledger model based on `.c2s/citation-history.jsonl` and
  `.c2s/handle-bindings.jsonl` is unsupported by the active replacement
  runtime.
- Replacement citation IDs identify intentional record instances. They are not
  derived solely from evidence identity or target fingerprints.
- Replacement groups and handles are stable authority objects with immutable
  IDs. Names and paths are mutable display data, not identity.
- Duplicate handling is scoped through group and handle policy. Duplicate
  evidence must not suppress intentional citation creation.
- Mutating commands require stable `operation_id` and `idempotency_key`.
- Replay processes only completed atomic operations.
- Semantic reconciliation applies only to repositories that already conform to
  the replacement protocol and share valid replacement ancestry.
- Archived-format repositories fail closed before replay, mutation,
  reconciliation, projection, or publication. This task does not authorize
  runtime migration or import.

## Session Rule

One regular coding session is one acceptance gate. A gate is accepted only when
implementation, tests, docs, and status evidence agree.

Before editing:

- run `git status --short`;
- confirm the active gate in `build-docs/internal/BUILD_WORKFLOW_CURRENT.md`;
- confirm the change maps to the status matrix, project plan, requirements,
  active architecture policy/spec, and schema package.

While implementing:

- keep cited artifacts source-clean;
- append authority rather than rewriting it;
- keep docs and tests in the same patch as behavior changes;
- preserve unrelated user changes;
- do not continue old-model behavior merely because old tests or docs exist.

Before reporting a gate as done, run the validation required by
`build-docs/internal/CI_VALIDATION.md` and the active gate prompt. If validation
cannot run, report the blocker and do not mark the gate accepted.
