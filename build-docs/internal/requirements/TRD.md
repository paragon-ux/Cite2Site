# Technical Requirements Document

**Status:** internal technical requirements authority.

## Runtime Requirements

| ID | Requirement | Priority |
|---|---|---:|
| TR-001 | Core implementation uses Python 3.11+. | Must |
| TR-002 | Core has no runtime third-party dependencies unless explicitly approved. | Must |
| TR-003 | Package installs with `python -m pip install -e .`. | Must |
| TR-004 | CLI runs as `python -m c2s`. | Must |
| TR-005 | Tests run with `python -m unittest discover -s tests`. | Must |

## Data Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| TR-101 | Citation repo root is `.c2s` by default. | CLI accepts `--repo`; default is `.c2s`. |
| TR-102 | Citation events live in `citation-history.jsonl`. | Init creates file; mutations append to it. |
| TR-103 | Handle events live in `handle-bindings.jsonl`. | Init creates file; handle mutations append to it. |
| TR-104 | Artifact index lives in `artifact-index.jsonl`. | Init creates file; indexing milestone populates it. |
| TR-105 | Events are hash chained. | `check` validates chain. |
| TR-106 | Event hashes use canonical JSON. | Hash function sorts keys and omits `event_id`. |
| TR-107 | Source artifacts are never mutated. | Tests compare source bytes before and after mutation commands. |

## Command Requirements

| Command | Requirement |
|---|---|
| `init` | Create repository layout and project metadata. |
| `cite-selection` | Append one citation event and optional handle event. |
| `cite-batch` | Validate and append multiple citation events. |
| `set-handle` | Append handle-binding event. |
| `lookup-actions` | Return contextual matches and actions. |
| `citations` | Query projected citations by filters. |
| `status` | Replay projected citation state. |
| `export` | Write JSON and MkDocs projections. |
| `check` | Validate repository integrity. |

## Replay Requirements

Replay must:

1. validate event chains;
2. reduce citation events by citation ID;
3. reduce handle bindings into preferred handles and aliases;
4. observe current artifacts through adapters;
5. compute stable statuses;
6. build grouping indexes;
7. apply privacy policy;
8. return deterministic JSON.

## Indexing Requirements

Indexes required:

- `by_artifact`;
- `by_handle`;
- `by_tag`;
- `by_status`;
- `by_batch`.

Each index entry must include:

- key;
- citation IDs;
- count;
- optional display label;
- deterministic order.

Artifact index entries must include:

- artifact ID;
- adapter;
- URI;
- citation IDs;
- status counts;
- first seen timestamp;
- last seen timestamp.

## Adapter Requirements

Adapter methods:

- identify;
- canonicalize;
- locate;
- observe;
- compare;
- summarize;
- privacy.

Supported first adapters:

- `filesystem-text`;
- `markdown`.

Adapter failure requirements:

- invalid UTF-8 returns `E_ARTIFACT_TEXT_DECODE`;
- missing artifact returns `missing` during replay and `E_ARTIFACT_MISSING`
  during mutation;
- unsupported adapter returns `E_ADAPTER_UNSUPPORTED`;
- ambiguous observation returns `ambiguous` and no mutation without explicit
  target.

## Export Requirements

JSON export files:

- `exports/c2s-status.json`;
- `exports/c2s-citations.jsonl`;
- `exports/index-by-artifact.json`;
- `exports/index-by-handle.json`;
- `exports/index-by-tag.json`;
- `exports/index-by-status.json`;
- `exports/index-by-batch.json`.

MkDocs files:

- `site/mkdocs.yml`;
- `site/docs/index.md`;
- `site/docs/citations.md`;
- grouped pages under artifacts, handles, tags, status, and batches.

Export must be deterministic.

## Privacy Requirements

Default mode: `metadata_only`.

Modes:

- `metadata_only`: no evidence text;
- `hash_only`: hashes allowed, no evidence text;
- `snippet`: snippets allowed only by explicit policy;
- `private_link`: local/private links allowed only by explicit policy.

## Error Requirements

Every CLI error must emit:

```json
{
  "ok": false,
  "error": {
    "code": "E_CODE",
    "message": "human-readable message",
    "details": {}
  }
}
```

Argument errors must also use this shape.

## Testing Requirements

Every feature requires:

- unit tests;
- structured error tests;
- source-clean tests when artifacts are touched;
- deterministic ordering tests for indexes and exports;
- privacy tests for publication output;
- CLI smoke coverage for public commands.

## CI Requirements

CI should run:

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
```

Later CI should also run:

- generated export determinism check;
- MkDocs build check when MkDocs is introduced as a dev dependency;
- package build check;
- schema fixture validation.
