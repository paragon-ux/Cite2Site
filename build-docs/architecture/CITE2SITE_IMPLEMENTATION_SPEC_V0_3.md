# Cite2Site Implementation Specification v0.3

**Status:** architecture-source implementation contract.

## Scope

This specification defines the target behavior for the Cite2Site local CLI and
projection engine. It covers authority files, event schemas, adapters, commands,
replay, indexing, publication, errors, and validation.

## Invariants

1. Cited artifacts are not modified by C2S.
2. Mutating operations append events.
3. Existing events are not rewritten.
4. Citation IDs are immutable.
5. Handles are editable aliases.
6. Replay is deterministic for the same histories, artifacts, adapters, and
   policy.
7. Generated exports and MkDocs pages are projections, not authority.
8. Unsupported or ambiguous evidence fails closed.
9. Public export defaults to metadata-only.

## Repository Layout

```text
.c2s/
  project.json
  citation-history.jsonl
  handle-bindings.jsonl
  artifact-index.jsonl
  exports/
    c2s-status.json
    c2s-citations.jsonl
    index-by-artifact.json
    index-by-handle.json
    index-by-tag.json
    index-by-status.json
    index-by-batch.json
  site/
    mkdocs.yml
    docs/
      index.md
      citations.md
      artifacts/
      handles/
      tags/
      status/
      batches/
```

## Project File

`project.json` fields:

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | Yes | Project schema version. |
| `repository_id` | Yes | Stable citation repository ID. |
| `workspace_root` | Yes | Base directory for relative artifact URIs. |
| `publication.privacy_mode` | Yes | Default export privacy mode. |
| `created_at` | Yes | Creation timestamp. |
| `tool` | Yes | Creating tool metadata. |

## Event Envelope

Every event must include:

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | Yes | Event schema version. |
| `event_type` | Yes | Event type string. |
| `event_id` | Yes | Hash of canonical event payload with `event_id` omitted. |
| `previous_event_hash` | Yes | Previous event hash in the same history file. |
| `repository_id` | Yes | Citation repository ID. |
| `batch_id` | When applicable | Groups related events. |
| `idempotency_key` | Optional | Caller-provided duplicate prevention key. |
| `created_at` | Yes | UTC timestamp. |
| `actor` | Yes | User, agent, or machine actor metadata. |
| `tool` | Yes | Tool name and version. |

## Citation Events

### `citation.created`

Creates a citation from accepted evidence.

Required payload:

- `citation_id`;
- `artifact`;
- `locator`;
- `accepted_evidence`;
- `metadata`.

### `citation.accepted`

Accepts current observed evidence as the next accepted evidence.

Required payload:

- `citation_id`;
- `accepted_evidence`;
- review metadata.

### `citation.retracted`

Hides a citation from preferred projections.

Required payload:

- `citation_id`;
- reason.

### `citation.restored`

Restores a retracted citation.

Required payload:

- `citation_id`;
- reason.

### `citation.relocated`

Binds a citation to a new locator after review.

Required payload:

- `citation_id`;
- old locator;
- new locator;
- observed evidence hash.

### `citation.noted`

Adds metadata without changing accepted evidence.

Required payload:

- `citation_id`;
- note or metadata patch.

## Handle Binding Events

Event type: `handle.bound`.

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `citation_id` | Yes | Target immutable citation ID. |
| `handle` | Yes | Handle being bound, renamed, aliased, or retired. |
| `action` | Yes | `bind`, `rename`, `alias`, or `retire`. |
| `previous_handle` | For rename | Handle being replaced. |
| `policy.preserve_previous_as_alias` | Yes | Whether rename preserves old handle as alias. |

Rules:

- Handle collisions fail unless binding to the same citation ID.
- Rename preserves old handle as alias by default.
- Retire removes preferred display but not audit history.

## Artifact Model

Artifact fields:

| Field | Required | Meaning |
|---|---:|---|
| `adapter` | Yes | Adapter kind. |
| `uri` | Yes | Adapter URI. |
| `artifact_id` | Yes | Stable identity derived from adapter and URI/path identity. |

The artifact index should maintain:

- artifact ID;
- adapter;
- URI;
- first seen event;
- last seen event;
- citation count;
- status counts.

## Adapter Contract

Adapters must implement:

| Method | Behavior |
|---|---|
| `identify(input)` | Return artifact identity and URI. |
| `canonicalize(selection)` | Return canonical evidence and hashes. |
| `locate(selection)` | Return locator. |
| `observe(locator)` | Read current artifact content at locator. |
| `compare(accepted, observed)` | Return replay status and deltas. |
| `summarize(locator)` | Return metadata-safe range summary. |
| `privacy(policy)` | Redact or suppress evidence for export mode. |

