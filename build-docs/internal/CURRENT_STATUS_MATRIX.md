# Current Status Matrix

This is the sole authority for whether a capability is available in the current
checkout. Target specifications define intended behavior; they do not override
this evidence-based report.

Status meanings:

- **Done**: implemented and covered by tests or smoke checks.
- **Partial**: implemented in a limited form, with clear gaps.
- **Planned**: accepted design direction, not implemented.
- **Deferred**: intentionally out of the current release path.

Evidence is required for every Done or Partial row. A function name, schema, or
future-phase prompt is not sufficient evidence by itself. See
`DOCUMENTATION_STANDARD.md` for the wider truth-label rule.

## Practical Status Statement

Cite2Site has a working local first slice, but it is not yet a complete v0.3.0
release. The implemented substrate proves the append-only event model,
source-clean citation creation, batch citation, handle binding, contextual
lookup, replay status, metadata-only export, structured JSON errors, and unit
test baseline.

The current blocking product gap is grouping and indexing. Without grouped
artifact, handle, tag, status, and batch indexes, the generated site remains a
flat citation ledger rather than a useful citation memory surface.

## Capability Matrix

| Area | Capability | Status | Current Evidence | Gap | Next Action |
|---|---|---:|---|---|---|
| Repository | Initialize dedicated citation repo | Done | `init_repo()` creates `.c2s/project.json`, history files, exports, and site scaffold. | None for first slice. | Add migration handling when schemas change. |
| Repository | Citation history append chain | Done | `append_event()` writes hash-chained JSONL events; `check` validates chains. | No cross-file transaction envelope yet. | Add transaction/event-set validation before multi-file append grows. |
| Repository | Handle binding history | Done | `.c2s/handle-bindings.jsonl`; `set-handle`; replay aliases. | No dedicated handle index export yet. | Add grouped handle index in indexing milestone. |
| Repository | Artifact index | Partial | `.c2s/artifact-index.jsonl` is created. | It is not populated or consumed. | Implement artifact index population during cite/replay/export. |
| Adapters | Filesystem text adapter | Done | Text selection, canonicalization, locator, observation, status tests. | No binary text detection beyond UTF-8 decode failure. | Add explicit adapter diagnostics. |
| Adapters | Markdown adapter | Done | `.md` defaults to `markdown`; current behavior uses text semantics. | No Markdown block-aware summaries. | Add optional block summaries after text behavior is stable. |
| Adapters | PDF, DOCX, spreadsheet, browser, conversation | Planned | Listed in product direction. | No implementation or tests. | Add one adapter at a time after adapter conformance tests exist. |
| Citation | `cite-selection` | Done | CLI and core create source-clean citation events. | No right-click plugin yet. | Keep CLI stable while integration examples are added. |
| Citation | `cite-batch` all-or-nothing | Done | Tests prove invalid batch appends nothing; request schema exists in `build-docs/architecture/schemas/cite-batch-request.schema.json`. | No runtime schema validator yet. | Add schema validation when public input hardening begins. |
| Citation | `cite-batch` partial mode | Done | Tests prove valid items append and rejected items report. | No policy controls for allowing partial mode. | Add repository policy gate before public release. |
| Citation | Expected content hash | Done | `E_CONTENT_HASH_MISMATCH` protects selected content. | Not exposed as a helper command. | Add `preflight-selection` or dry-run output if needed. |
| Handles | Create handle during citation | Done | `--handle` on `cite-selection` and batch item `handle`. | No first-line handle mode yet. | Add first-line mode after grouping/indexing. |
| Handles | Rename, alias, retire | Partial | `set-handle` supports actions and replay aliases. | Retire behavior is basic; no CLI query for alias history. | Add handle history export and tests. |
| Context menu | `lookup-actions` | Done | Returns matches, actions, and `requires_picker`. | No plugin package for editor/browser UI. | Add integration examples after action schema hardens. |
| Context menu | Overlap ordering | Partial | Exact match, range size, handle presence, citation ID. | Target ordering requires most recent binding order, not merely handle presence. | Replace handle-presence sort with binding order and add fixture tests. |
| Replay | Status projection | Done | `resolved`, `changed`, `missing`, `unsupported`, `retracted` paths exist. | `ambiguous`, `private`, and `adapter_unavailable` need stronger paths. | Add tests and explicit projection logic. |
| Replay | Citation grouping | Planned | Tags, handles, artifact URI are present in records. | No grouped projections. | Implement grouping indexes. |
| Export | Flat JSON status | Done | `.c2s/exports/c2s-status.json`. | No grouped indexes. | Add artifact/tag/handle/batch indexes. |
| Export | Flat JSONL citations | Done | `.c2s/exports/c2s-citations.jsonl`. | No query-specific JSONL outputs. | Add deterministic grouped JSON files. |
| Export | MkDocs scaffold | Done | `.c2s/site/mkdocs.yml`, `index.md`, `citations.md`. | No artifact/tag/handle pages. | Add grouped MkDocs pages and navigation. |
| Privacy | Metadata-only default | Partial | Project policy and export default are `metadata_only`. | The current privacy transform is a no-op; no test yet proves default export suppresses evidence text. | Implement explicit transforms and no-leak tests before publication claims. |
| Errors | Structured JSON errors | Done | `C2SError`; JSON argparse usage errors; tests. | No public error-code catalog. | Add error catalog to spec. |
| Testing | First-slice unit tests | Done | `tests/test_first_slice.py`, 10 tests. | No committed subprocess integration test module yet. | Add subprocess smoke tests as formal tests when CLI surface grows. |
| Testing | Session gate model | Done | `BUILD_WORKFLOW_CURRENT.md` defines one-session gates G0 through G8 and validation requirements. | Gates are documentation-enforced until CI expands per phase. | Keep each phase prompt aligned with gate acceptance. |
| Testing | CI validation workflow | Partial | `.github/workflows/ci.yml` and `build-docs/internal/CI_VALIDATION.md` validate docs, unit tests, compile checks, CLI help, and smoke behavior from a clean checkout. | Remote GitHub Actions run has not been observed in this branch. | Confirm first remote CI run after push and fix any platform issue. |
| Packaging | Editable install | Done | `pyproject.toml`; `python -m pip install -e .` passed locally. | No CI or release build artifact. | Add CI matrix and release workflow. |
| Docs | Build contract | Done | Internal requirements, workflow, plan, specifications, external narratives, ADRs, and documentation standard are present; live Markdown links validate. | Documents must continue to track implementation maturity. | Require truth-label and cross-reference review in every behavior-changing gate. |

