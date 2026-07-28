# Engineering Overview

**Status:** historical v0.3/v1 narrative pending replacement rewrite.

The active replacement protocol is defined by the refined reconciliation RFC
and archival boundary. This overview is preserved for history only.

Cite2Site is a local Python package with a CLI-first core. Integrations such as
editor menus or browser extensions should call the CLI or library contracts
rather than storing their own authoritative state.

## Current Implementation

The first slice supports text and Markdown selections through `filesystem-text`
and `markdown` adapters, with a formal adapter protocol (`src/c2s/adapter.py`)
and conformance test harness (`tests/test_adapter_conformance.py`). The
implemented commands are `init`, `cite-selection`, `cite-batch`, `set-handle`,
`accept-current`, `retract`, `restore`, `relocate`, `note`,
`preflight-selection`, `lookup-actions`, `citations`, `status`, `export`, and
`check`. Each command uses a structured JSON success or error envelope;
`citations --format jsonl` emits one result object per line.

The current export includes grouped JSON indexes and MkDocs pages by artifact,
handle, tag, status, and batch. `status` supplies deterministic in-memory
indexes and `citations` supplies index-backed JSON and JSONL filters. Complete
privacy transforms are implemented; native editor/browser
integrations remain target work. A design specification is not a claim that
these interfaces are already available.

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
- `accept-current`;
- `retract`;
- `restore`;
- `relocate`;
- `note`;
- `preflight-selection`;
- `lookup-actions`;
- `citations`;
- `status`;
- `export`;
- `check`.

## Next Engineering Gate

The implementation has adapter protocol conformance, indexed status projection,
query filters, grouped export, enforced privacy modes, append-only workflow
commands, and integration contract documentation with reference examples. The
next engineering work is release and migration hardening:

- add migration fixture tests;
- confirm remote CI;
- complete release readiness evidence.

Each gate requires determinism, privacy, and source-clean evidence so that
integration code does not become a hidden authority layer.
