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

Cite2Site has a complete local v1.0 implementation (G0-G8 clear). The implemented substrate
proves the append-only event model,
source-clean citation creation, batch citation, handle binding, contextual
lookup, replay status, metadata-only export, structured JSON errors, and unit
test baseline.

G1 supplies deterministic replay indexes and a populated derived artifact
cache; G2 supplies index-backed query filters; G3 supplies grouped JSON
exports and MkDocs navigation; G4 supplies enforced, policy-gated privacy
transforms for replay and export projections; G5 supplies recovery and
lifecycle commands; G6 supplies adapter protocol conformance; G7 supplies
integration contracts and examples; G8 supplies migration fixtures, release
checklists, and CI hardening. Richer adapters (block-aware Markdown, PDF,
DOCX) and native editor/browser integrations remain deferred to post-v1 gates.

## Capability Matrix

| Area | Capability | Status | Current Evidence | Gap | Next Action |
|---|---|---:|---|---|---|
| Repository | Initialize dedicated citation repo | Done | `init_repo()` creates `.c2s/project.json`, history files, exports, and site scaffold. | None for first slice. | Add migration handling when schemas change. |
| Repository | Citation history append chain | Done | `append_event()` writes hash-chained JSONL events; `check` validates chains. | No cross-file transaction envelope yet. | Add transaction/event-set validation before multi-file append grows. |
| Repository | Handle binding history | Done | `.c2s/handle-bindings.jsonl`; `set-handle`; replay aliases. | No dedicated handle index export yet. | Add grouped handle index in indexing milestone. |
| Repository | Artifact index | Done | Successful authority mutations and export deterministically refresh `.c2s/artifact-index.jsonl` from replay. | It is a derived cache, not replay authority; read-only replay deliberately does not refresh it. | Retain the cache contract through future migrations. |
| Adapters | Filesystem text adapter | Done | Adapter protocol (`src/c2s/adapter.py`); `FilesystemTextAdapter` conformance tests cover identify, canonicalize, evidence, locate, observe, compare, summarize, and privacy. | Markdown block-aware observation is not yet shipped. | Add block-level locator spec before enabling Markdown-specific observation. |
| Adapters | Markdown adapter | Done | `.md` defaults to `markdown`; `MarkdownAdapter` inherits text semantics and passes the full adapter conformance suite. | No Markdown block-aware summaries. | Add optional block summaries after text behavior is stable. |
| Adapters | Adapter conformance harness | Done | `tests/test_adapter_conformance.py`; shared `_AdapterConformance` mixin; `FilesystemTextConformanceTests`, `MarkdownConformanceTests`, `AdapterNegativeTests` classes; `adapter_diagnostics()` with 6 stable codes. |
| Citation | `cite-selection` | Done | CLI and core create source-clean citation events. | No right-click plugin yet. | Keep CLI stable while integration examples are added. |
| Citation | `cite-batch` all-or-nothing | Done | Tests prove invalid batch appends nothing; request schema exists in `build-docs/architecture/schemas/cite-batch-request.schema.json`. | No runtime schema validator yet. | Add schema validation when public input hardening begins. |
| Citation | `cite-batch` partial mode | Done | Tests prove valid items append and rejected items report. | No policy controls for allowing partial mode. | Add repository policy gate before public release. |
| Citation | Expected content hash | Done | `E_CONTENT_HASH_MISMATCH` protects selected content; `preflight-selection` returns the selected evidence contract without appending history. | No batch preflight command. | Add only if batch review needs a distinct contract. |
| Citation | `citations` query filters | Done | Index-backed artifact, handle/alias, tag, status, and batch filters support deterministic JSON and JSONL output. | Query output intentionally remains metadata-safe in every privacy mode. | Retain metadata-safe query tests through later CLI changes. |
| Handles | Create handle during citation | Done | `--handle`, batch item `handle`, and opt-in `cite-selection --handle-from-first-line`. | First-line parsing is not available in batch requests. | Add only with a batch schema revision. |
| Handles | Rename, alias, retire | Partial | `set-handle` supports actions and replay aliases. | Retire behavior is basic; no CLI query for alias history. | Add handle history export and tests. |
| Context menu | `lookup-actions` | Done | Returns matches, actions, and `requires_picker`. | Integration contract (`build-docs/architecture/INTEGRATION_CONTRACT.md`) and editor mock (`examples/integration/editor_plugin_mock.py`) delivered. | |
| Context menu | Overlap ordering | Partial | Exact match, range size, handle presence, citation ID. | Target ordering requires most recent binding order, not merely handle presence. | Replace handle-presence sort with binding order and add fixture tests. |
| Integration | Integration contract | Done | `build-docs/architecture/INTEGRATION_CONTRACT.md` covers range encoding, overlap picker, action labels, cancellation, error handling, accessibility. | | |
| Integration | Editor plugin mock | Done | `examples/integration/editor_plugin_mock.py` demonstrates lookup → picker → action interaction loop. | | |
| Integration | Thin-client reference | Done | `examples/integration/thin_client.py` is a transport-neutral library wrapping the C2S CLI with action contracts. | | |
| Integration | Integration fixtures | Done | `examples/integration/fixtures/` contains request/response examples for uncited, overlap, cancel, and unavailable actions. | | |
| Replay | Workflow compensation | Done | `accept-current`, `retract`, `restore`, `relocate`, and `note` append deterministic citation events; unchanged state requests are idempotent. | No explicit undo/redo command aliases. | Keep compensating actions as the authoritative recovery model. |
| Replay | Status projection | Done | `resolved`, `changed`, `missing`, `unsupported`, `retracted`, and `adapter_unavailable` paths exist and are tested. | `ambiguous` and `private` need stronger paths. |
| Replay | Citation grouping | Done | Replay indexes, query filters, grouped JSON exports, and MkDocs navigation cover artifact, handle/alias, tag, status, and batch. | Group pages deliberately use metadata-safe citation views even when a richer flat projection is authorized. | Preserve that separation in later publication work. |
| Export | Flat JSON status | Done | `.c2s/exports/c2s-status.json` includes the nested replay indexes and its effective privacy mode. | No configurable field-level projection profiles. | Add profiles only with a schema and no-leak tests. |
| Export | Flat JSONL citations | Done | `.c2s/exports/c2s-citations.jsonl` follows the selected effective privacy mode. | No signed or encrypted export transport. | Keep transport outside the source-clean core. |
| Export | Grouped JSON indexes | Done | `index-by-artifact`, `index-by-handle`, `index-by-tag`, `index-by-status`, and `index-by-batch` are deterministic metadata-safe JSON projections. | No user-defined grouping dimensions. | Add only with deterministic ordering rules. |
| Export | MkDocs grouped navigation | Done | Group pages and non-empty generated navigation exist for artifact, handle, tag, status, and batch indexes. | Site pages intentionally do not render snippets or private links. | Add explicit site fields only under a separately reviewed public contract. |
| Privacy | Publication privacy modes | Done | `metadata_only`, `hash_only`, policy-gated `snippet`, and HTTPS-only policy-gated `private_link` transforms have no-leak and refusal tests. | Older authority events without retained text cannot emit snippets. | Preserve migration behavior when event schemas evolve. |
| Errors | Structured JSON errors | Done | `C2SError`; JSON argparse usage errors; tests. | No public error-code catalog. | Add error catalog to spec. |
| Testing | First-slice unit tests | Done | `tests/test_first_slice.py`, 21 tests. | No committed subprocess integration test module yet. | Add subprocess smoke tests as formal tests when CLI surface grows. |
| Testing | Session gate model | Done | `BUILD_WORKFLOW_CURRENT.md` defines one-session gates G0 through G8 and validation requirements. | Gates are documentation-enforced until CI expands per phase. | Keep each phase prompt aligned with gate acceptance. |
| Testing | CI validation workflow | Done | `.github/workflows/ci.yml` covers unit tests, compile checks, CLI help, smoke flow, docs validation, and source-clean checks from a clean checkout. First remote run observed and passed. | |
| Packaging | Editable install | Done | `pyproject.toml`; `python -m pip install -e .` passed locally. | No CI or release build artifact. | Add CI matrix and release workflow. |
| Docs | Build contract | Done | Internal requirements, workflow, plan, specifications, external narratives, ADRs, and documentation standard are present; live Markdown links validate. | Documents must continue to track implementation maturity. | Require truth-label and cross-reference review in every behavior-changing gate. |
| Release | v1 stabilization (Phase 7) | Done | `V1_STABLE_CONTRACT.md` (38 codes, 7 event types, 15 commands, 6 schema IDs), `USER_GUIDE.md`, `AGENT_GUIDE.md`, `COMPATIBILITY_CORPUS.md`, `SUPPORT_POLICY.md`, release checklist verified, threat/privacy sign-off complete. | Compatibility test corpus fixtures and test_compat.py are specified but not yet implemented. | Build compatibility test suite per corpus spec. |

