# Agent Guidance

Cite2Site is source-clean and append-only.

## Fresh Agent Reading Order

`AGENTS.md` is the single source of truth for fresh agent orientation. Read
these files in order before implementation:

1. `AGENTS.md` for invariants, scope boundaries, and gate rules.
2. `build-docs/README.md` for the active documentation map.
3. `build-docs/internal/CURRENT_STATUS_MATRIX.md` for current capability state.
4. `build-docs/internal/BUILD_WORKFLOW_CURRENT.md` for user, agent, CI, and
   release workflows.
5. `build-docs/internal/CI_VALIDATION.md` for automated gate checks.
6. `build-docs/internal/PROJECT_PLAN.md` for phase order and milestone scope.
7. `build-docs/architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md` for command
   contracts.
8. `build-docs/architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md` for engine
   contracts.
9. `build-docs/architecture/SCHEMA_INDEX.md` and referenced schemas/examples
   when request or response shapes change.
10. Relevant ADRs in `build-docs/internal/adrs/` when changing an architectural
   invariant.
11. The phase prompt in `build-docs/internal/phase_prompts/` for the active
    implementation phase, when one exists.

Do not rely on historical summaries when the current build docs and source
files disagree. Prefer current source, protocol specs, status matrix, and ADRs.

## Core Invariants

- Do not add markers to cited artifacts.
- Treat `.c2s/citation-history.jsonl` and `.c2s/handle-bindings.jsonl` as the
  authority files.
- Treat status, exports, and MkDocs pages as replay projections.
- Handles are editable aliases, not citation identity.
- For overlapping contextual hits, mutating actions must name a concrete
  `citation_id`.
- Static-site publication defaults to metadata-only.
- Use `build-docs/` for project planning, requirements, workflows, technical
  specification, current status, and ADR context.

## Session Gate Protocol

Assume one regular coding session is one acceptance gate. A gate is accepted
only when implementation, tests, docs, and status updates for that session are
complete.

Before editing:

- inspect `git status --short`;
- identify the active phase and gate in
  `build-docs/internal/BUILD_WORKFLOW_CURRENT.md`;
- confirm the change maps to the status matrix, project plan, requirements,
  and architecture specs.

During implementation:

- keep cited artifacts source-clean;
- append authority state only, never rewrite event history;
- update docs in the same patch as behavior changes;
- add or update tests for every new behavior and failure mode.

Before reporting changes, run the relevant gate validation:

- `python -m unittest discover -s tests`;
- `python -m compileall src`;
- CLI smoke checks for changed commands;
- docs validation when `build-docs/`, `README.md`, or `AGENTS.md` changes;
- export determinism or source-clean checks when generated output or artifact
  mutation behavior changes.

If any required validation cannot run, report the exact blocker and do not mark
the gate accepted.
