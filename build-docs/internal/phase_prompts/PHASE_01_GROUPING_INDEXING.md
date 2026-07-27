# Phase 01: Grouping And Indexing

**Status:** G1 grouping/indexing core, G2 grouped query CLI, and G3 grouped
export/site are implemented. G4 privacy and publication is also implemented;
the next active build boundary is Phase 03 workflow completeness.

This prompt is written for an implementation agent. Complete the phase end to
end before moving to adapters, privacy expansion, or integrations.

Before editing, read `AGENTS.md`, `CURRENT_STATUS_MATRIX.md`,
`BUILD_WORKFLOW_CURRENT.md`, `DOCUMENTATION_STANDARD.md`, and the two v0.3
architecture specifications. This phase turns approved Target behavior into
Implemented behavior only when its evidence is complete.

## Goal

Turn flat citation replay/export into navigable grouped citation indexes by
artifact, handle, tag, status, and batch.

## Gate Boundaries

This phase spans three independently accepted gates:

| Gate | Scope | Completion evidence |
|---|---|---|
| G1 | Deterministic in-memory replay indexes and derived artifact-cache population. | Core membership/order/cache tests and status-schema update. |
| G2 | `c2s citations` filters and JSON/JSONL result contract. | CLI success/error/filter tests. |
| G3 | Grouped JSON export and MkDocs group pages. | Deterministic output, link, source-clean, and privacy tests. |

Do not implement a later row merely because it is described below. Complete its
own acceptance loop before moving forward.

## Boundary Of This Phase

This phase must not silently implement lifecycle commands, native right-click
interfaces, semantic matching, or non-text adapters. It may make their future
contracts easier to consume, but its acceptance evidence is limited to indexes,
querying, deterministic export, grouped pages, and metadata-only safety.

## Non-Negotiable Constraints

- Do not modify cited artifacts.
- Do not rewrite existing events.
- Do not make generated indexes authority.
- Keep metadata-only export free of evidence text.
- Keep all outputs deterministic.
- Keep all command errors structured JSON.

## Gate-Specific Source Changes

The requirements below are phase-wide. The gate labels are binding: a later
label is not a requirement of G1.

### `src/c2s/core.py`

### G1: Replay Indexes And Artifact Cache

Add these pure helpers:

- `citation_sort_key(citation) -> tuple`
- `build_indexes(projection) -> dict`
- `index_entry(key, citation_ids, display=None, extra=None) -> dict`
- `populate_artifact_index(repo, projection) -> path`

Update `replay()`:

1. keep the existing flat `citations` list;
2. compute deterministic indexes;
3. include `indexes` in the returned status report;
4. do not write files during replay.

### G3: Grouped Export And Site

Update `export()`:

1. call `replay()`;
2. write existing flat files;
3. write grouped index JSON files;
4. write grouped MkDocs pages;
5. populate `artifact-index.jsonl` or deterministic artifact index projection;
6. return paths for grouped outputs.

### G2: Query Handler

Add `citations(args)` command handler:

- filters: artifact, handle, tag, status, batch;
- output modes: `json`, `jsonl`;
- uses replay indexes;
- returns deterministic results;
- metadata-only behavior applies.

### G2: `src/c2s/cli.py`

Add `citations` subcommand:

```bash
python -m c2s citations
python -m c2s citations --artifact notes.md
python -m c2s citations --handle OPENING-CLAIM
python -m c2s citations --tag overview
python -m c2s citations --status changed
python -m c2s citations --batch sha256:...
python -m c2s citations --format jsonl
```

### Gate-Specific Tests

Add or split tests for:

- G1: status includes `indexes`; indexes contain artifact, handle, alias, tag,
  status, and batch groups; grouped index order is deterministic; artifact
  cache population is deterministic; source file bytes do not change.
- G2: `citations --handle` returns preferred-handle and alias matches;
  artifact, tag, status, and batch filters return only matching citations.
- G3: export writes all grouped JSON files and MkDocs pages; metadata-only
  grouped pages do not include accepted evidence text.

## G3 Required Output Files

JSON:

```text
.c2s/exports/index-by-artifact.json
.c2s/exports/index-by-handle.json
.c2s/exports/index-by-tag.json
.c2s/exports/index-by-status.json
.c2s/exports/index-by-batch.json
```

MkDocs:

```text
.c2s/site/docs/artifacts/index.md
.c2s/site/docs/artifacts/<slug>.md
.c2s/site/docs/handles/index.md
.c2s/site/docs/handles/<slug>.md
.c2s/site/docs/tags/index.md
.c2s/site/docs/tags/<slug>.md
.c2s/site/docs/status/index.md
.c2s/site/docs/status/<slug>.md
.c2s/site/docs/batches/index.md
.c2s/site/docs/batches/<slug>.md
```

## Index Construction Rules

Common entry shape:

```json
{
  "key": "overview",
  "display": "overview",
  "count": 2,
  "citation_ids": ["sha256:..."]
}
```

Ordering:

1. group keys sorted lexically;
2. citation IDs ordered by citation creation order;
3. tie-break by citation ID lexical order.

Group membership:

- `by_artifact`: every citation by `artifact.uri`;
- `by_handle`: preferred handle and every alias;
- `by_tag`: every metadata tag;
- `by_status`: replay status;
- `by_batch`: citation creation `batch_id`.

Empty groups are omitted.

## Slug Rules

Use deterministic filesystem-safe slugs:

1. lowercase;
2. replace non-alphanumeric runs with `-`;
3. trim leading/trailing `-`;
4. if empty, use first 16 hex chars of SHA-256 over the original key;
5. if collision occurs, append `-` plus first 8 hash chars.

## Privacy Rules

In `metadata_only`:

- allowed: citation ID, handle, aliases, tags, artifact URI, status, range
  summary, batch ID, timestamps;
- forbidden: accepted evidence text, observed evidence text, snippets.

Tests must assert the original selected text does not appear in grouped pages.

## Phase Completion Checklist (After G3)

- `python -m unittest discover -s tests` passes.
- `python -m compileall src` passes.
- `python -m c2s --help` shows `citations` after G2.
- CLI smoke creates two citations with tags/handles, exports grouped pages, and
  queries by handle/tag/status.
- `build-docs/internal/CURRENT_STATUS_MATRIX.md` marks each delivered row with
  its G1, G2, or G3 maturity only after that gate's tests prove it.
- `build-docs/internal/requirements/BRD.md`, `DRD.md`, and `TRD.md` retain
  their current/target distinctions and link the delivered behavior to this
  gate.
- Re-run documentation validation after updating generated-output contracts and
  verify every restored ADR/external reference remains live.
