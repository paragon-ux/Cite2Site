# Cite2Site v1.0 Stable Contract

**Status:** v1.0 stabilization authority. Defines every stable interface, every
experimental/deferred surface, and the compatibility rules for future releases.

This document is a required Phase 7 deliverable. It is referenced by the v1
gate report, the compatibility test corpus, and the user and agent guides.

---

## 1. Stable Schema Identifiers

| Identifier | Meaning | Frozen |
|---|---|---|
| `c2s.event.v0.3` | Event envelope and citation-created/handle-bound/workflow event schema_version | Yes |
| `c2s.project.v0.3` | Project file schema_version | Yes |
| `c2s.citations.v0.3` | `c2s citations` response schema_version | Yes |
| `c2s.status.v0.3` | `c2s status` response schema_version | Yes |
| `c2s.lookup-actions.v0.3` | `c2s lookup-actions` response schema_version (defined in schema; not yet emitted at runtime) | Yes |

| `c2s.artifact-index.v0.3` | Derived artifact-index cache schema_version (internal) | Yes |

Note: the v0.3 in the schema identifier is the protocol version, not the
Future protocol versions must maintain a migration path from v0.3.

---

## 2. Stable CLI Commands

| Command | Stability | Notes |
|---|---|---|
| `c2s init` | Stable | --force flag |
| `c2s cite-selection` | Stable | --artifact, --start, --end, --adapter, --expected-content-hash, --handle, --label, --tag, --note, --handle-from-first-line |
| `c2s cite-batch` | Stable | --request (JSON file path) |
| `c2s set-handle` | Stable | --citation-id, --handle, --action (bind/rename/alias/retire), --previous-handle |
| `c2s preflight-selection` | Stable | Same flags as cite-selection; read-only |
| `c2s accept-current` | Stable | --citation-id, --expected-content-hash |
| `c2s retract` | Stable | --citation-id |
| `c2s restore` | Stable | --citation-id |
| `c2s relocate` | Stable | --citation-id, --artifact, --start, --end, --adapter, --expected-content-hash |
| `c2s note` | Stable | --citation-id, --note |
| `c2s lookup-actions` | Stable | --artifact, --start, --end, --privacy |
| `c2s status` | Stable | --privacy |
| `c2s citations` | Stable | --artifact, --handle, --tag, --status, --batch, --privacy, --format |
| `c2s export` | Stable | --privacy |
| `c2s check` | Stable | No flags |

All commands above accept the global `--repo REPO` flag.

---

## 3. Stable Event Fields

Every event in `.c2s/citation-history.jsonl` carries:

| Field | Type | Required | Frozen |
|---|---|---|---|
| `schema_version` | `const "c2s.event.v0.3"` | Yes | Yes |
| `event_type` | string | Yes | Yes |
| `event_id` | sha256 hex | Yes | Yes |
| `previous_event_hash` | sha256 hex | Yes | Yes |
| `repository_id` | sha256 hex | Yes | Yes |
| `batch_id` | sha256 hex or null | No | Yes |
| `idempotency_key` | string | No | Yes |
| `created_at` | ISO 8601 string | Yes | Yes |
| `actor.kind` | user/agent/machine | Yes | Yes |
| `actor.id` | string | No | Yes |
| `tool.name` | string | Yes | Yes |
| `tool.version` | string | Yes | Yes |

### citation.created event (additional fields)

