# Cite2Site Integration Examples

**Maturity:** implemented G7 integration fixtures.

This directory demonstrates the intended right-click integration shape without
creating overlay authority. Every example shells out to implemented C2S CLI
commands and stores no citation state outside `.c2s`.

## Contract

The authoritative integration contract is documented in
`build-docs/architecture/INTEGRATION_CONTRACT.md`.  Key rules:

- Range encoding is `unicode_scalar_offset`, matching `cite-selection` and
  `lookup-actions` `--start` and `--end`.
- Artifact identity is the CLI artifact URI plus adapter kind.
- Uncited selections prepare a `cite-selection` command.
- Cited regions call `lookup-actions`.
- Overlapping matches require picker selection before mutation.
- Mutating actions always carry a concrete `citation_id`.
- Implemented recovery actions map to concrete CLI command templates. Deferred
  actions such as undo and redo are rendered as unavailable, not enabled.
- Picker cancellation performs no mutation.

## Examples

### Thin Client (`thin_client.py`)

A transport-neutral Python library that wraps the C2S CLI. Suitable for
automation, scripting, and as a reference for editor/browser integrators.

```powershell
python examples/integration/thin_client.py --repo .c2s lookup --artifact notes.md --start 0 --end 11
```

### Editor Plugin Mock (`editor_plugin_mock.py`)

A minimal interaction loop simulating an editor plugin: open file, select text,
lookup actions, display picker, execute note action.

```powershell
python examples/integration/editor_plugin_mock.py --repo .c2s --artifact notes.md --start 0 --end 11
```

### Fixtures

`fixtures/` contains JSON request/response contract examples for:

- `lookup-uncited-response.json` — no citation at the query range;
- `lookup-overlap-picker.json` — multiple overlapping citations;
- `selection-citation-request.json` — a prepared citation request;
- `picker-cancelled.json` — cancellation without mutation;
- `unavailable-actions.json` — actions that are deferred or not implemented.

These fixtures are used by `tests/test_integration_thin_client.py` as
contract compatibility checks.

## Accessibility Expectations

- Every icon-only host menu item must have a visible text label or accessible
  name matching the action label.
- Picker rows must be keyboard reachable in the same order returned by C2S.
- Cancelling the picker must return focus to the originating selection.
- Disabled actions must stay visible with an explanation from
  `unavailable_reason`.
