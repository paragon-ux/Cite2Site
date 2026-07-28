# Integration Contract

**Status:** historical v0.3/v1 integration contract pending replacement rewrite.

This contract describes archived lookup/action shapes. Replacement integrations
must wait for replacement command and message schemas with groups, handle IDs,
operation idempotency, scoped duplicates, and archived-repository rejection.

## Purpose

This document defines the stable contract that editor, browser, document-tool,
and automation integrations must follow when calling Cite2Site. It covers
selection citation, contextual lookup, overlap picking, handle editing, action
availability, cancellation, error handling, and accessibility. An integration
that follows this contract calls C2S for state and actions without storing
authoritative overlay state.

## Authority

The authoritative implementation of this contract is:

- `src/c2s/cli.py` — CLI command surface;
- `src/c2s/core.py` — replay, lookup, and mutation logic;
- `examples/integration/thin_client.py` — reference thin-client implementation;
- `examples/integration/editor_plugin_mock.py` — editor-plugin mock;
- `examples/integration/fixtures/` — request/response contract fixtures.

Generated JSON, exports, and MkDocs pages are projections. The integration
must not treat them as authority and must not persist C2S state outside `.c2s`.

## Selection Citation

An uncited text selection becomes a citation through one command:

```
c2s cite-selection --artifact <uri> --start <offset> --end <offset> [--adapter <kind>]
```

### Range Encoding

Ranges use **unicode-scalar offsets** (not byte offsets, line:column pairs, or
grapheme-cluster indices). The start is inclusive; the end is exclusive.  Line
numbers are derived by counting `\n` characters and reported in
`locator.start_line` / `locator.end_line` for display only.

Integrations that use line:column positioning must convert to scalar offsets
before calling C2S. The reference implementation in `thin_client.py` passes
offsets directly.

### Selection Normalization

The adapter canonicalizes the artifact content (line-ending normalization,
encoding) before computing the evidence hash. Integrations **must not**
pre-normalize the selection before sending it to C2S — canonicalization is the
adapter's responsibility and must remain deterministic.

### Artifact Identity

Artifact identity is a stable hash of `{adapter, uri, path}`. Integrations must
supply:

