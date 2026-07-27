# Cite2Site Project Plan

**Status:** current internal project plan.

This plan is execution authority for sequencing. The current status matrix is
the authority for what is already complete.

## Objective

Build Cite2Site into a source-clean universal citation system that lets humans
eventually cite evidence through a right-click integration, lets agents cite and
query evidence through deterministic JSON, and publishes a durable citation
site through MkDocs and ordinary static hosting. The current first slice is the
CLI/core substrate for that experience, not the completed experience itself.

## Product Thesis

Citations should be durable without requiring source markers, proprietary note
apps, or project-specific requirement systems. Cite2Site stores citation
history beside the user's work, replays it against current artifacts, and
publishes metadata-safe citation indexes that humans and agents can inspect.

## Success Definition

Cite2Site is successful when:

1. ordinary users can cite evidence without editing the source artifact;
2. agents can create single or batch citations and receive deterministic JSON;
3. handles are editable aliases over immutable citation IDs;
4. overlapping citations are manageable from contextual menus;
5. citation history is append-only and hash-validated;
6. grouped indexes make citations navigable by artifact, handle, tag, status,
   and batch;
7. MkDocs output can publish through GitHub Pages or another static host;
8. privacy defaults prevent accidental evidence leakage;
9. every command has structured errors;
10. the project has tests, CI, release docs, and migration rules.

Success is evidence-based: each statement above requires a corresponding status
row, acceptance test, and authority document. A planning milestone cannot make
a capability available by declaration.

## Scope

In scope:

- local citation repository;
- append-only event histories;
- source-clean text and Markdown citations;
- batch citation;
- handle binding;
- contextual lookup;
- replay status;
- grouping and indexing;
- metadata-safe export;
- MkDocs site generation;
- CLI-first agent surface;
- integration contracts for right-click tools.

Out of scope for early releases:

- semantic equivalence inference;
- source-persisted markers;
- proprietary cloud sync;
- mandatory Git dependency for cited artifacts;
- first-party full editor/browser plugins before the CLI contracts stabilize;
- rich non-text adapters before adapter tests exist.

## Milestone Plan

Milestones are delivered through session gates defined in
`BUILD_WORKFLOW_CURRENT.md`. One normal coding session should close one gate.
If a session cannot close a gate, record the remaining work in the current
status matrix before stopping.

### M0: Foundation

Status: Done.

Deliverables:

- repository scaffold;
- Python package;
- core CLI;
- first-slice tests;
- append-only event chains;
- metadata-only export.

Acceptance:

- `python -m unittest discover -s tests` passes;
- editable install works;
- CLI smoke test covers `init`, `cite-selection`, `lookup-actions`, `status`,
  `export`, and `check`.

Residual limitations at the initial slice: export was flat, privacy modes beyond
the default were not behavioral transforms, and right-click interaction was not
shipped. Grouping and privacy delivery below supersede the first two limits.

### M1: Grouping And Indexing

Gate: G1 through G3.

Goal: make citation collections navigable instead of flat.

Current delivery: G1 provides deterministic in-memory indexes and derived
artifact-cache population; G2 makes the collection queryable through the CLI;
and G3 writes the grouped JSON and MkDocs navigation projections. G4 completes
the privacy boundary for flat publication projections.

Deliverables:

- populate `artifact-index.jsonl`;
- replay indexes by artifact, handle, tag, status, and batch;
- `citations` query command with filters;
- grouped JSON exports;
- MkDocs artifact, handle, tag, status, and batch pages;
- tests for deterministic grouping and metadata-only privacy.

Acceptance:

- every citation appears in all relevant indexes;
- output order is deterministic;
- empty groups are omitted;
- old handles resolve as aliases;
- grouped pages never expose evidence text in `metadata_only`.

### M2: Privacy And Publication

Gate: G4.

Goal: make static publication safe and useful.

Current delivery: G4 implements deterministic `metadata_only` and `hash_only`
transforms, policy-gated snippet and private-link projections, and no-leak
refusal coverage. Grouped MkDocs pages remain metadata-safe by design.

Deliverables:

- privacy transform implementation for `metadata_only`, `hash_only`,
  `snippet`, and `private_link`;
- repository policy for allowed publication mode;
- static-host publication guidance for generated navigation;
- local preview instructions;
- export determinism tests.

Acceptance:

- default export is metadata-only;
- snippets require explicit policy;
- local preview instructions are reproducible;
- generated files are stable across repeated exports with unchanged inputs.

### M3: Workflow Completeness

Gate: G5.

Goal: make local and agent workflows complete without converting replay or UI
state into authority.

Deliverables:

- `accept-current`;
- `retract`;
- `restore`;
- `relocate`;
- `note`;
- first-line handle mode;
- `preflight-selection` dry run;
- command reference docs;
- error-code catalog.

Acceptance:

- all user-facing actions are append-only;
- every implemented workflow in `BUILD_WORKFLOW_CURRENT.md` maps to commands;
- all commands support structured JSON errors;
- no command rewrites cited artifacts.

