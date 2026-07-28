#!/usr/bin/env python3
"""Cite2Site Native Messaging Host for Chrome Extension.

Reads JSON messages from stdin (Chrome native messaging protocol),
runs c2s commands, writes JSON responses to stdout. One message, one exit.
"""
import hashlib, json, struct, subprocess, sys
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
        if candidate.is_dir():
            return str(candidate)
    return None


def _run_c2s(cmd: list[str]) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"code": "E_TIMEOUT", "message": "timed out"}}
    except FileNotFoundError:
        return {"ok": False, "error": {"code": "E_NO_C2S", "message": "c2s not found"}}
    if r.returncode != 0:
        return {"ok": False, "error": {"code": "E_C2S_ERROR", "message": r.stderr.strip() or f"exit {r.returncode}"}}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": {"code": "E_BAD_JSON", "message": r.stderr or r.stdout}}


def handle_cite(msg: dict) -> dict:
    text = msg.get("selectedText", "")
    if not text:
        return {"ok": False, "error": {"code": "E_EMPTY", "message": "No text selected"}}

    c2s_dir = _find_c2s_dir()
    if c2s_dir is None:
        return {"ok": False, "error": {"code": "E_NO_REPO", "message": "No .c2s repo. Run c2s init first."}}

    # Persist capture to .c2s/captured/ so it survives replay
    captured_dir = Path(c2s_dir) / "captured"
    captured_dir.mkdir(parents=True, exist_ok=True)
    capture_path = captured_dir / f"web-{hashlib.sha256(text.encode()).hexdigest()[:8]}.txt"
    capture_path.write_text(text, encoding="utf-8")

    result = _run_c2s(["c2s", "--repo", c2s_dir, "cite-selection",
                       "--artifact", str(capture_path),
                       "--start", "0", "--end", str(len(text)),
                       "--adapter", "filesystem-text"])

    # Regenerate the site so citations.md reflects the new citation
    if result.get("ok"):
        export_result = _run_c2s(["c2s", "--repo", c2s_dir, "export"])
        if not export_result.get("ok"):
            result["export_error"] = export_result.get("error", {}).get("message", "export failed")

    return result


def main() -> None:
    msg = read_message()
    if msg is None:
        send_message({"ok": False, "error": {"code": "E_EMPTY", "message": "No message"}})
        return
    action = msg.get("action", "")
    if action == "cite-selection":
        result = handle_cite(msg)
    else:
        result = {"ok": False, "error": {"code": "E_UNKNOWN", "message": f"Unknown action: {action}"}}
    send_message(result)


if __name__ == "__main__":
    main()