| Field | Type | Required | Frozen |
|---|---|---|---|
| `citation_id` | sha256 hex | Yes | Yes |
| `artifact.adapter` | filesystem-text/markdown | Yes | Yes |
| `artifact.uri` | string | Yes | Yes |
| `artifact.artifact_id` | sha256 hex | Yes | Yes |
| `locator.kind` | text-range | Yes | Yes |
| `locator.encoding` | unicode-scalar | Yes | Yes |
| `locator.start` | integer >= 0 | Yes | Yes |
| `locator.end` | integer >= 0 | Yes | Yes |
| `locator.start_line` | integer >= 1 | Yes | Yes |
| `locator.end_line` | integer >= 1 | Yes | Yes |
| `accepted_evidence.kind` | text | Yes | Yes |
| `accepted_evidence.canonicalization` | text-utf8-lf-v1 | Yes | Yes |
| `accepted_evidence.content_hash` | sha256 hex | Yes | Yes |
| `accepted_evidence.line_hashes` | array of sha256 hex | Yes | Yes |
| `accepted_evidence.byte_count` | integer | Yes | Yes |
| `accepted_evidence.line_count` | integer | Yes | Yes |
| `accepted_evidence.text` | string | No | Retained in authority; stripped by privacy |
| `metadata.label` | string or null | No | Yes |
| `metadata.tags` | array of strings | Yes | Yes |
| `metadata.note` | string or null | No | Yes |

### handle.bound event (additional fields)

| Field | Type | Required | Frozen |
|---|---|---|---|
| `citation_id` | sha256 hex | Yes | Yes |
| `handle` | pattern `^[A-Za-z0-9_.:/-]{1,128}$` | Yes | Yes |
| `action` | bind/rename/alias/retire | Yes | Yes |
| `previous_handle` | string or null | No | Yes |
| `policy.preserve_previous_as_alias` | boolean | Yes | Yes |

### Workflow events (citation.accepted, retracted, restored, relocated, noted)

| Field | Type | Required | Frozen |
|---|---|---|---|
| `citation_id` | sha256 hex | Yes | Yes |
| `accepted_evidence` | object | Accept + relocate only | Yes |
| `artifact` | object | Relocate only | Yes |
| `locator` | object | Relocate only | Yes |
| `observed_content_hash` | sha256 hex | Accept only | No |
| `note` | string | Noted only | Yes |

---

## 4. Stable Projection Fields

### Status report

| Field | Type | Frozen |
|---|---|---|
| `ok` | bool | Yes |
| `schema_version` | "c2s.status.v0.3" | Yes |
| `repository_id` | sha256 hex | Yes |
| `privacy_mode` | enum | Yes |
| `citations[]` | array | Yes |
| `indexes.by_artifact` | grouped index | Yes |
| `indexes.by_handle` | grouped index | Yes |
| `indexes.by_tag` | grouped index | Yes |
| `indexes.by_status` | grouped index | Yes |
| `indexes.by_batch` | grouped index | Yes |
| `summary` | object | Yes |

### Citations query response

| Field | Type | Frozen |
|---|---|---|
| `ok` | bool (always true) | Yes |
| `schema_version` | "c2s.citations.v0.3" | Yes |
| `repository_id` | sha256 hex | Yes |
| `privacy_mode` | enum | Yes |
| `filters` | object | Yes |
| `citations[]` | array of citation projections | Yes |

### Lookup-actions response

| Field | Type | Frozen |
|---|---|---|
| `ok` | bool (always true) | Yes |
| `requires_picker` | bool | Yes |
| `actions` | array of strings | Yes |
| `matches[]` | array | Yes |
| `matches[].citation_id` | sha256 hex | Yes |
| `matches[].preferred_handle` | string or null | Yes |
| `matches[].match_kind` | exact/contains/contained_by/overlaps | Yes |
| `matches[].range_summary` | string | Yes |
| `matches[].status` | enum | Yes |
| `matches[].actions` | array of strings | Yes |

### Export indexes

| Index File | Frozen |
|---|---|
| `exports/index-by-artifact.json` | Yes |
| `exports/index-by-handle.json` | Yes |
| `exports/index-by-tag.json` | Yes |
| `exports/index-by-status.json` | Yes |
| `exports/index-by-batch.json` | Yes |

### MkDocs site URL shape