- `uri` — relative or absolute path to the artifact (C2S normalizes `\` to `/`
  and resolves against the citation workspace root);
- `adapter` — `"filesystem-text"`, `"markdown"`, or another supported adapter.

Absolute URIs outside the workspace root are rejected with
`E_ARTIFACT_OUTSIDE_WORKSPACE`.

## Contextual Lookup

An integration inspects a cursor position or selected range through
`lookup-actions`:

```
c2s lookup-actions --artifact <uri> --start <offset> --end <offset> [--privacy <mode>]
```

### No Match

When no citation overlaps the query range, the response contains
`"actions": ["cite"]`. The integration should offer **"Cite with C2S"** as the
primary action.

### Single Match

When exactly one citation overlaps, the response lists that citation with its
available actions. The integration **may** show actions directly without a
picker.

### Multiple Matches (Overlap Picker)

When two or more citations overlap the query range, the response contains
`"requires_picker": true`. The integration **must** present an ordered picker
before any mutating action can proceed. The picker must:

- show each citation's `preferred_handle` (or `citation_id` when no handle);
- display `range_summary` and `status` for disambiguation;
- order matches by the deterministic overlap sort order.

### Overlap Sort Order

Citations are ordered by:

1. **Match kind** (exact > contains > contained_by > overlaps);
2. **Range size** (smallest range first for `contains` matches);
3. **Handle presence** (citations with a preferred handle sort before those without);
4. **Citation ID** (lexical order as tiebreaker).

This ordering is deterministic for the same histories and artifacts. The
integration must preserve it; re-sorting by last-used, recency, or display name
would make the picker inconsistent with the authoritative match order.

**Note:** The current implementation sorts by handle presence (has handle /
no handle). The target spec (`CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md`) defines
most-recent-binding order. See `CURRENT_STATUS_MATRIX.md` overlap-ordering
row for the gap status.

### Mutation Requires Concrete citation_id

Any mutating action (`set-handle`, `note`, `accept-current`, `relocate`,
`retract`, `restore`) **must** include the selected `citation_id`. The
integration must reject the mutation if the user has not selected a concrete
citation from the picker. C2S will also reject the command if called without
a `--citation-id`, but the integration must enforce this client-side to avoid
a confusing error round-trip.

## Action Labels And Availability

### Implemented Actions

| Action ID | Label | Command | Requires citation_id |
|---|---|---|---|
| `cite` | Cite with C2S | `cite-selection` | No |
| `set_handle` | Rename handle | `set-handle --action rename` | Yes |
| `note` | Add note | `note` | Yes |
| `accept_current` | Accept current evidence | `accept-current` | Yes |
| `relocate` | Relocate citation | `relocate` | Yes |
| `retract` | Retract citation | `retract` | Yes |
| `restore` | Restore citation | `restore` | Yes |

### Host Actions

| Action ID | Label | Implementation |
|---|---|---|
| `open` | Open citation | Host-native: open the artifact at the cited range. |

### Unavailable Actions

| Action ID | Reason |
|---|---|
| `retire` | Citation retirement is not implemented in this runtime. |
| `undo` | Undo is not implemented in this runtime. |
| `redo` | Redo is not implemented in this runtime. |

Integrations must display unavailable actions with their reason rather than
showing them as disabled buttons with no explanation.

## Cancellation

Picker cancellation is read-only. The integration must not modify history,
state, or the cited artifact when the user dismisses the picker. The fixture
`picker-cancelled.json` documents the expected integration-side response shape.

## Error Presentation

C2S returns structured JSON errors with stable codes. Integrations must:

1. Parse the `error.code` field.
2. Display the `error.message` text to the user.
3. Never parse prose, match substrings, or guess the error from unstructured output.
4. Never expose resolved filesystem paths — error details may contain the
   user-supplied `artifact` URI but not the internal resolved path.

Common integration-facing error codes:

| Code | Meaning | Source |
|---|---|---|
| `E_ARTIFACT_MISSING` | The artifact file does not exist. | C2S CLI |
| `E_ADAPTER_UNSUPPORTED` | The requested adapter is not installed or recognized. | C2S CLI |
| `E_ARTIFACT_OUTSIDE_WORKSPACE` | The artifact path is outside the citation workspace. | C2S CLI |
| `E_CITATION_NOT_FOUND` | The citation ID does not exist. | C2S CLI |
| `E_HANDLE_COLLISION` | The handle is already bound to a different citation. | C2S CLI |
| `E_PRIVACY_POLICY` | The requested privacy mode is not authorized. | C2S CLI |
| `E_INTEGRATION_PICKER_REQUIRED` | Overlapping citations require a selected citation ID before mutation. | thin-client |
| `E_INTEGRATION_BAD_JSON` | C2S did not return a JSON envelope. | thin-client |

## Accessibility

Integrations should provide:

- **Keyboard path:** Every action reachable without a pointer device. The picker
  must support arrow-key navigation and Enter to select.
- **Visible text labels:** Every action must have a human-readable label.
  Citation IDs are not displayed as primary labels when a preferred handle exists.
- **Focus behavior:** Opening the picker should not move keyboard focus to an
  unrelated element. Closing the picker should return focus to the originating
  selection or context-menu trigger.
- **Picker ordering:** The picker must preserve the authoritative sort order
  defined above. Screen-reader announcement should include match kind and range
  summary.

## Transport Notes

### Editor Plugin

An editor plugin calls C2S as a subprocess or via the Python library. It sends
the current selection's artifact URI and scalar offsets. The `editor_plugin_mock.py`
example demonstrates the minimal interaction loop: select text → lookup → display
picker → execute action → refresh display.

### Browser Extension

A browser extension cannot call C2S as a subprocess directly. It should:

1. Serialize the selection contract as a JSON request;
2. Send it to a local native-messaging host or a local HTTP endpoint that calls C2S;
3. Receive the structured JSON response;
4. Render actions in the extension popup or context menu.

The extension must not cache citation state across page reloads — it must
re-call `lookup-actions` on every interaction.

### Document Tool

A document tool with a scripting interface (e.g., a PDF viewer with a plugin
API) should expose selection as artifact URI + adapter + scalar offsets. The
tool must not convert offsets to a different encoding without an explicit,
documented transformation. If the tool cannot produce deterministic scalar
offsets, it must document the limitation and the expected drift in replay
status.
