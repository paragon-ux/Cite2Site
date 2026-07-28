# Technical Requirements Document

**Status:** internal technical requirements authority, pending replacement rewrite.

**Replacement boundary:** technical requirements that describe the v0.3/v1
two-ledger model, evidence-derived citation identity, direct string handles,
or old projection shapes are historical until rewritten. The active technical
model is completed atomic operations, record-instance citation IDs, stable
groups, group-owned handles, complete rolling tallies, scoped supersession, and
replacement-only reconciliation.

## Requirement Interpretation

This document uses **must** for binding technical requirements. It describes the
v0.3 target architecture while the status matrix reports current delivery.
Where a requirement names a future command or projection, its acceptance column
is a gate obligation, not evidence that the runtime already supplies it.

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
| TR-104 | Artifact index lives in `artifact-index.jsonl` as a derived cache. | Successful authority mutations deterministically refresh it; replay does not read it as authority. |
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
| `citations` | Query projected citations by artifact, handle, tag, status, and batch filters; JSONL emits one metadata-safe result per line. |
| `status` | Replay projected citation state. |
| `export` | Write JSON and MkDocs projections. |
| `check` | Validate repository integrity. |
| `accept-current` | Append accepted-evidence event after review. |
| `retract` | Mark citation as retracted. |
| `restore` | Restore a retracted citation to active state. |
| `relocate` | Update citation locator and artifact after evidence moves. |
| `note` | Append a note to a citation. |
| `preflight-selection` | Return the citation contract without appending history. |

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

Current maturity: flat replay, hash-chain validation, text observation, status
calculation, deterministic in-memory index construction, derived artifact
cache population, index-backed querying, grouped export, and policy-enforced
privacy transforms are implemented. Richer adapters (block-aware Markdown,
PDF, DOCX) remain later-gate requirements.

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

Current maturity: flat status JSON, JSONL citations, grouped JSON indexes, and
grouped MkDocs pages are implemented. Flat projections apply the effective
privacy mode; grouped pages intentionally remain metadata-safe.

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

Mode names alone do not meet this requirement. Each mode must have an explicit
input-to-output rule and a negative test proving forbidden evidence is absent.

Publication policy fields are `allow_snippet`, optional `snippet_max_chars`,
`allow_private_link`, and required `private_link_base` when private links are
enabled. `private_link_base` must be an absolute HTTPS URL without credentials,
query, or fragment. Disallowed or invalid rich modes fail with
`E_PRIVACY_POLICY`.

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

For a safety-critical invariant, include at least one counterexample test that
would fail if the invariant regressed: for example, source bytes changed,
ambiguous mutation accepted, or evidence text emitted in metadata-only output.

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
