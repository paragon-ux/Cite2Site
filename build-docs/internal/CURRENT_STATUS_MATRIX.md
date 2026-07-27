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

G1 supplies deterministic replay indexes and a populated derived artifact
cache; G2 supplies index-backed query filters; G3 supplies grouped JSON
exports and MkDocs navigation; and G4 supplies enforced, policy-gated privacy
transforms for replay and export projections. Recovery workflows, richer
adapters, and native integrations remain separate work.

## Capability Matrix

| Area | Capability | Status | Current Evidence | Gap | Next Action |
|---|---|---:|---|---|---|
| Repository | Initialize dedicated citation repo | Done | `init_repo()` creates `.c2s/project.json`, history files, exports, and site scaffold. | None for first slice. | Add migration handling when schemas change. |
| Repository | Citation history append chain | Done | `append_event()` writes hash-chained JSONL events; `check` validates chains. | No cross-file transaction envelope yet. | Add transaction/event-set validation before multi-file append grows. |
| Repository | Handle binding history | Done | `.c2s/handle-bindings.jsonl`; `set-handle`; replay aliases. | No dedicated handle index export yet. | Add grouped handle index in indexing milestone. |
| Repository | Artifact index | Done | Successful authority mutations and export deterministically refresh `.c2s/artifact-index.jsonl` from replay. | It is a derived cache, not replay authority; read-only replay deliberately does not refresh it. | Retain the cache contract through future migrations. |
| Adapters | Filesystem text adapter | Done | Text selection, canonicalization, locator, observation, status tests. | No binary text detection beyond UTF-8 decode failure. | Add explicit adapter diagnostics. |
| Adapters | Markdown adapter | Done | `.md` defaults to `markdown`; current behavior uses text semantics. | No Markdown block-aware summaries. | Add optional block summaries after text behavior is stable. |
| Adapters | PDF, DOCX, spreadsheet, browser, conversation | Planned | Listed in product direction. | No implementation or tests. | Add one adapter at a time after adapter conformance tests exist. |
| Citation | `cite-selection` | Done | CLI and core create source-clean citation events. | No right-click plugin yet. | Keep CLI stable while integration examples are added. |
| Citation | `cite-batch` all-or-nothing | Done | Tests prove invalid batch appends nothing; request schema exists in `build-docs/architecture/schemas/cite-batch-request.schema.json`. | No runtime schema validator yet. | Add schema validation when public input hardening begins. |
| Citation | `cite-batch` partial mode | Done | Tests prove valid items append and rejected items report. | No policy controls for allowing partial mode. | Add repository policy gate before public release. |
| Citation | Expected content hash | Done | `E_CONTENT_HASH_MISMATCH` protects selected content; `preflight-selection` returns the selected evidence contract without appending history. | No batch preflight command. | Add only if batch review needs a distinct contract. |
| Citation | `citations` query filters | Done | Index-backed artifact, handle/alias, tag, status, and batch filters support deterministic JSON and JSONL output. | Query output intentionally remains metadata-safe in every privacy mode. | Retain metadata-safe query tests through later CLI changes. |
| Handles | Create handle during citation | Done | `--handle`, batch item `handle`, and opt-in `cite-selection --handle-from-first-line`. | First-line parsing is not available in batch requests. | Add only with a batch schema revision. |
| Handles | Rename, alias, retire | Partial | `set-handle` supports actions and replay aliases. | Retire behavior is basic; no CLI query for alias history. | Add handle history export and tests. |
| Context menu | `lookup-actions` | Done | Returns matches, actions, and `requires_picker`. | No plugin package for editor/browser UI. | Add integration examples after action schema hardens. |
| Context menu | Overlap ordering | Partial | Exact match, range size, handle presence, citation ID. | Target ordering requires most recent binding order, not merely handle presence. | Replace handle-presence sort with binding order and add fixture tests. |
| Replay | Workflow compensation | Done | `accept-current`, `retract`, `restore`, `relocate`, and `note` append deterministic citation events; unchanged state requests are idempotent. | No explicit undo/redo command aliases. | Keep compensating actions as the authoritative recovery model. |
| Replay | Status projection | Done | `resolved`, `changed`, `missing`, `unsupported`, and `retracted` paths exist. | `ambiguous`, `private`, and `adapter_unavailable` need stronger paths. | Add tests and explicit projection logic. |
| Replay | Citation grouping | Done | Replay indexes, query filters, grouped JSON exports, and MkDocs navigation cover artifact, handle/alias, tag, status, and batch. | Group pages deliberately use metadata-safe citation views even when a richer flat projection is authorized. | Preserve that separation in later publication work. |
| Export | Flat JSON status | Done | `.c2s/exports/c2s-status.json` includes the nested replay indexes and its effective privacy mode. | No configurable field-level projection profiles. | Add profiles only with a schema and no-leak tests. |
| Export | Flat JSONL citations | Done | `.c2s/exports/c2s-citations.jsonl` follows the selected effective privacy mode. | No signed or encrypted export transport. | Keep transport outside the source-clean core. |
| Export | Grouped JSON indexes | Done | `index-by-artifact`, `index-by-handle`, `index-by-tag`, `index-by-status`, and `index-by-batch` are deterministic metadata-safe JSON projections. | No user-defined grouping dimensions. | Add only with deterministic ordering rules. |
| Export | MkDocs grouped navigation | Done | Group pages and non-empty generated navigation exist for artifact, handle, tag, status, and batch indexes. | Site pages intentionally do not render snippets or private links. | Add explicit site fields only under a separately reviewed public contract. |
| Privacy | Publication privacy modes | Done | `metadata_only`, `hash_only`, policy-gated `snippet`, and HTTPS-only policy-gated `private_link` transforms have no-leak and refusal tests. | Older authority events without retained text cannot emit snippets. | Preserve migration behavior when event schemas evolve. |
| Errors | Structured JSON errors | Done | `C2SError`; JSON argparse usage errors; tests. | No public error-code catalog. | Add error catalog to spec. |
| Testing | First-slice unit tests | Done | `tests/test_first_slice.py`, 20 tests. | No committed subprocess integration test module yet. | Add subprocess smoke tests as formal tests when CLI surface grows. |
| Testing | Session gate model | Done | `BUILD_WORKFLOW_CURRENT.md` defines one-session gates G0 through G8 and validation requirements. | Gates are documentation-enforced until CI expands per phase. | Keep each phase prompt aligned with gate acceptance. |
| Testing | CI validation workflow | Partial | `.github/workflows/ci.yml` and `build-docs/internal/CI_VALIDATION.md` validate docs, unit tests, compile checks, CLI help, and smoke behavior from a clean checkout. | Remote GitHub Actions run has not been observed in this branch. | Confirm first remote CI run after push and fix any platform issue. |
| Packaging | Editable install | Done | `pyproject.toml`; `python -m pip install -e .` passed locally. | No CI or release build artifact. | Add CI matrix and release workflow. |
| Docs | Build contract | Done | Internal requirements, workflow, plan, specifications, external narratives, ADRs, and documentation standard are present; live Markdown links validate. | Documents must continue to track implementation maturity. | Require truth-label and cross-reference review in every behavior-changing gate. |

