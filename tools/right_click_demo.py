#!/usr/bin/env python3
"""Right-click context-menu demo — the human interaction path for Cite2Site.

This is the reference implementation of the right-click workflow.  Given a
file and a cursor position (or selection), it looks up what citations exist
at that spot, presents them as a picker, and dispatches the chosen action.

Usage::

    python tools/right_click_demo.py --repo .c2s --artifact notes.md --start 5 --end 5

If the cursor falls inside an existing citation, the tool shows the
available actions (set-handle, note, accept-current, retract, etc.) and
lets you pick one.  If multiple citations overlap, it shows a picker.
If no citation exists, it offers to create one.

This is the human-facing equivalent of ``c2s lookup-actions`` — it
exercises the full lookup→picker→action loop that editor plugins and
browser extensions are expected to implement.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "examples"))

from integration.thin_client import C2SThinClient  # noqa: E402


def pick_from_list(items: list[str], prompt: str = "Choose") -> int | None:
    """Show a numbered menu and return the chosen index or None if cancelled."""
    print(f"\n{prompt}:")
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {item}")
    print(f"  [0] Cancel")
    while True:
        try:
            choice = input("> ").strip()
            if choice == "0" or choice.lower() == "q":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return idx
        except (ValueError, KeyboardInterrupt):
            print("  (type a number or 0 to cancel)")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Right-click context-menu demo — lookup citations at a position and act on them."
    )
    parser.add_argument("--repo", default=".c2s", help="Citation repository path")
    parser.add_argument("--artifact", required=True, help="Artifact file path")
    parser.add_argument("--start", type=int, required=True, help="Cursor position (0-based char offset)")
    parser.add_argument("--end", type=int, required=True, help="End of selection (0-based char offset)")
    args = parser.parse_args()

    # Resolve repo — walk up from artifact if not found at given path
    repo_path = Path(args.repo)
    if not repo_path.exists():
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(f"Error: artifact '{args.artifact}' does not exist")
            return 1
        # Walk up from artifact's directory looking for .c2s
        for parent in [artifact_path.parent] + list(artifact_path.parent.parents):
            candidate = parent / ".c2s"
            if candidate.exists():
                repo_path = candidate
                break
        else:
            print(f"Error: no .c2s repository found at '{args.repo}' or above '{args.artifact}'")
            print("Run 'c2s init' first.")
            return 1

    client = C2SThinClient(repo_path)

    # --- 1. Look up what's at this position ---
    print(f"Looking up citations in {args.artifact} at {args.start}-{args.end}...")
    context = client.lookup_context(args.artifact, args.start, args.end)

    if not context.get("ok"):
        print(f"Error: {context.get('error', {}).get('message', context)}")
        return 1

    matches = context.get("matches", [])
    if not matches:
        # --- Uncited: offer to create a citation ---
        print("\nNo citations found at this position.")
        actions = context.get("actions", [])
        cite_actions = [a for a in actions if a["id"] == "cite"]
        if not cite_actions:
            print("No 'cite' action available.")
            return 0
        choice = input("Create a citation here? [y/N]: ").strip().lower()
        if choice not in ("y", "yes"):
            print("Cancelled.")
            return 0
        handle = input("Handle (optional): ").strip() or None
        label = input("Label (optional): ").strip() or None
        result = client.cite_selection(
            args.artifact, args.start, args.end,
            handle=handle, label=label,
        )
        if result.get("ok"):
            print(f"\n[OK] Citation created: {result.get('citation_id', '?')}")
        else:
            print(f"\n[FAIL] {result.get('error', {}).get('message', result)}")
            return 1
        return 0

    # --- 2. Show matches (picker if multiple) ---
    if context.get("requires_picker"):
        print(f"\n{len(matches)} citations overlap at this position:")
        match_labels = []
        for m in matches:
            status_icon = {"resolved": "✓", "changed": "~", "missing": "✗",
                           "retracted": "⊘", "unsupported": "?"}.get(m["status"], "?")
            label = f"{status_icon} {m.get('preferred_handle') or m['citation_id'][:12]}"
            label += f"  [{m['match_kind']}]  {m['range_summary']}  ({m['status']})"
            match_labels.append(label)
        idx = pick_from_list(match_labels, "Select citation")
        if idx is None:
            print(client.cancel_picker(context))
            return 0
        selected_match = matches[idx]
    else:
        selected_match = matches[0]

    # --- 3. Show actions for selected citation ---
    cid = selected_match["citation_id"]
    handle = selected_match.get("preferred_handle", cid[:12])
    print(f"\nSelected: {handle}  [{selected_match['status']}]  {selected_match['range_summary']}")

    available = [a for a in selected_match.get("actions", []) if a.get("available")]
    if not available:
        print("No actions available for this citation.")
        return 0

    action_labels = [f"{a['label']} ({a['id']})" for a in available]
    idx = pick_from_list(action_labels, "Choose action")
    if idx is None:
        print("Cancelled.")
        return 0

    action = available[idx]
    print(f"\nDispatching: {action['label']} on {handle}...")

    # --- 4. Collect any required inputs ---
    extra_args: list[str] = []
    for inp in action.get("required_inputs", []):
        val = input(f"  {inp}: ").strip()
        if not val:
            print("Cancelled — input required.")
            return 0
        extra_args += [f"--{inp}", val]

    # Build and run the command
    cmd = action.get("command_template", [])
    if not cmd:
        print(f"No command template for action '{action['id']}'")
        return 1

    result = client.run_c2s(cmd + extra_args)
    if result.get("ok"):
        print(f"\n[OK] {action['label']}")
    else:
        print(f"\n[FAIL] {result.get('error', {}).get('message', result)}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
