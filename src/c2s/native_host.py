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

# --- Protocol version ---
PROTOCOL_VERSION = "1.0"

# --- Action dispatch table ---
# Each action maps to: handler, requires_citation_id, requires_artifact
ACTIONS: dict[str, dict[str, Any]] = {
    "cite-selection":       {"handler": "handle_cite_selection",       "requires_citation_id": False, "description": "Cite selected text"},
    "lookup-actions":       {"handler": "handle_lookup_actions",       "requires_citation_id": False, "description": "Look up citations at position"},
    "cite-file-selection":  {"handler": "handle_cite_file_selection",  "requires_citation_id": False, "description": "Cite selection from dropped file"},
    "lookup-file-selection":{"handler": "handle_lookup_file_selection","requires_citation_id": False, "description": "Look up citations in dropped file"},
    "retract":              {"handler": "handle_retract",              "requires_citation_id": True,  "description": "Retract a citation"},
    "restore":              {"handler": "handle_restore",              "requires_citation_id": True,  "description": "Restore a retracted citation"},
    "set-handle":           {"handler": "handle_set_handle",           "requires_citation_id": True,  "description": "Set or rename a citation handle"},
    "note":                 {"handler": "handle_note",                 "requires_citation_id": True,  "description": "Add a note to a citation"},
    "accept-current":       {"handler": "handle_accept_current",       "requires_citation_id": True,  "description": "Accept current evidence"},
    "relocate":             {"handler": "handle_relocate",             "requires_citation_id": True,  "description": "Relocate a citation"},
}

# --- Action label table (for extension UI) ---
ACTION_LABELS: dict[str, str] = {
    "cite":              "Cite with Cite2Site",
    "set_handle":        "Change handle",
    "note":              "Add note",
    "accept_current":    "Accept current evidence",
    "relocate":          "Relocate citation",
    "retract":           "Retract citation",
    "restore":           "Restore citation",
    "open":              "Open citation",
}


