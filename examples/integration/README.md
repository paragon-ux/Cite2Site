# Cite2Site Thin-Client Integration Example

**Maturity:** minimal reproducible G7 integration fixture.

This directory demonstrates the intended right-click integration shape without
creating overlay authority. The example shells out to implemented C2S CLI
commands and stores no citation state outside `.c2s`.

## Contract

- Range encoding is `unicode_scalar_offset`, matching `cite-selection` and
  `lookup-actions` `--start` and `--end`.
- Artifact identity is the CLI artifact URI plus adapter kind.
- Uncited selections prepare a `cite-selection` command.
- Cited regions call `lookup-actions`.
- Overlapping matches require picker selection before mutation.
- Mutating actions always carry a concrete `citation_id`.
- Recovery actions not implemented by the current CLI are rendered as
  unavailable, not enabled.
- Picker cancellation performs no mutation.

## Reference Client

Run from this repository root after initializing the citation repository with
the local source tree:

```powershell
$env:PYTHONPATH='src'
python -m c2s --repo .c2s init
python examples/integration/thin_client.py --repo .c2s lookup --artifact notes.md --start 0 --end 11
```

The example is intentionally transport-neutral. Editors, browsers, and document
tools can render the same contract as native menus, but C2S remains the
authority.

## Accessibility Expectations

- Every icon-only host menu item must have a visible text label or accessible
  name matching the action label.
- Picker rows must be keyboard reachable in the same order returned by C2S.
- Cancelling the picker must return focus to the originating selection.
- Disabled actions must stay visible with an explanation from
  `unavailable_reason`.
