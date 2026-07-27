# Cite2Site Protocol Specification v0.3

**Status:** architecture-source protocol contract.

This document defines command-level inputs, outputs, state transitions, and
failure behavior. It is written so an implementation agent can map each section
directly to code and tests.

## Intent, Scope, And Maturity

This is the normative target protocol for v0.3. It deliberately describes the
full contract required for a portable citation repository, including commands
and projections that are not in the first runtime slice. It is not a release
note.

The current runtime implements `init`, `cite-selection`, `cite-batch`,
`set-handle`, `lookup-actions`, `citations`, `status`, `export`, and `check`.
`status` includes deterministic in-memory grouped indexes and enforces the
configured projection privacy mode. The runtime does not yet implement
lifecycle commands or actual right-click integrations. The precise state is maintained
in `../internal/CURRENT_STATUS_MATRIX.md`; a caller must not infer availability
from a target contract alone.

## Authority And Verification

The protocol governs CLI/API behavior. JSON schemas describe stable shapes, but
they do not replace semantic checks such as hash-chain validation, deterministic
ordering, source cleanliness, or collision policy. Every protocol claim must be
backed by a command test, a contract fixture, or a documented future acceptance
gate.

| Concern | Primary authority | Verification |
|---|---|---|
| Current availability | Status matrix | Unit tests and CLI help |
| Command semantics | This protocol | Command success and error tests |
| Record and response shape | Schema index and JSON files | JSON parse and schema-fixture review |
| Architectural rationale | ADRs when available | Decision-record review |

## Protocol Invariants

1. Every command returns JSON.
2. Every error returns `{"ok": false, "error": ...}`.
3. Mutating commands append events only.
4. Read/projection commands do not append events.
5. Cited artifacts are never modified by C2S.
6. Ambiguous mutations require a concrete `citation_id`.
7. Public export defaults to `metadata_only`.

An integration may present these operations through a menu, a script, or an
agent tool. That transport does not acquire authority: it must call the same
explicit command contract and preserve the cited artifact.

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
- `--handle-from-first-line`, opt-in and mutually exclusive with `--handle`;
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

## Commands: Workflow Completion

`preflight-selection` validates a proposed citation without writing history. It
returns the canonical artifact, locator, evidence hash/measurements, calculated
citation ID, and an explicitly selected handle when first-line handle mode is
used.

`accept-current`, `retract`, `restore`, `relocate`, and `note` require a
concrete `--citation-id`. They append compensating citation events; no command
rewrites a creation, acceptance, or handle-binding event. `accept-current`,
`retract`, `restore`, and unchanged `relocate` requests are idempotent when the
requested state already holds.

`relocate` requires an exact artifact/range selection and may include an
expected content hash. `note` rejects empty content. First-line handle mode is
available only when explicitly requested and cites the text after the handle
line; arbitrary text is never interpreted as a handle by default.

Errors include `E_FIRST_LINE_HANDLE`, `E_HANDLE_MODE_CONFLICT`,
`E_CITATION_RETRACTED`, `E_NOTE_EMPTY`, and the existing range, hash, adapter,
and citation-not-found codes.

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

**Current implementation:** the CLI computes contextual matches and actions.
An editor, browser, or document right-click transport is a Target integration,
not a shipped capability.

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

**Maturity:** Implemented in G2.

Purpose: query projected citations and indexes.

Filters:

- `--artifact`;
- `--handle`;
- `--tag`;
- `--status`;
- `--batch`;
- `--format json|jsonl`.

JSON output uses `schemas/citations-response.schema.json`. JSONL output emits
one metadata-safe citation object per line in the same deterministic order,
without a wrapper envelope. Errors remain the common structured JSON envelope
on stderr.

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
- includes flat citations and the implemented in-memory grouped indexes;
- read-only.

## Command: `export`

Purpose: write JSON and MkDocs projections.

Writes:

- flat JSON status and flat JSONL citations;
- grouped JSON indexes by artifact, handle, tag, status, and batch;
- MkDocs home, flat citations, and group pages with generated navigation.

Grouped JSON and MkDocs pages use metadata-safe index and citation views. Flat
status and JSONL projections apply the effective privacy transform before they
are written; a disallowed rich mode fails with `E_PRIVACY_POLICY`.

Rules:

- deterministic order;
- metadata-only default;
- `snippet` and `private_link` require explicit repository policy;
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

## Falsification Rules

A protocol statement is not satisfied merely because a command name exists.
Reject the implementation claim when any of the following is true:

1. a mutating command changes the cited artifact;
2. an error path emits only prose rather than the common error envelope;
3. the same history and artifact state produce different projection ordering;
4. an ambiguous contextual mutation proceeds without a concrete
   `citation_id`;
5. metadata-only output exposes accepted or observed evidence text;
6. a Target capability is described as available in a current-state document.
