# Cite2Site Protocol Specification v0.3

**Status:** architecture-source protocol contract.

This document defines command-level inputs, outputs, state transitions, and
failure behavior. It is written so an implementation agent can map each section
directly to code and tests.

## Protocol Invariants

1. Every command returns JSON.
2. Every error returns `{"ok": false, "error": ...}`.
3. Mutating commands append events only.
4. Read/projection commands do not append events.
5. Cited artifacts are never modified by C2S.
6. Ambiguous mutations require a concrete `citation_id`.
7. Public export defaults to `metadata_only`.

## Common Success Envelope

Every successful command returns:

```json
{
  "ok": true
}
```

Commands may add fields, but `ok: true` is mandatory.

## Common Error Envelope

```json
{
  "ok": false,
  "error": {
    "code": "E_CODE",
    "message": "stable human-readable message",
    "details": {}
  }
}
```

`code` is stable API surface. `message` may improve for clarity but must not be
the only machine-readable signal.

## Command: `init`

Purpose: create a dedicated citation repository.

Inputs:

- `--repo`, default `.c2s`;
- `--force`, optional, allows replacing project metadata only when explicitly
  requested.

Writes:

- `.c2s/project.json`;
- `.c2s/citation-history.jsonl`;
- `.c2s/handle-bindings.jsonl`;
- `.c2s/artifact-index.jsonl`;
- `.c2s/exports/`;
- `.c2s/site/mkdocs.yml`;
- `.c2s/site/docs/index.md`;
- `.c2s/site/docs/citations.md`.

Success:

```json
{
  "ok": true,
  "repo": "C:/path/.c2s",
  "repository_id": "sha256:..."
}
```

Errors:

- `E_REPO_EXISTS`;
- `E_JSON_INVALID`;
- `E_FILE_NOT_FOUND`;
- `E_USAGE`.

Tests:

- creates every expected path;
- repeated init without `--force` fails;
- no cited artifact is created or modified.

## Command: `cite-selection`

Purpose: create one source-clean citation from an artifact range.

Inputs:

- `--artifact`, required;
- `--adapter`, optional, `filesystem-text` or `markdown`;
- `--start`, required unicode-scalar offset;
- `--end`, required unicode-scalar offset;
- `--expected-content-hash`, optional;
- `--handle`, optional;
- `--label`, optional;
- `--tag`, repeatable;
- `--note`, optional;
- `--actor-kind`, default `user`;
- `--actor-id`, optional.

Validation order:

1. repository initialized;
2. adapter supported;
3. artifact readable;
4. range valid;
5. selection non-empty;
6. expected hash matches when supplied;
7. handle syntax valid when supplied;
8. handle collision policy passes.

Writes:

- one `citation.created` event;
- optional `handle.bound` event with same `batch_id`.

Success:

```json
{
  "ok": true,
  "batch_id": "sha256:...",
  "citation_id": "sha256:...",
  "event_id": "sha256:...",
  "handle_event_id": "sha256:..."
}
```

Errors:

- `E_REPO_NOT_INITIALIZED`;
- `E_ADAPTER_UNSUPPORTED`;
- `E_ARTIFACT_MISSING`;
- `E_ARTIFACT_TEXT_DECODE`;
- `E_RANGE_INVALID`;
- `E_SELECTION_EMPTY`;
- `E_CONTENT_HASH_MISMATCH`;
- `E_HANDLE_INVALID`;
- `E_HANDLE_COLLISION`.

Tests:

- source bytes unchanged;
- event chain valid;
- replay status `resolved`;
- handle appears as preferred handle.

## Command: `cite-batch`

Purpose: create multiple citations in one agent-friendly request.

Inputs:

- `--request`, path to JSON request;
- actor fields.

Default mode: `all_or_nothing`.

Request schema: `schemas/cite-batch-request.schema.json`.

Validation order:

1. request JSON valid;
2. mode valid;
3. items non-empty;
4. each item independently validates as a citation;
5. all handle collisions checked before write;
6. if `all_or_nothing`, any rejection aborts all writes;
7. if `partial`, valid items append and rejected items report.

Success or partial response:

```json
{
  "ok": true,
  "batch_id": "sha256:...",
  "created": [],
  "rejected": []
}
```

In partial mode with rejected items, `ok` is `false` and `created` may be
non-empty.

Tests:

- invalid all-or-nothing batch appends nothing;
- partial mode appends valid items only;
- rejected items include `client_item_id` and code;
- created events share `batch_id`.

## Command: `set-handle`

Purpose: append handle-binding event.

Inputs:

- `--citation-id`;
- `--handle`;
- `--action bind|rename|alias|retire`;
- `--previous-handle`, required by policy for rename;
- actor fields.

Rules:

- citation ID must exist;
- handle syntax must pass;
- handle collision fails unless same citation ID;
- rename preserves previous handle as alias by default;
- retire removes preferred handle but does not erase history.

Tests:

- citation ID unchanged after rename;
- old handle appears in aliases;
- collision with another citation fails.

## Command: `lookup-actions`

Purpose: support contextual right-click menus without making overlays
authoritative.

Inputs:

- `--artifact`;
- `--start`;
- `--end`;
- `--privacy`.

Output schema: `schemas/lookup-actions-response.schema.json`.

Rules:

- no match returns `actions: ["cite"]`;
- one match returns direct match actions;
- multiple matches return `requires_picker: true`;
- ordering: exact match, smallest containing range, most recent handle binding,
  citation ID;
- mutating follow-up commands must name `citation_id`.

Tests:

- no match returns cite action;
- one match returns direct actions;
- overlapping citations are ordered deterministically.

## Command: `citations`

Status: planned.

Purpose: query projected citations and indexes.

Filters:

- `--artifact`;
- `--handle`;
- `--tag`;
- `--status`;
- `--batch`;
- `--format json|jsonl`.

Acceptance:

- filters use replay indexes, not ad hoc scans in each command;
- output order is deterministic;
- no evidence text in metadata-only mode.

## Command: `status`

Purpose: replay current projected citation state.

Output schema: `schemas/status-report.schema.json`.

Rules:

- validates event chains before projection;
- computes statuses from current artifact observations;
- includes flat citations and, after indexing milestone, grouped indexes;
- read-only.

## Command: `export`

Purpose: write JSON and MkDocs projections.

Writes:

- flat JSON status;
- flat JSONL citations;
- grouped JSON indexes;
- MkDocs home, flat citations, and grouped pages.

Rules:

- deterministic order;
- metadata-only default;
- generated files are not authority.

## Command: `check`

Purpose: validate citation repository integrity.

Checks:

- project file exists and parses;
- citation event chain valid;
- handle event chain valid;
- required directories exist;
- schema versions recognized.

Read-only: yes.

## Implementation Checklist Per Command

For every new command or command change:

1. update this protocol spec;
2. update JSON schema if request/response shape changes;
3. add success test;
4. add structured error test;
5. add source-clean test when artifacts are involved;
6. update current status matrix;
7. update workflow docs when user/agent flow changes.
