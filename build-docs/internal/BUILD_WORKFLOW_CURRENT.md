# Current Build Workflow

This document is current internal workflow authority for Cite2Site. It defines
the practical flows implementation must support from local use through
published citation sites. Workflows are implementation contracts, not marketing
journeys.

## Maturity Boundary

The current first slice is CLI/core-first. It implements the source-clean event
and replay substrate; it does not provide a native right-click integration.
Human context-menu journeys below are Target integration workflows whose client
must call the same explicit contracts. Do not represent them as current product
interaction until an integration gate supplies code and fixtures.

## Workflow Principles

- The cited artifact remains unchanged.
- All mutating actions append events.
- Replay computes projected state.
- A future human integration should begin with a contextual action, while the
  current human-accessible surface is the CLI.
- Agents and automation should use deterministic JSON CLI commands.
- Publication is generated from the citation repository, not from hidden UI
  state.

## Session Gate Model

One normal coding session is one gate. A gate may implement one feature, one
workflow slice, one adapter increment, one docs correction, or one CI/release
slice. A gate is not accepted until code, tests, generated contracts, docs, and
status records agree.

Gate rules:

- start every gate by reading `AGENTS.md`, this workflow, the status matrix,
  the project plan, and the relevant protocol/spec sections;
- define the gate objective before editing;
- keep the gate small enough to review in one session;
- do not carry incomplete behavior across gates without recording it as
  Partial or Planned in the status matrix;
- update `CURRENT_STATUS_MATRIX.md` in the same gate when capability state
  changes;
- update protocol specs and schemas in the same gate when command behavior or
  JSON shape changes;
- update external docs only when implemented behavior is stable enough to
  describe publicly;
- apply `DOCUMENTATION_STANDARD.md` whenever requirements, workflow, or
  architecture language changes;
- reject the gate if any required validation fails or cannot run.

## Gate Validation Stack

Run the smallest relevant checks first, then the full gate stack.

Required for every implementation gate:

1. Unit tests: `python -m unittest discover -s tests`.
2. Import/compile check: `python -m compileall src`.
3. CLI help check: `python -m c2s --help`.
4. Command smoke checks for every changed command.
5. Source-clean check for any command touching cited artifacts.
6. Structured error check for every new failure path.

Required when exports, replay, or publication change:

1. Run export twice against the same fixture.
2. Compare generated JSON and Markdown outputs for determinism.
3. Confirm `metadata_only` output does not include evidence text.
4. Confirm generated MkDocs links point to existing generated pages.

Required when docs change:

1. Parse all JSON schema and example files.
2. Check local Markdown links under `build-docs/`.
3. Confirm `AGENTS.md` reading order still points to existing files.
4. Search for stale internal project references before reporting.
5. Confirm every changed behavior is labelled Implemented, Partial, Target, or
   Open in the status matrix or document scope statement.

Required in CI:

1. install the package from a clean checkout;
2. run unit tests;
3. run compile checks;
4. run CLI help and smoke checks;
5. validate docs links and JSON files;
6. run export/source-clean smoke checks.

## Actionable Phases And Gates

Each phase below is made of session-sized gates. Complete gates in order unless
the status matrix shows a gate is already Done.

| Gate | Phase | Objective | Required Deliverables | Acceptance Tests | Status Update |
|---|---|---|---|---|---|
| G0 | Baseline control | Preserve the current working first slice and make CI runnable. | CI workflow, docs link/JSON validation, CLI smoke script or inline CI smoke commands. | Unit tests, compileall, CLI help, docs validation, CI smoke locally where practical. | Mark CI baseline Done or Partial with remote-run status. |
| G1 | Grouping/indexing core | Add deterministic replay indexes. | `build_indexes`, grouped status output, artifact index population. | Unit tests for artifact, handle, tag, status, batch grouping; deterministic ordering tests. | Move grouping core from Planned to Done or Partial. |
| G2 | Grouped query CLI | Add agent-friendly query surface. | `c2s citations` with artifact, handle, tag, status, batch filters and JSON/JSONL output. | CLI subprocess tests, invalid filter/error tests, metadata-only output tests. | Update CLI/status rows. |
| G3 | Grouped export/site | Publish grouped projections. | grouped JSON exports, MkDocs group pages, generated navigation, stable slugs. | export determinism test, link existence test, privacy leakage test. | Update export and publication rows. |
| G4 | Privacy modes | Implement explicit publication privacy transforms. | `metadata_only`, `hash_only`, `snippet`, `private_link` behavior and policy checks. | privacy-mode unit tests, export tests, refusal tests for disallowed snippets. | Update privacy rows and external docs. |
| G5 | Workflow command completion | Fill recovery and lifecycle-adjacent append actions. | `accept-current`, `retract`, `restore`, `relocate`, `note`, `preflight-selection`, first-line handle mode. | success/failure tests for each command, source-clean checks, structured errors. | Update workflow and protocol rows. |
| G6 | Adapter hardening | Make future adapters safe. | adapter interface docs/tests, conformance fixtures, richer text diagnostics, Markdown summaries. | adapter conformance tests, unsupported/private/ambiguous status tests. | Update adapter rows. |
| G7 | Right-click integration contract | Prove human interactivity without overlays. | minimal editor/browser/document integration examples, action schema examples, overlap picker docs. | integration contract smoke tests or fixture tests, lookup overlap tests. | Update integration rows. |
| G8 | Release/migration hardening | Prepare a stable public release path. | release checklist, migration policy/tests, package build check, changelog/security checklist. | clean checkout CI, package build, migration fixture tests, docs validation. | Update release readiness rows. |