## Release Readiness By Version

| Version | Release Goal | Readiness | Exit Criteria |
|---|---|---:|---|
| v0.3.0 | Local first slice | Partial | Grouping/indexing, privacy transforms, CLI query filters, and docs complete. |
| v0.4.0 | Publishable citation site | Planned | MkDocs grouped pages, GitHub Pages guide, privacy modes, and static output tests. |
| v0.5.0 | Integration-ready C2S | Planned | Right-click integration examples, stable `lookup-actions`, adapter conformance tests. |
| v0.6.0 | Agent-first automation | Planned | Batch policies, idempotency, full JSON schemas, CI checks, and recovery workflows. |
| v1.0.0 | Public stable release | Planned | Schema freeze, migration rules, threat model, docs, examples, CI, and release artifacts. |

## Known Current Gaps

1. Grouping and indexing are not implemented beyond flat status/export.
2. Artifact index is created but not populated.
3. MkDocs output is useful but minimal.
4. Privacy modes other than `metadata_only` are not functionally distinct yet.
5. First-line handle mode is not implemented.
6. Adapter support is text-first; richer file types are not present.
7. CI workflow exists locally, but no remote run has been observed yet.
8. JSON Schema files exist for current public request/response examples, but
   runtime schema validation is not implemented.
9. No migration command exists because there is only one implementation schema.
10. No editor/browser/document integration package exists yet.
11. The worktree omits external narratives and ADRs named by the historical
    map; do not claim a complete documentation set until the owner restores or
    intentionally replaces them.

## Immediate Next Build: Grouping And Indexing

Implement citation grouping and indexing:

1. populate `artifact-index.jsonl`;
2. add replay indexes by artifact, handle, tag, status, and batch;
3. add `citations` query command with filters;
4. export grouped JSON files;
5. generate MkDocs artifact, handle, tag, status, and batch pages;
6. add tests for deterministic grouping and privacy-safe output.
