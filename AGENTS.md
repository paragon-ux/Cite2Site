# Agent Guidance

Welcome — you're picking up work on Cite2Site, a source-clean, append-only
citation tool. This file is your orientation. Read it before touching any
code or docs.

The short version: Cite2Site never edits the files people cite. Every
citation is recorded externally in an append-only history, and everything
else — status, exports, the published site — is a replay of that history.
Keep that in mind and most of the rules below will feel obvious.

## Start Here, In Order

`AGENTS.md` (this file) is the single source of truth for fresh-agent
orientation. Read these in order before implementing anything:

1. `AGENTS.md` — you're here. Invariants, scope boundaries, gate rules.
2. `build-docs/README.md` for the active documentation map.
3. `build-docs/internal/CURRENT_STATUS_MATRIX.md` for what's actually built
   versus planned.
4. `build-docs/internal/BUILD_WORKFLOW_CURRENT.md` for how users, agents,
   CI, and releases fit together.
5. `build-docs/internal/CI_VALIDATION.md` for the automated gate checks.
6. `build-docs/internal/PROJECT_PLAN.md` for phase order and milestone
   scope.
7. `build-docs/architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md` for command
   contracts.
8. `build-docs/architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md` for
   engine contracts.
9. `build-docs/architecture/SCHEMA_INDEX.md` and the referenced
   schemas/examples, whenever a request or response shape changes.
10. Relevant ADRs in `build-docs/internal/adrs/`, whenever an architectural
    invariant changes.
11. The matching phase prompt in `build-docs/internal/phase_prompts/`, if
    one exists for the active phase.

If a historical summary (including this file, from memory) ever disagrees
with current source, the status matrix, or the ADRs — trust the current
source and docs, not the summary.

## The Rules That Actually Matter

These are non-negotiable, because they're what makes Cite2Site trustworthy:

- **Never mark up cited artifacts.** No comments, bookmarks, or injected
  IDs — the source stays exactly as the user left it.
- **`.c2s/citation-history.jsonl` and `.c2s/handle-bindings.jsonl` are the
  only authority files.** Everything else is derived from them.
- **Status pages, exports, and the MkDocs site are replay projections**,
  not sources of truth. Never treat generated output as authoritative.
- **Handles are editable aliases, not identity.** A citation's real
  identity is its citation ID; renaming a handle never changes what it
  points to.
- **When contextual hits overlap, mutating actions must name a concrete
  `citation_id`.** Never guess which citation the user meant.
- **Static-site publication defaults to metadata-only.** Don't expose
  evidence text unless the user has explicitly opted in.
- **`build-docs/` is where planning, requirements, workflow, spec, status,
  and ADR context live.** Check it before assuming scope.

## Session = One Gate

Treat one regular coding session as one acceptance gate. A gate is only
"accepted" once implementation, tests, docs, and status updates for that
session are all done — a half-finished gate isn't a finished gate.

**Before you start editing:**

- run `git status --short` to see what's already in flight;
- check `build-docs/internal/BUILD_WORKFLOW_CURRENT.md` for the active
  phase and gate;
- confirm your change maps to the status matrix, project plan,
  requirements, and architecture specs. If it doesn't map anywhere, that's
  a sign to update the docs first, or to treat the change as out of scope.

**While you're implementing:**

- keep cited artifacts source-clean;
- append to authority state — never rewrite event history;
- update docs in the same patch as the behavior change, not a follow-up;
- add or update tests for every new behavior and failure mode.

**Before you report the change as done, run the gate validation:**

- `python -m unittest discover -s tests`;
- `python -m compileall src`;
- CLI smoke checks for any commands you touched;
- docs validation, if `build-docs/`, `README.md`, or `AGENTS.md` changed;
- export determinism or source-clean checks, if generated output or
  artifact mutation behavior changed.

If any of these can't run, say exactly what's blocking you and don't mark
the gate as accepted. A clearly reported blocker is far more useful than an
optimistic "done."