Gate acceptance requires all listed tests to pass. A gate can be closed as
Partial only when the missing work is explicitly listed in the status matrix
with a next action.

## Human Local Citation Workflow

**Maturity:** Target integration workflow. The implemented equivalent is an
explicit `cite-selection` CLI invocation with the same artifact/range contract.

Actors:

- everyday user;
- local editor, browser, document tool, or file manager integration;
- C2S CLI/core behind the integration.

Steps:

1. User selects evidence in a supported artifact.
2. Integration sends artifact identity, selected text, and locator/range to C2S.
3. C2S canonicalizes selected evidence.
4. C2S validates expected content hash when supplied.
5. C2S appends `citation.created`.
6. If the user supplies a handle, C2S appends `handle.bound`.
7. Integration shows citation ID and preferred handle.
8. Source artifact remains unchanged.

Exit criteria:

- citation appears in `status`;
- citation appears in export;
- source artifact bytes are unchanged;
- failure returns structured JSON error.

## Contextual Cited-Region Workflow

**Maturity:** Implemented integration contract and reference examples.
`lookup-actions` is implemented; the integration contract
(`build-docs/architecture/INTEGRATION_CONTRACT.md`) and editor plugin mock
(`examples/integration/editor_plugin_mock.py`) demonstrate the picker and
action model.  Native right-click plugins are deferred.

Actors:

- user;
- right-click integration;
- C2S `lookup-actions`.

Steps:

1. User right-clicks a cursor position or selected range.
2. Integration calls `lookup-actions`.
3. If no citation overlaps, integration shows `Cite with C2S`.
4. If one citation overlaps, integration shows direct actions.
5. If multiple citations overlap, integration shows a picker.
6. User selects a citation and action.
7. Mutating action names a concrete `citation_id`.
8. C2S appends the relevant event or rejects with a stable error code.

Overlap ordering:

1. exact selection match;
2. smallest containing citation range;
3. most recent preferred-handle binding;
4. citation ID lexical order.

Actions:

- `open`;
- `set_handle`;
- `note`;
- `accept_current`;
- `relocate`;
- `retract`;
- `restore`.

`undo`, `redo`, and `retire` are deferred to a later gate.

Exit criteria:

- ambiguous mutations fail closed;
- selected citation ID is present in the appended event;
- replay reflects the action;
- source artifact remains unchanged.

## Agent Batch Citation Workflow

Actors:

- agent or automation;
- C2S CLI/JSON.

Steps:

1. Agent identifies several evidence selections.
2. Agent builds a `cite-batch` request with `client_item_id` values.
3. C2S validates every item.
4. In `all_or_nothing` mode, any rejection prevents all appends.
5. In explicit `partial` mode, valid items append and rejected items are
   reported.
6. C2S returns `batch_id`, created citation IDs, and rejected item codes.
7. Replay and export expose the batch relationship.

Exit criteria:

- rejected items include stable codes;
- batch events share one `batch_id`;
- no partial append occurs unless requested;
- source artifacts remain unchanged.

## Handle Assignment And Rename Workflow

Actors:

- user or agent;
- C2S handle binding history.

Steps:

1. User or agent chooses a citation ID.
2. User or agent supplies handle and action: `bind`, `rename`, `alias`, or
   `retire`.
3. C2S validates handle syntax.
4. C2S checks handle collision policy.
5. C2S appends `handle.bound`.
6. Replay computes preferred handle and aliases.

Rules:

- `citation_id` never changes.
- Handle edits never rewrite citation history.
- Old handles remain aliases by default.
- Retired handles remain visible in audit history.

Exit criteria:

- status shows preferred handle;
- alias history is recoverable;
- collisions fail unless policy allows same-citation aliasing.

## Replay And Review Workflow

Actors:

- user, agent, CI, or publisher.

Steps:

1. Command reads citation and handle histories.
2. Command validates hash chains.
3. Command observes current artifact content through adapters.
4. Command compares accepted evidence to observed evidence.
5. Command emits projected citation state.

Statuses:

