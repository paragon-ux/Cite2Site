#!/usr/bin/env python3
"""Cite2Site native-messaging host.

Chrome launches this program with its working directory set to the host
installation directory. The target Cite2Site repository is therefore read
from config.json rather than inferred from the process working directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

_MAX_INBOUND_BYTES = 64 * 1024 * 1024
_MAX_OUTBOUND_BYTES = 1024 * 1024


def _set_binary_stdio() -> None:
    """Prevent Windows CRT newline translation from corrupting the protocol."""
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
            {
                "ok": False,
                "error": {
                    "code": "E_EXTENSION_RESPONSE_TOO_LARGE",
                    "message": "Native-host response exceeded Chrome's 1 MiB limit.",
                },
            },
            separators=(",", ":"),
        ).encode("utf-8")

    sys.stdout.buffer.write(struct.pack("@I", len(raw)))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _config_path() -> Path:
    override = os.environ.get("CITE2SITE_NATIVE_CONFIG")
    return Path(override).expanduser().resolve() if override else Path(__file__).with_name("config.json")


def _load_repo_dir() -> Path:
    path = _config_path()
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Native-host config is missing. Re-run c2s install-native-host."
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Native-host config is invalid: {path}") from exc

    repo_value = config.get("repo")
    if not isinstance(repo_value, str) or not repo_value:
        raise RuntimeError("Native-host config does not contain a repository path.")

    repo_dir = Path(repo_value).expanduser().resolve()
    if not (repo_dir / "project.json").is_file():
        raise RuntimeError(
            f"Cite2Site repository is not initialized at {repo_dir}. "
            "Run c2s init, then reinstall the native host."
        )
    return repo_dir


def _run_c2s(repo_dir: Path, arguments: list[str], timeout: int = 30) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "c2s.cli",
        "--repo",
        str(repo_dir),
        *arguments,
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": {
                "code": "E_EXTENSION_TIMEOUT",
                "message": "The Cite2Site command timed out.",
            },
        }
    except OSError as exc:
        return {
            "ok": False,
            "error": {
                "code": "E_EXTENSION_LAUNCH",
                "message": f"Could not launch Cite2Site: {type(exc).__name__}.",
            },
        }

    output = completed.stdout.strip()
    error_output = completed.stderr.strip()
    try:
        parsed = json.loads(output) if output else None
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        return parsed

    return {
        "ok": False,
        "error": {
            "code": "E_EXTENSION_C2S_ERROR",
            "message": error_output or output or f"Cite2Site exited with code {completed.returncode}.",
        },
    }


def _content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _capture_paths(repo_dir: Path, source_url: str, content_hash: str) -> tuple[Path, Path]:
    source_key = hashlib.sha256(
        (source_url + "\0" + content_hash).encode("utf-8")
    ).hexdigest()
    directory = repo_dir / "captured" / "web"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{source_key}.txt", directory / f"{source_key}.json"


def handle_cite_selection(message: dict[str, Any]) -> dict[str, Any]:
    selected_text = message.get("selectedText")
    if not isinstance(selected_text, str) or not selected_text:
        return {
            "ok": False,
            "error": {"code": "E_EXTENSION_EMPTY", "message": "No text was selected."},
        }

    actual_hash = _content_hash(selected_text)
    expected_hash = message.get("contentHash")
    if expected_hash and expected_hash != actual_hash:
        return {
            "ok": False,
            "error": {
                "code": "E_CONTENT_HASH_MISMATCH",
                "message": "The selected-text hash changed before it reached Cite2Site.",
                "details": {"expected": expected_hash, "actual": actual_hash},
            },
        }

    try:
        repo_dir = _load_repo_dir()
    except RuntimeError as exc:
        return {
            "ok": False,
            "error": {"code": "E_EXTENSION_CONFIG", "message": str(exc)},
        }

    source_url = message.get("sourceUrl") or message.get("artifact") or "web-selection"
    source_url = str(source_url)
    title = str(message.get("title") or source_url)

    capture_path, metadata_path = _capture_paths(repo_dir, source_url, actual_hash)
    capture_path.write_text(selected_text, encoding="utf-8", newline="\n")
    metadata_path.write_text(
        json.dumps(
            {
                "source_url": source_url,
                "title": title,
                "content_hash": actual_hash,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    cite_arguments = [
        "cite-selection",
        "--artifact",
        str(capture_path),
        "--start",
        "0",
        "--end",
        str(len(selected_text)),
        "--adapter",
        "filesystem-text",
        "--expected-content-hash",
        actual_hash,
        "--tag",
        "web",
        "--label",
        title[:500],
        "--note",
        source_url[:4000],
        "--actor-kind",
        "machine",
        "--actor-id",
        "chrome-extension",
    ]
    citation_result = _run_c2s(repo_dir, cite_arguments)
    if not citation_result.get("ok"):
        return citation_result

    export_result = _run_c2s(repo_dir, ["export"], timeout=60)
    if not export_result.get("ok"):
        return {
            "ok": False,
            "error": {
                "code": "E_EXTENSION_EXPORT",
                "message": "The citation was recorded, but the site projection could not be refreshed.",
                "details": {"export_error": export_result.get("error")},
            },
            "citation": citation_result,
        }

    return {
        **citation_result,
        "source_url": source_url,
        "capture_path": str(capture_path),
        "site_dir": export_result.get("site_dir"),
    }


def handle_lookup_actions(message: dict[str, Any]) -> dict[str, Any]:
    try:
        repo_dir = _load_repo_dir()
    except RuntimeError as exc:
        return {
            "ok": False,
            "error": {"code": "E_EXTENSION_CONFIG", "message": str(exc)},
        }

    artifact = message.get("artifact")
    start = message.get("start")
    end = message.get("end")
    if not isinstance(artifact, str) or start is None or end is None:
        return {
            "ok": False,
            "error": {
                "code": "E_EXTENSION_INVALID",
                "message": "artifact, start, and end are required.",
            },
        }

    return _run_c2s(
        repo_dir,
        [
            "lookup-actions",
            "--artifact",
            artifact,
            "--start",
            str(start),
            "--end",
            str(end),
        ],
    )


def dispatch(message: dict[str, Any]) -> dict[str, Any]:
    action = message.get("action")
    if action == "cite-selection":
        return handle_cite_selection(message)
    if action == "lookup-actions":
        return handle_lookup_actions(message)
    return {
        "ok": False,
        "error": {
            "code": "E_EXTENSION_UNKNOWN_ACTION",
            "message": f"Unknown action: {action}",
        },
    }


def main() -> None:
    _set_binary_stdio()
    try:
        message = read_message()
        response = (
            dispatch(message)
            if message is not None
            else {
                "ok": False,
                "error": {
                    "code": "E_EXTENSION_EMPTY",
                    "message": "No native message was received.",
                },
            }
        )
    except Exception as exc:
        response = {
            "ok": False,
            "error": {
                "code": "E_EXTENSION_HOST_CRASH",
                "message": f"{type(exc).__name__}: {exc}",
            },
        }
    send_message(response)


if __name__ == "__main__":
    main()