### M4: Adapter Hardening

Gate: G6.

Status: Done.

Goal: make adapter growth safe.

Current delivery: G6 delivers the adapter protocol (`src/c2s/adapter.py`) with
`BaseAdapter` ABC and `FilesystemTextAdapter`/`MarkdownAdapter` implementations;
a 35-test conformance harness (`tests/test_adapter_conformance.py`); workspace
boundary enforcement (`E_ARTIFACT_OUTSIDE_WORKSPACE`); and six stable adapter
diagnostic codes. Markdown block summaries, a conversation export adapter, and
a PDF text adapter are deferred.

### M5: Integration Examples

Gate: G7.

Status: Done.

Goal: prove right-click interaction without making UI authority.

Current delivery: G7 delivers the integration contract
(`build-docs/architecture/INTEGRATION_CONTRACT.md`) and editor plugin mock
(`examples/integration/editor_plugin_mock.py`); updated fixtures and thin-client
reference. Browser-extension and document-tool examples are deferred.

### M6: CI, Release, And Migration

Gate: G0 and G8.

Status: Done.

Goal: make the project maintainable.

Current delivery: CI workflow (`.github/workflows/ci.yml`), first remote CI run observed passing, package build check,
release checklist, schema migration policy, changelog, security checklist,
and migration fixture tests (`tests/test_migration_fixtures.py`).

### M7: v1.0 Stabilization

Status: Done (v1.0 contracts frozen, guides published, release docs finalized).

Goal: freeze stable user and agent contracts.

Deliverables:

- v1 event schema;
- stable CLI;
- stable JSON schemas;
- stable MkDocs projection shape;
- complete user guide;
- complete agent guide;
- examples for common workflows.

Acceptance:

- no known untested authority paths;
- no known privacy leaks in default publication;
- docs, tests, and implementation agree on command behavior;
- migration path exists for all prior release schemas.

## Work Breakdown Structure

| Workstream | Owner Role | Deliverables |
|---|---|---|
| Core engine | Maintainer / agent | event append, chain validation, replay, statuses |
| CLI | Maintainer / agent | commands, JSON output, errors, help text |
| Indexing | Maintainer / agent | grouped indexes and query filters |
| Publication | Maintainer / agent | MkDocs pages, privacy transforms, static-host docs |
| Adapters | Maintainer / agent | adapter interface, conformance tests, file-type support |
| Integrations | Maintainer / integrator | right-click examples, action lookup, overlap picker |
| Quality | Maintainer / CI | tests, smoke checks, release gates |
| Documentation | Maintainer / writer | whitepaper, spec, workflows, user guide, agent guide |

## Dependency Order

1. Keep append-only event model stable.
2. Add grouped replay indexes.
3. Add query command over indexes.
4. Add grouped export.
5. Add grouped MkDocs pages.
6. Add privacy transforms.
7. Add workflow commands.
8. Add adapter conformance.
9. Add integrations.
10. Add CI/release/migration.
11. Freeze v1 stable contracts, publish user/agent guides, finalize release docs.

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Old handles break links after rename | Published links become brittle. | Preserve old handles as aliases by default. |
| Export leaks evidence text | Privacy failure. | Default `metadata_only`; require explicit snippet policy. |
| Overlapping citations cause wrong mutation | Data integrity issue. | Require concrete `citation_id` for mutation. |
| Adapter guesses evidence | False citation authority. | Fail closed and require explicit acceptance. |
| Batch partial writes surprise users | Audit confusion. | Default all-or-nothing; explicit partial mode only. |
| Hash chain corruption blocks work | Repository unusable until repaired. | Stop mutation, report code, recover from Git/backup. |
| MkDocs grows into authority | Architectural drift. | Treat site output as projection only. |
| Integration owns hidden state | Cross-tool inconsistency. | Integrations call `lookup-actions`; C2S remains authority. |
| Target language is read as availability | Incorrect adoption or unsafe automation. | Require status evidence and the documentation standard in every release gate. |

## Acceptance Gates

Every session gate must pass:

- unit tests for new behavior;
- compile/import checks;
- CLI smoke test for new commands;
- source-clean mutation check;
- structured error check;
- deterministic export check where output is generated;
- JSON schema/example parse checks when architecture files change;
- Markdown link checks when docs change;
- documentation update for new user/agent behavior.
- truth-label and cross-reference review for every architecture or workflow
  change.

The gate list and exact validation stack live in
`BUILD_WORKFLOW_CURRENT.md`. The project plan defines sequencing; the workflow
defines session-level acceptance.

## Definition Of Done

A capability is done only when:

1. behavior is implemented;
2. tests cover success and failure paths;
3. CLI output is structured;
4. source artifacts are not rewritten;
5. docs describe the behavior accurately;
6. generated outputs are deterministic;
7. privacy behavior is explicit;
8. current-status matrix is updated.
