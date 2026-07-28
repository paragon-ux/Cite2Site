#!/usr/bin/env python3
"""Cite2Site Native Messaging Host for Chrome Extension.

Reads JSON messages from stdin (Chrome native messaging protocol),
runs ``c2s`` commands, and writes JSON responses to stdout.

Install this host so the Chrome extension can talk to c2s:
    c2s install-native-host
"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path


def read_message() -> dict | None:
    """Read a single native-messaging JSON message from stdin."""
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len or len(raw_len) < 4:
        return None
    msg_len = struct.unpack("@I", raw_len)[0]
    raw = sys.stdin.buffer.read(msg_len)
    return json.loads(raw.decode("utf-8"))


def send_message(data: dict) -> None:
    """Write a single native-messaging JSON message to stdout."""
    raw = json.dumps(data).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(raw)))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def handle_lookup_actions(msg: dict) -> dict:
    """Run c2s lookup-actions for the given position."""
    c2s_dir = None
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        candidate = parent / ".c2s"
        if candidate.exists():
            c2s_dir = candidate
            break
    if c2s_dir is None:
        return {"ok": False, "error": {"code": "E_REPO_NOT_FOUND", "message": "No .c2s repository found."}}

    artifact = msg.get("artifact", "")
    start = msg.get("start", 0)
    end = msg.get("end", 0)
    r = subprocess.run(
        ["c2s", "--repo", str(c2s_dir), "lookup-actions",
         "--artifact", str(artifact), "--start", str(start), "--end", str(end)],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": {"code": "E_EXTENSION_BAD_JSON", "message": r.stderr or r.stdout}}


def handle_cite_selection(msg: dict) -> dict:
    """Run c2s cite-selection for the given selection."""
    selected_text = msg.get("selectedText", "")
    if not selected_text:
        return {"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "No text selected."}}

    # Find the .c2s repo — walk up from CWD
    repo = Path.cwd()
    c2s_dir = None
    for parent in [repo] + list(repo.parents):
        candidate = parent / ".c2s"
        if candidate.exists():
            c2s_dir = candidate
            break

    if c2s_dir is None:
        return {"ok": False, "error": {"code": "E_REPO_NOT_FOUND", "message": "No .c2s repository found. Run 'c2s init' first."}}

    # Write selected text to a temp file so c2s can canonicalize it
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(selected_text)
        tmp_path = f.name

    try:
        r = subprocess.run(
            [
                "c2s", "--repo", str(c2s_dir),
                "cite-selection",
                "--artifact", tmp_path,
                "--start", "0",
                "--end", str(len(selected_text)),
                "--adapter", "filesystem-text",
            ],
            capture_output=True, text=True, timeout=30,
        )
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"ok": False, "error": {"code": "E_EXTENSION_BAD_JSON", "message": r.stderr or r.stdout}}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> None:
    """Process a single native-messaging message and exit."""
    msg = read_message()
    if msg is None:
        send_message({"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "No message received."}})
        return
    action = msg.get("action", "")
    if action == "cite-selection":
        result = handle_cite_selection(msg)
    elif action == "lookup-actions":
        result = handle_lookup_actions(msg)
    else:
        result = {"ok": False, "error": {"code": "E_EXTENSION_UNKNOWN_ACTION", "message": f"Unknown action: {action}"}}
    send_message(result)


if __name__ == "__main__":
    main()