| Extension | Chrome extension (M0) | Done | `browser-extension/manifest.json`, `background.js`; `src/c2s/_native_host.py`; `c2s install-native-host` writes registry + profile manifests; right-click context-menu cite flow confirmed via manual Chrome test. | | |
| Extension | Popup file drop (M1) | Done | `browser-extension/popup.html`, `popup.js` restore drop-zone, file picker, text viewer, selection tracking, cite/lookup via native host; persistent capture model (`.c2s/captured/files/<hash>/<name>`); manual Chrome gate confirmed. | | |
| Extension | Shared protocol (M2) | Done | `native_host.py` ACTIONS table (10 actions), PROTOCOL_VERSION 1.0, ACTION_LABELS for UI, mutation routing with citation_id enforcement, centralized error normalization; `background.js` sender validation + action-label table; `tools/test_m2_protocol.py` (8 tests). | M3-M8 deferred per sequential milestone rule. | Proceed to M3 after user acceptance. |
| Extension | Contextual picker (M3-M8) | Planned | See `PHASE_07_PT2_POST_v1_CHECKPOINTS.md` milestones 3-8. | Not yet implemented. | Await M2 acceptance then implement in order. |

## Release Readiness By Version

| Version | Release Goal | Readiness | Exit Criteria |
|---|---|---:|---|
| v1.0.0 | G0-G8 complete (protocol v0.3) | Done | Grouping, indexing, privacy transforms, CLI query filters, workflow commands, adapter protocol conformance, integration contracts and examples, migration fixture tests, CI workflow, release checklist. Remote CI run observed and passing. Phase 7 (v1 stabilization) is complete: stable contract, user/agent guides, compatibility corpus, support policy, threat/privacy sign-off delivered. |