| Path Pattern | Frozen |
|---|---|
| `docs/index.md` | Yes |
| `docs/citations.md` | Yes |
| `docs/artifacts/<key>.md` | Yes |
| `docs/handles/<key>.md` | Yes |
| `docs/tags/<key>.md` | Yes |
| `docs/status/<key>.md` | Yes |
| `docs/batches/<key>.md` | Yes |

Key format: `url_safe_slug` — lowercase alphanumeric + hyphens, no leading/trailing hyphens.

---

## 5. Stable Error Codes

| Code | Category | Frozen |
|---|---|---|
| `E_FILE_NOT_FOUND` | Input | Yes |
| `E_JSON_INVALID` | Input | Yes |
| `E_JSONL_INVALID` | Input | Yes |
| `E_ARTIFACT_MISSING` | Citation | Yes |
| `E_ARTIFACT_OUTSIDE_WORKSPACE` | Citation | Yes |
| `E_ARTIFACT_TEXT_DECODE` | Citation | Yes |
| `E_SELECTION_EMPTY` | Citation | Yes |
| `E_RANGE_INVALID` | Citation | Yes |
| `E_CONTENT_HASH_MISMATCH` | Citation | Yes |
| `E_FIRST_LINE_HANDLE` | Citation | Yes |
| `E_CITATION_NOT_FOUND` | Workflow | Yes |
| `E_CITATION_RETRACTED` | Workflow | Yes |
| `E_HANDLE_INVALID` | Handle | Yes |
| `E_HANDLE_COLLISION` | Handle | Yes |
| `E_HANDLE_ACTION_INVALID` | Handle | Yes |
| `E_HANDLE_MODE_CONFLICT` | Handle | Yes |
| `E_BATCH_EMPTY` | Batch | Yes |
| `E_BATCH_ITEM_INVALID` | Batch | Yes |
| `E_BATCH_MODE` | Batch | Yes |
| `E_NOTE_EMPTY` | Workflow | Yes |
| `E_PRIVACY_MODE` | Privacy | Yes |
| `E_PRIVACY_POLICY` | Privacy | Yes |
| `E_REPO_NOT_INITIALIZED` | Repository | Yes |
| `E_REPO_EXISTS` | Repository | Yes |
| `E_REPO_LOCKED` | Repository | Yes |
| `E_SCHEMA_UNKNOWN` | Schema | Yes |
| `E_SCHEMA_UNSUPPORTED` | Schema | Yes |
| `E_EVENT_CHAIN` | Chain | Yes |
| `E_EVENT_HASH` | Chain | Yes |
| `E_EVENT_ID_MISSING` | Chain | Yes |
| `E_PROJECTION_WRITE` | Export | Yes |
| `E_ARTIFACT_INDEX_CACHE` | Internal | Yes |
| `E_ADAPTER_UNSUPPORTED` | Adapter | Yes |
| `E_ADAPTER_UTF8` | Adapter | Yes |
| `E_ADAPTER_MISSING` | Adapter | Yes |
| `E_ADAPTER_EMPTY_SELECTION` | Adapter | Yes |
| `E_ADAPTER_RANGE_INVALID` | Adapter | Yes |
| `E_ADAPTER_AMBIGUOUS` | Adapter | Yes |

**38 stable C2SError codes.** No error code may be removed or have its meaning
changed without a protocol version bump.

---

## 6. Stable Privacy Modes

| Mode | Behavior | Frozen |
|---|---|---|
| `metadata_only` | Default. Strips `accepted_evidence.text` from all projections. | Yes |
| `hash_only` | Strips `accepted_evidence.text` and `accepted_evidence.line_hashes`. | Yes |
| `snippet` | Includes `accepted_evidence.text` only when `allow_snippet: true` is in project publication policy. | Yes |
| `private_link` | Includes private-link URLs only when `allow_private_link: true` and `private_link_base` is an HTTPS URL in project publication policy. | Yes |

---

## 7. Stable Canonicalization