def _mutate(repo_dir: Path, action: str, citation_id: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    """Run a mutation command and refresh export afterwards."""
    if not citation_id:
        return {"ok": False, "error": {"code": "E_EXTENSION_MISSING_CITATION_ID", "message": "citation_id is required for mutations."}}
    args = [action, "--citation-id", citation_id]
    if extra_args:
        args.extend(extra_args)
    result = _run_c2s(repo_dir, args)
    if result.get("ok"):
        export_result = _run_c2s(repo_dir, ["export"], timeout=60)
        if not export_result.get("ok"):
            return {
                "ok": False,
                "error": {
                    "code": "E_EXTENSION_EXPORT",
                    "message": "The mutation was recorded, but the site projection could not be refreshed.",
                    "details": {"export_error": export_result.get("error")},
                },
                "mutation": result,
            }
    return result


def handle_retract(message: dict[str, Any]) -> dict[str, Any]:
    return _mutate(_load_repo_dir(), "retract", str(message.get("citation_id", "")))


def handle_restore(message: dict[str, Any]) -> dict[str, Any]:
    return _mutate(_load_repo_dir(), "restore", str(message.get("citation_id", "")))


def handle_set_handle(message: dict[str, Any]) -> dict[str, Any]:
    handle_val = message.get("handle", "")
    if not handle_val:
        return {"ok": False, "error": {"code": "E_EXTENSION_INVALID", "message": "handle is required for set-handle."}}
    return _mutate(_load_repo_dir(), "set-handle", str(message.get("citation_id", "")),
                   ["--handle", str(handle_val), "--action", message.get("handle_action", "bind")])


def handle_note(message: dict[str, Any]) -> dict[str, Any]:
    note_text = message.get("note", "")
    if not note_text:
        return {"ok": False, "error": {"code": "E_EXTENSION_INVALID", "message": "note text is required."}}
    return _mutate(_load_repo_dir(), "note", str(message.get("citation_id", "")),
                   ["--text", str(note_text)])


def handle_accept_current(message: dict[str, Any]) -> dict[str, Any]:
    return _mutate(_load_repo_dir(), "accept-current", str(message.get("citation_id", "")))


def handle_relocate(message: dict[str, Any]) -> dict[str, Any]:
    artifact = message.get("artifact", "")
    start = message.get("start")
    end = message.get("end")
    if not artifact or start is None or end is None:
        return {"ok": False, "error": {"code": "E_EXTENSION_INVALID", "message": "artifact, start, end required for relocate."}}
    return _mutate(_load_repo_dir(), "relocate", str(message.get("citation_id", "")),
                   ["--artifact", str(artifact), "--start", str(start), "--end", str(end)])

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


def _safe_file_name(value: Any) -> str:
    name = str(value or "imported.txt").replace("\\", "/").rsplit("/", 1)[-1]
    return name or "imported.txt"


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


def handle_cite_file_selection(message: dict[str, Any]) -> dict[str, Any]:
    """Persist entire file snapshot, then cite the selection."""
    file_info = message.get("file", {})
    selection = message.get("selection", {})
    file_name = _safe_file_name(file_info.get("name", "imported.txt"))
    file_content = file_info.get("content", "")
    selected_text = selection.get("selectedText", "")
    sel_start = selection.get("start", 0)
    sel_end = selection.get("end", 0)
    content_hash = selection.get("contentHash", "")

    if not file_content:
        return {"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "File content is empty."}}
    if not selected_text:
        return {"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "No text selected."}}

    # Validate hash using existing helper
    actual_hash = _content_hash(selected_text)
    if content_hash and content_hash != actual_hash:
        return {"ok": False, "error": {"code": "E_CONTENT_HASH_MISMATCH", "message": "Selection hash mismatch."}}

    try:
        repo_dir = _load_repo_dir()
    except RuntimeError as exc:
        return {"ok": False, "error": {"code": "E_EXTENSION_CONFIG", "message": str(exc)}}

    repo = Path(repo_dir)
    # Persist full file under .c2s/captured/files/<hash>/<name>
    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
    captured_dir = repo / "captured" / "files" / file_hash
    captured_dir.mkdir(parents=True, exist_ok=True)
    file_path = captured_dir / Path(file_name).name
    file_path.write_text(file_content, encoding="utf-8")
    # Metadata sidecar
    meta = {
        "name": file_name,
        "size": len(file_content.encode("utf-8")),
        "imported_at": message.get("_timestamp", ""),
    }
    (captured_dir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    # Cite the selection from the persisted file
    result = _run_c2s(
        repo_dir,
        [
            "cite-selection", "--artifact", str(file_path),
            "--start", str(sel_start), "--end", str(sel_end),
            "--adapter", "filesystem-text",
        ],
    )

    if result.get("ok"):
        export_result = _run_c2s(repo_dir, ["export"], timeout=60)
        if not export_result.get("ok"):
            return {
                "ok": False,
                "error": {
                    "code": "E_EXTENSION_EXPORT",
                    "message": "The citation was recorded, but the site projection could not be refreshed.",
                    "details": {"export_error": export_result.get("error")},
                },
                "citation": result,
            }
    return result


def handle_lookup_file_selection(message: dict[str, Any]) -> dict[str, Any]:
    """Persist file and run lookup-actions at the given position."""
    file_info = message.get("file", {})
    file_content = file_info.get("content", "")
    if not file_content:
        return {"ok": False, "error": {"code": "E_EXTENSION_EMPTY", "message": "File content is empty."}}
    try:
        repo_dir = _load_repo_dir()
    except RuntimeError as exc:
        return {"ok": False, "error": {"code": "E_EXTENSION_CONFIG", "message": str(exc)}}
    repo = Path(repo_dir)
    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
    captured_dir = repo / "captured" / "files" / file_hash
    captured_dir.mkdir(parents=True, exist_ok=True)
    file_path = captured_dir / _safe_file_name(file_info.get("name", "imported.txt"))
    file_path.write_text(file_content, encoding="utf-8")
    start = message.get("start", 0)
    end = message.get("end", 0)
    return _run_c2s(
        repo_dir,
        ["lookup-actions", "--artifact", str(file_path), "--start", str(start), "--end", str(end)],
    )


def dispatch(message: dict[str, Any]) -> dict[str, Any]:
    action = message.get("action", "")
    action_def = ACTIONS.get(action)

    if action_def is None:
        return {
            "ok": False,
            "protocol_version": PROTOCOL_VERSION,
            "error": {"code": "E_EXTENSION_UNKNOWN_ACTION", "message": f"Unknown action: {action or '(missing)'}"},
        }

    if action_def["requires_citation_id"] and not message.get("citation_id"):
        return {
            "ok": False,
            "protocol_version": PROTOCOL_VERSION,
            "error": {"code": "E_EXTENSION_MISSING_CITATION_ID", "message": f"citation_id is required for action '{action}'."},
        }

    handler_name = action_def["handler"]
    handler = globals().get(handler_name)
    if handler is None:
        return {
            "ok": False,
            "protocol_version": PROTOCOL_VERSION,
            "error": {"code": "E_EXTENSION_INTERNAL", "message": f"Handler {handler_name} not found."},
        }

    try:
        result = handler(message)
    except RuntimeError as exc:
        result = {
            "ok": False,
            "error": {"code": "E_EXTENSION_CONFIG", "message": str(exc)},
        }
    if isinstance(result, dict):
        result.setdefault("protocol_version", PROTOCOL_VERSION)
    return result


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