## Known Current Gaps

1. Richer file type support beyond text/Markdown is not present (PDF, DOCX, etc.).
2. Runtime schema validation is not implemented, but migration fixture tests cover schema version, corrupt-file, and hash-chain rejection paths.
3. Chrome extension milestones M3-M8 (contextual picker, context-menu actions, mutations in popup, action panel, unsupported-actions guard, regression suite) are deferred per sequential milestone gate rule; see `build-docs/internal/phase_prompts/PHASE_07_PT2_POST_v1_CHECKPOINTS.md`.
   but migration fixture tests (`tests/test_migration_fixtures.py`) cover
   schema version validation, corrupt inputs, hash-chain integrity, and
   source preservation.
4. No editor/browser/document integration package exists yet, but integration
   contract documentation and reference examples are delivered in
   `build-docs/architecture/INTEGRATION_CONTRACT.md` and `examples/integration/`.

## Immediate Next Build: Phase 7 — v1 Stabilization

G0-G8 and Phase 7 v1 stabilization are complete. The v1 stable contract,
user guide, agent guide, compatibility corpus specification, support policy,
release checklist, and threat/privacy checklist are delivered and signed off.
Remaining deferred work:

1. implement `tests/test_compat.py` and `tests/compat_fixtures/` per the
   compatibility corpus specification;
2. add block-aware Markdown, PDF, and DOCX adapters;
3. add browser-extension and document-tool examples;
4. prepare v1.0 release tag.
