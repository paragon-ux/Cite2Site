#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import replacement
from .core import C2SError

PROTOCOL_VERSION = "replacement.v1"
INTEGRATION_SCHEMA = "c2s.integration.replacement.v1"
_MAX_INBOUND_BYTES = 64 * 1024 * 1024
_MAX_OUTBOUND_BYTES = 1024 * 1024


def _set_binary_stdio() -> None:
    if os.name != "nt":
        return
    import msvcrt

    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def _read_exact(size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = sys.stdin.buffer.read(remaining)
        if not chunk:
            raise EOFError(f"native message ended {remaining} byte(s) early")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_message() -> dict[str, Any] | None:
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None
    if len(raw_len) != 4:
        raise ValueError("native message length prefix is truncated")
    message_length = struct.unpack("@I", raw_len)[0]
    if message_length > _MAX_INBOUND_BYTES:
        raise ValueError(f"native message is too large: {message_length} bytes")
    payload = json.loads(_read_exact(message_length).decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("native message must be a JSON object")
    return payload


def send_message(data: dict[str, Any]) -> None:
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > _MAX_OUTBOUND_BYTES:
        raw = json.dumps(
            {"ok": False, "error": {"code": "E_EXTENSION_RESPONSE_TOO_LARGE", "message": "Native-host response exceeded Chrome's 1 MiB limit."}},
            separators=(",", ":"),
        ).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(raw)))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _config_path() -> Path:
    override = os.environ.get("CITE2SITE_NATIVE_CONFIG")
    return Path(override).expanduser().resolve() if override else Path(__file__).with_name("config.json")


def _load_repo_dir(message: dict[str, Any]) -> Path:
    explicit = message.get("repository")
    if isinstance(explicit, str) and explicit:
        return Path(explicit).expanduser().resolve()
    path = _config_path()
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError("Native-host config is missing. Re-run c2s install-native-host.") from exc
    repo_value = config.get("repo")
    if not isinstance(repo_value, str) or not repo_value:
        raise RuntimeError("Native-host config does not contain a repository path.")
    return Path(repo_value).expanduser().resolve()


def _run_c2s(repo_dir: Path, arguments: list[str], timeout: int = 30) -> dict[str, Any]:
    command = [sys.executable, "-m", "c2s.cli", "--repo", str(repo_dir), *arguments]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"code": "E_EXTENSION_TIMEOUT", "message": "Cite2Site command timed out."}}
    stream = completed.stdout if completed.returncode == 0 else completed.stderr
    try:
        parsed = json.loads(stream)
    except json.JSONDecodeError:
        return {"ok": False, "error": {"code": "E_EXTENSION_NATIVE", "message": "Cite2Site returned invalid JSON.", "details": {"stderr": completed.stderr[-500:]}}}
    return parsed


def dispatch(message: dict[str, Any]) -> dict[str, Any]:
    if message.get("schema_version") != INTEGRATION_SCHEMA:
        return {"ok": False, "error": {"code": "E_EXTENSION_SCHEMA", "message": "replacement integration schema_version is required"}}
    action = message.get("action")
    payload = message.get("payload", {})
    if not isinstance(payload, dict):
        return {"ok": False, "error": {"code": "E_EXTENSION_INVALID", "message": "payload must be an object"}}
    repo = _load_repo_dir(message)
    if action == "citation.create":
        key = message.get("idempotency_key")
        if not isinstance(key, str) or not key:
            return {"ok": False, "error": {"code": "E_EXTENSION_IDEMPOTENCY_REQUIRED", "message": "idempotency_key is required"}}
        try:
            result = replacement.cite_integration_payload(repo, message)
        except C2SError as exc:
            return exc.to_json()
        if result.get("ok"):
            export_result = _run_c2s(repo, ["export"], timeout=60)
            if not export_result.get("ok"):
                return {"ok": False, "error": {"code": "E_EXTENSION_EXPORT", "message": "Mutation succeeded but projection refresh failed.", "details": export_result.get("error")}, "mutation": result}
        return result
    if action == "lookup-actions":
        return _run_c2s(
            repo,
            [
                "lookup-actions",
                "--artifact",
                str(payload.get("artifact", "")),
                "--start",
                str(payload.get("start", "")),
                "--end",
                str(payload.get("end", "")),
            ],
        )
    if action == "status":
        return _run_c2s(repo, ["status"])
    return {"ok": False, "error": {"code": "E_EXTENSION_ACTION_UNSUPPORTED", "message": f"unsupported replacement action: {action}"}}


def main() -> int:
    _set_binary_stdio()
    while True:
        message = read_message()
        if message is None:
            return 0
        try:
            send_message(dispatch(message))
        except Exception as exc:  # Native-host boundary must return structured JSON.
            send_message({"ok": False, "error": {"code": "E_EXTENSION_NATIVE", "message": str(exc)}})


if __name__ == "__main__":
    raise SystemExit(main())
