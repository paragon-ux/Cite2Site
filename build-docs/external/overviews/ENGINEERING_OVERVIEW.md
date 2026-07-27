# Engineering Overview

Cite2Site is a local Python package with a CLI-first core. Integrations such as
editor menus or browser extensions should call the CLI or library contracts
rather than storing their own authoritative state.

## Current Implementation

The first slice supports text and Markdown selections through `filesystem-text`
and `markdown` semantics. The implemented commands are `init`,
`cite-selection`, `cite-batch`, `set-handle`, `lookup-actions`, `status`,
`export`, and `check`. Each command uses a structured JSON success or error
envelope.

The current export is deliberately flat. Grouped indexes, `citations` queries,
fully distinct privacy transforms, lifecycle-adjacent commands, and native
editor/browser integrations are target work. A design specification is not a
claim that these interfaces are already available.

## Authority

Authority lives in `.c2s`:

- `project.json`;
- `citation-history.jsonl`;
- `handle-bindings.jsonl`.

Generated JSON and MkDocs pages are projections.

The cited artifact is also not authority for Cite2Site state: it is observed
for replay, never rewritten to carry markers or hidden metadata.

## Core Commands

- `init`;
- `cite-selection`;
- `cite-batch`;
- `set-handle`;
- `lookup-actions`;
- `status`;
- `export`;
- `check`.

## Next Engineering Gate

The implementation has flat export and status projection. The next engineering
work is grouped indexing:

- populate artifact index;
- build indexes by artifact, handle, tag, status, and batch;
- add query filters;
- generate grouped JSON and MkDocs pages.

The gate is accepted only when deterministic index, export, privacy, and
source-clean tests pass. This keeps a useful static site from becoming a
separate state model.
