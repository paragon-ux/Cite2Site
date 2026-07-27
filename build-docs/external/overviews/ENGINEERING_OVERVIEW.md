# Engineering Overview

Cite2Site is a local Python package with a CLI-first core. Integrations such as
editor menus or browser extensions should call the CLI or library contracts
rather than storing their own authoritative state.

## Authority

Authority lives in `.c2s`:

- `project.json`;
- `citation-history.jsonl`;
- `handle-bindings.jsonl`.

Generated JSON and MkDocs pages are projections.

## Core Commands

- `init`;
- `cite-selection`;
- `cite-batch`;
- `set-handle`;
- `lookup-actions`;
- `status`;
- `export`;
- `check`.

## Current Engineering Gap

The implementation has flat export and status projection. The next engineering
work is grouped indexing:

- populate artifact index;
- build indexes by artifact, handle, tag, status, and batch;
- add query filters;
- generate grouped JSON and MkDocs pages.
