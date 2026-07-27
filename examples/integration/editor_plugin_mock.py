"""Editor plugin mock — minimal interaction loop for a text-editor integration.

This is a transport-neutral reference that demonstrates the required
interaction contract: selection lookup → picker display → action execution
→ display refresh.  It delegates all citation logic to the C2S CLI via
the thin-client library (`thin_client.py`) which normalizes action dicts
to the contract shape.  It stores no authoritative overlay state.

Usage (from project root):
    python examples/integration/editor_plugin_mock.py --repo .c2s
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

# Reuse the thin-client wrapper for action-contract normalization.
# This avoids the raw-CLI list[str] vs dict mismatch.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from examples.integration.thin_client import C2SThinClient  # noqa: E402


# ---------------------------------------------------------------------------
# Simulated editor state — in a real plugin this would come from the editor API
# ---------------------------------------------------------------------------


@dataclass
class EditorState:
    """Simulates an editor with an open file and a text selection."""

    artifact_uri: str = "notes.md"
    adapter: str = "markdown"
    selection_start: int = 0
    selection_end: int = 11
    repo: Path = field(default_factory=lambda: Path(".c2s"))


# ---------------------------------------------------------------------------
# Picker display (simulated — in a real plugin this would be a UI widget)
# ---------------------------------------------------------------------------


def display_picker(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Simulate showing an ordered overlap picker and returning the user's choice.

    Actions in each match are already normalized to dicts by C2SThinClient.
    """
    print("\n  Overlapping citations detected — picker required:\n")
    for idx, match in enumerate(matches, 1):
        label = match.get("preferred_handle") or match["citation_id"]
        print(
            f"  [{idx}] {label}  ({match['match_kind']}, {match['range_summary']}, status={match['status']})"
        )
        for action in match.get("actions", []):
            if action.get("available", True):
                print(f"       -> {action['label']}")
            else:
                reason = action.get("unavailable_reason", "unavailable")
                print(f"       -> {action['label']} (unavailable: {reason})")
    print("\n  [0] Cancel")
    choice = input("\n  Select citation (0-{}): ".format(len(matches)))
    try:
        idx = int(choice)
    except ValueError:
        return None
    if idx == 0:
        return None
    if 1 <= idx <= len(matches):
        return matches[idx - 1]
    return None


def display_error(error: dict[str, Any]) -> None:
    """Simulate showing a structured error to the user."""
    print(f"\n  Error [{error.get('code', 'UNKNOWN')}]: {error.get('message', 'no message')}")


# ---------------------------------------------------------------------------
# Interaction loop
# ---------------------------------------------------------------------------


def interaction_loop(state: EditorState) -> None:
    """One cycle: lookup → picker → action → refresh."""

    client = C2SThinClient(state.repo)

    # 1. Lookup actions for the current selection.
    response = client.lookup_context(
        state.artifact_uri, state.selection_start, state.selection_end
    )

    if not response.get("ok"):
        display_error(response.get("error", {}))
        return

    # 2. No match → offer citation.
    top_actions = response.get("actions", [])
    cite_action = next((a for a in top_actions if a.get("id") == "cite"), None)
    if cite_action and cite_action.get("available"):
        print(f"\n  No citation at this location. Ready to cite.")
        return

    matches = response.get("matches", [])

    # 3. Single match → show actions directly.
    if not response.get("requires_picker", False) and len(matches) == 1:
        selected = matches[0]
        label = selected.get("preferred_handle") or selected["citation_id"]
        print(f"\n  One citation: {label} ({selected['match_kind']}, status={selected['status']})")
    else:
        # 4. Multiple matches → require picker before any mutation.
        selected = display_picker(matches)
        if selected is None:
            print("\n  Picker cancelled — no mutation performed.")
            return

    # 5. Show available actions for the selected citation.
    show_citation_actions(client, selected)


def show_citation_actions(client: C2SThinClient, match: dict[str, Any]) -> None:
    """Display available actions for one selected citation."""
    cid = match["citation_id"]
    label = match.get("preferred_handle") or cid
    actions = {action["id"]: action for action in match.get("actions", [])}
    available_labels = [a["label"] for a in actions.values() if a.get("available", True)]

    print(f"\n  Selected: {label}")
    print(f"  Actions: {', '.join(available_labels)}")

    # Demonstrate one mutating action: add a note.
    note_action = actions.get("note")
    if note_action and note_action.get("available", True):
        note_text = input("\n  Add note text (Enter to skip): ").strip()
        if note_text:
            result = client.run_c2s(["note", "--citation-id", cid, "--note", note_text])
            if result.get("ok"):
                print(f"  Note added (event: {result.get('event_id', '?')})")
            else:
                display_error(result.get("error", {}))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Editor plugin mock — Cite2Site integration example.")
    parser.add_argument("--repo", default=".c2s", help="citation repository path")
    parser.add_argument("--artifact", default="notes.md", help="artifact URI to open")
    parser.add_argument("--start", type=int, default=0, help="selection start offset")
    parser.add_argument("--end", type=int, default=11, help="selection end offset")
    args = parser.parse_args(argv)

    state = EditorState(
        artifact_uri=args.artifact,
        selection_start=args.start,
        selection_end=args.end,
        repo=Path(args.repo),
    )

    interaction_loop(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