## Release Readiness By Version

| Version | Release Goal | Readiness | Exit Criteria |
|---|---|---:|---|
| v0.3.0 | Local first slice | Partial | Grouping/indexing, privacy transforms, CLI query filters, and docs complete. |
| v0.4.0 | Publishable citation site | Planned | Static-host deployment guide, publication review, and remote CI validation. |
| v0.5.0 | Integration-ready C2S | Planned | Right-click integration examples, stable `lookup-actions`, adapter conformance tests. |
| v0.6.0 | Agent-first automation | Planned | Batch policies, idempotency, full JSON schemas, CI checks, and recovery workflows. |
| v1.0.0 | Public stable release | Planned | Schema freeze, migration rules, threat model, docs, examples, CI, and release artifacts. |

## Known Current Gaps

1. Adapter support is text-first; richer file types are not present.
2. CI workflow exists locally, but no remote run has been observed yet.
3. JSON Schema files exist for current public request/response examples, but
   runtime schema validation is not implemented.
4. No migration command exists because there is only one implementation schema.
5. No editor/browser/document integration package exists yet.

## Immediate Next Build: Adapter Hardening

Implement a conformance harness and diagnostics for the existing text adapters:

1. define adapter protocol fixtures for identity, canonicalization, location,
   observation, comparison, summaries, and privacy;
2. harden UTF-8, missing-file, unsupported, and ambiguous diagnostics;
3. add source-clean conformance tests for filesystem-text and Markdown.
