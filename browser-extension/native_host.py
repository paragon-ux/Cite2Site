#!/usr/bin/env python3
"""Cite2Site Native Messaging Host for Chrome Extension.

Reads JSON messages from stdin (Chrome native messaging protocol),
runs ``c2s`` commands, and writes JSON responses to stdout.
Processes one message and exits.
"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path


def read_message() -> dict | None:
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len or len(raw_len) < 4:
        return None
    msg_len = struct.unpack("@I", raw_len)[0]
    raw = sys.stdin.buffer.read(msg_len)
    return json.loads(raw.decode("utf-8"))


def send_message(data: dict) -> None:
    raw = json.dumps(data).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(raw)))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _find_c2s_dir() -> str | None:
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        candidate = parent / ".c2s"
        if candidate.exists():
            return str(candidate)
    return None


def _run_c2s(cmd: list[str]) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"code": "E_EXTENSION_TIMEOUT", "message": "c2s command timed out."}}
    except FileNotFoundError:
        return {"ok": False, "error": {"code": "E_EXTENSION_C2S_NOT_FOUND", "message": "c2s not found on PATH."}}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": {"code": "E_EXTENSION_BAD_JSON", "message": r.stderr or r.stdout}}


def handle_lookup_actions(msg: dict) -> dict:
    c2s_dir = _find_c2s_dir()
    if c2s_dir is None:
        return {"ok": False, "error": {"code": "E_REPO_NOT_FOUND", "message": "No .c2s repository found."}}
    artifact = msg.get("artifact", "")
    start = msg.get("start")
    end = msg.get("end")
    if start is None or end is None:
        return {"ok": False, "error": {"code": "E_EXTENSION_INVALID", "message": "start and end are required."}}
    return _run_c2s(["c2s", "--repo", c2s_dir, "lookup-actions",
                     "--artifact", str(artifact), "--start", str(start), "--end", str(end)])


def handle_cite_selection(msg: dict) -> dict:
    selected_text = msg.get("selectedText", "")
    if not selected_text:
        return {"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "No text selected."}}
    c2s_dir = _find_c2s_dir()
    if c2s_dir is None:
        return {"ok": False, "error": {"code": "E_REPO_NOT_FOUND", "message": "No .c2s repository found."}}
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(selected_text)
        tmp_path = f.name
    try:
        return _run_c2s(["c2s", "--repo", c2s_dir, "cite-selection",
                         "--artifact", tmp_path, "--start", "0",
                         "--end", str(len(selected_text)),
                         "--adapter", "filesystem-text"])
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> None:
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