First supported adapters:

- `filesystem-text`;
- `markdown` using text semantics.

## Commands

All commands must emit JSON on success and error.

### `init`

Creates a dedicated citation repository.

### `cite-selection`

Creates one citation from selected evidence.

Inputs:

- artifact URI;
- adapter;
- start/end range;
- expected content hash;
- handle;
- label;
- tags;
- note.

### `cite-batch`

Creates multiple citations.

Rules:

- default mode: `all_or_nothing`;
- explicit mode: `partial`;
- every item has `client_item_id`;
- rejected items include stable codes;
- created events share `batch_id`.

### `set-handle`

Appends handle-binding event.

Actions:

- `bind`;
- `rename`;
- `alias`;
- `retire`.

### `lookup-actions`

Returns contextual actions for a cursor or selection.

Overlap ordering:

1. exact selection match;
2. smallest containing range;
3. most recent preferred-handle binding;
4. citation ID lexical order.

Mutating follow-up actions must name a concrete `citation_id`.

### `citations`

Planned query command.

Filters:

- `--artifact`;
- `--handle`;
- `--tag`;
- `--status`;
- `--batch`;
- `--format json|jsonl`.

### `status`

Replays citation state.

### `export`

Writes JSON and MkDocs projections.

### `check`

Validates repository integrity.

## Replay Statuses

| Status | Meaning |
|---|---|
| `resolved` | Accepted evidence still matches observation. |
| `changed` | Locator resolves but evidence differs. |
| `missing` | Artifact or locator cannot be found. |
| `ambiguous` | Multiple possible observations require user choice. |
| `adapter_unavailable` | Adapter cannot run. |
| `private` | Evidence details suppressed by policy. |
| `unsupported` | Adapter or locator unsupported. |
| `retracted` | Citation hidden from preferred projections. |

## Grouping And Indexing

Replay must produce flat citations plus indexes:

```json
{
  "citations": [],
  "indexes": {
    "by_artifact": {},
    "by_handle": {},
    "by_tag": {},
    "by_status": {},
    "by_batch": {}
  }
}
```

Index rules:

- every active or retracted citation appears in `by_artifact`;
- preferred handles and aliases appear in `by_handle`;
- every tag appears in `by_tag`;
- every replay status appears in `by_status`;
- every batch ID appears in `by_batch`;
- ordering is deterministic by creation order, then citation ID;
- metadata-only mode does not include evidence text.

## Publication

Export must write:

- flat status JSON;
- flat citations JSONL;
- grouped JSON indexes;
- MkDocs index page;
- MkDocs flat citations page;
- MkDocs group pages.

Static-site publication defaults to `metadata_only`.

## Privacy Modes

| Mode | Behavior |
|---|---|
| `metadata_only` | No evidence text. |
| `hash_only` | Evidence hashes allowed, no evidence text. |
| `snippet` | Short snippets allowed by explicit policy. |
| `private_link` | Local/private links allowed for trusted environments. |

## Error Codes

Required stable errors:

- `E_USAGE`;
- `E_REPO_NOT_INITIALIZED`;
- `E_REPO_EXISTS`;
- `E_REPO_LOCKED`;
- `E_EVENT_CHAIN`;
- `E_EVENT_HASH`;
- `E_JSON_INVALID`;
- `E_JSONL_INVALID`;
- `E_FILE_NOT_FOUND`;
- `E_ARTIFACT_MISSING`;
- `E_ARTIFACT_TEXT_DECODE`;
- `E_ADAPTER_UNSUPPORTED`;
- `E_RANGE_INVALID`;
- `E_SELECTION_EMPTY`;
- `E_CONTENT_HASH_MISMATCH`;
- `E_BATCH_MODE`;
- `E_BATCH_EMPTY`;
- `E_BATCH_ITEM_INVALID`;
- `E_HANDLE_INVALID`;
- `E_HANDLE_COLLISION`;
- `E_HANDLE_ACTION_INVALID`;
- `E_CITATION_NOT_FOUND`;
- `E_PRIVACY_MODE`;
- `E_AMBIGUOUS_CITATION_TARGET`.

## Validation Requirements

Every release must run:

```bash
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
```

Each new command also needs:

- success test;
- structured error test;
- source-clean test when artifacts are involved;
- deterministic output test when projection is generated.