- `resolved`;
- `changed`;
- `missing`;
- `ambiguous`;
- `adapter_unavailable`;
- `private`;
- `unsupported`;
- `retracted`.

Exit criteria:

- status is deterministic for the same histories and artifacts;
- errors are structured;
- no command mutates history during replay.

## Grouping And Indexing Workflow

**Maturity:** Partial. G1 provides grouped replay indexes and a derived
artifact-index cache; G2 supplies deterministic query filters; G3 writes
grouped JSON and MkDocs navigation; and G4 applies privacy policy before every
replay/export projection. The generated grouped surfaces intentionally remain
metadata-safe even when a richer flat projection is authorized.

Actors:

- user;
- agent;
- MkDocs publisher;
- C2S export command.

Steps:

1. Replay produces flat citation projection.
2. Indexer groups citations by artifact, handle, alias, tag, status, and batch.
3. Export writes grouped JSON indexes.
4. MkDocs generator writes grouped pages and navigation.
5. User or agent consumes the grouped site or JSON.

Required grouped outputs:

- `exports/index-by-artifact.json`;
- `exports/index-by-handle.json`;
- `exports/index-by-tag.json`;
- `exports/index-by-status.json`;
- `exports/index-by-batch.json`;
- `site/docs/artifacts/*.md`;
- `site/docs/handles/*.md`;
- `site/docs/tags/*.md`;
- `site/docs/status/*.md`;
- `site/docs/batches/*.md`.

Exit criteria:

- grouping is deterministic;
- metadata-only privacy is preserved;
- empty groups are omitted;
- links between citation pages and group pages are stable.

## Publication Workflow

**Maturity:** Implemented privacy contract. `metadata_only` is the default;
`hash_only` omits accepted text; `snippet` requires explicit text-release
authorization; and `private_link` requires an explicit HTTPS base URL. A
generated page remains a derived projection, not publication approval for a
specific hosting environment.

Actors:

- maintainer or ordinary user;
- C2S export;
- MkDocs;
- static host.

Steps:

1. User runs `c2s export`.
2. C2S writes JSON projections and MkDocs Markdown.
3. User previews the site locally.
4. Git-backed citation repo publishes through GitHub Pages or another static
   host.
5. User shares site URL with people or agents.

Privacy modes:

- `metadata_only`;
- `hash_only`;
- `snippet`;
- `private_link`.

`snippet` and `private_link` requests without their matching repository policy
fail with `E_PRIVACY_POLICY`. Generated MkDocs group pages remain
metadata-safe; rich fields are limited to the authorized flat projection.

Exit criteria:

- `metadata_only` is default;
- public export does not leak evidence text by default;
- generated pages are deterministic;
- broken artifact links do not break site generation.

Local preview is reproducible after installing MkDocs outside the stdlib core:
`python -m mkdocs serve -f .c2s/site/mkdocs.yml`. Static hosting publishes the
generated `.c2s/site` projection; it never replaces citation history authority.

## CI And Maintainer Workflow

Actors:

- project maintainer;
- CI runner;
- C2S check/export commands.

Steps:

1. CI installs package.
2. CI runs tests.
3. CI runs `c2s check` on any sample citation repositories.
4. CI runs export smoke tests.
5. CI optionally builds MkDocs.

Exit criteria:

- unit tests pass;
- command smoke tests pass;
- generated docs are deterministic;
- no source artifact mutation occurs in tests.

## Adapter Hardening Workflow

**Maturity:** Implemented in G6. The adapter protocol (`src/c2s/adapter.py`)
defines `BaseAdapter` with eight contract methods. `FilesystemTextAdapter` and
`MarkdownAdapter` pass the conformance harness (`tests/test_adapter_conformance.py`).
Workspace boundary enforcement (`E_ARTIFACT_OUTSIDE_WORKSPACE`) prevents
artifact-path escapes.

## Integration Contract Workflow

**Maturity:** Implemented in G7. The integration contract
(`build-docs/architecture/INTEGRATION_CONTRACT.md`) and reference examples
(`examples/integration/`) document the interaction model for editor, browser,
and document-tool implementers. A thin-client library and editor plugin mock
demonstrate the lookup → picker → action loop without storing overlay state.

## Recovery Workflow

**Maturity:** Implemented in G5. `accept-current`, `retract`, `restore`,
`relocate`, and `note` are delivered with append-only events and idempotency
guards. `undo` and `redo` command aliases are deferred to a later gate.

Recovery must preserve append-only history.

Cases:

- wrong evidence cited: append retraction and create a new citation;
- wrong handle: append rename or alias event;
- moved evidence: append relocation after review;
- changed evidence: append accepted evidence only after explicit acceptance;
- missing artifact: report `missing` and wait for user action;
- chain validation failure: stop mutation and require repair from backup or Git
  history.

Exit criteria:

- repair does not rewrite existing events;
- recovery action is visible in replay;
- command reports stable error code when recovery cannot proceed.