| Canonicalization | Identifier | Frozen |
|---|---|---|
| Text line-ending normalization | `text-utf8-lf-v1` | Yes |
| Content hash | sha256 of canonicalized text | Yes |
| Line hashes | sha256 of each canonicalized line | Yes |
| Artifact identity | sha256 of `{adapter, uri, artifact_id}` dict | Yes |
| Citation ID | sha256 of `{artifact, locator, accepted_evidence}` dict | Yes |
| Event ID | sha256 of full event dict excluding event_id | Yes |

---

## 8. Stable Status Transitions

| Current Status | Trigger | Result |
|---|---|---|
| (none) | citation.created | resolved |
| resolved | citation.accepted | resolved (idempotent) |
| resolved | citation.retracted | retracted |
| retracted | citation.restored | resolved |
| resolved | citation.relocated | resolved (new evidence) |
| resolved | citation.noted | resolved (annotation added) |
| changed | citation.accepted | resolved (evidence accepted) |
| missing | citation.relocated | resolved (new location) |
| any | replay observation | resolved/changed/missing/unsupported/adapter_unavailable/retracted |

---

## 9. Experimental / Deferred Surfaces

| Surface | Status | Isolation |
|---|---|---|
| Overlap ordering by most-recent binding | Partial | Present ordering (handle presence) is documented; binding-order sort is a future enhancement |
| Block-aware Markdown adapter | Deferred | MarkdownAdapter currently uses text semantics; block-level locators not defined |
| PDF adapter | Deferred | No adapter exists |
| DOCX adapter | Deferred | No adapter exists |
| Browser extension integration | Deferred | Integration contract exists; no package |
| Editor plugin integration | Deferred | Editor mock example exists; no package |
| Runtime schema validation | Deferred | Migration fixture tests cover schema validation |
| `undo`/`redo` command aliases | Deferred | Recovery commands (`retract`/`restore`) provide the authoritative recovery model |
| Citation-level `retire` | Deferred | Handle retire exists; citation retire deferred |
| Signed/encrypted export transport | Deferred | Export is local filesystem only |
| User-defined grouping dimensions | Deferred | Five standard dimensions provided |
| Field-level projection profiles | Deferred | Privacy modes cover the available levels |

**Isolation rule:** experimental/deferred surfaces must not be referenced as
available in status rows, guides, or release notes without explicit
qualification.

---

## 10. Compatible Event Types

| event_type | Status |
|---|---|
| `citation.created` | Stable |
| `handle.bound` | Stable |
| `citation.accepted` | Stable |
| `citation.retracted` | Stable |
| `citation.restored` | Stable |
| `citation.relocated` | Stable |
| `citation.noted` | Stable |

**7 stable event types.**

---

## 11. Semantic Versioning Policy

Cite2Site uses semantic versioning. Given MAJOR.MINOR.PATCH:

- **MAJOR** — bumped when any frozen identifier, error code, event field,
  projection field, command flag, or URL shape is removed or changes meaning
  incompatibly. A major bump must include a migration path.
- **MINOR** — bumped when a new stable interface is added (new command, new
  event type, new flag, new error code) without breaking existing ones.
- **PATCH** — bumped for bug fixes, documentation corrections, and
  non-breaking internal changes that do not alter any stable interface.

Deprecation policy: a stable interface may be deprecated in a MINOR release
with a documented replacement and must remain functional through the next
MAJOR release.

---

## 12. Compatibility Test Corpus

See `build-docs/internal/COMPATIBILITY_CORPUS.md` for the concrete fixture
set and test matrix. The corpus must cover:

1. Every event type against frozen fixtures.
2. Every error code with a trigger fixture.
3. Every privacy mode with deterministic output fixtures.
4. Cross-version schema migration (v0.3 → v0.3 idempotent; unknown version
   refusal).
5. Deterministic export comparison (two runs, same fixture, same output).
6. Source-clean verification (artifact unchanged after citation workflows).
7. Hash-chain integrity (tampered event rejection).
