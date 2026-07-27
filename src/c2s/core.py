from __future__ import annotations

import argparse
import copy
import contextlib
import dataclasses
import hashlib
import html
import json
import os
import re
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

SCHEMA_VERSION = "c2s.event.v0.3"
TOOL = {"name": "c2s", "version": "0.3.0"}
EMPTY_HASH = "sha256:" + ("0" * 64)
TEXT_CANON = "text-utf8-lf-v1"
VALID_STATUSES = {
    "resolved",
    "changed",
    "missing",
    "ambiguous",
    "adapter_unavailable",
    "private",
    "unsupported",
    "retracted",
}
PRIVACY_MODES = {"metadata_only", "hash_only", "snippet", "private_link"}


class C2SError(Exception):
    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_json(self) -> dict[str, Any]:
        return {"ok": False, "error": {"code": self.code, "message": self.message, "details": self.details}}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise C2SError("E_FILE_NOT_FOUND", f"file not found: {path}", path=path.name) from exc
    except json.JSONDecodeError as exc:
        raise C2SError("E_JSON_INVALID", f"invalid JSON in {path}", path=path.name, line=exc.lineno) from exc


def dump_json(path: Path, value: Any) -> None:
    write_text_atomically(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_text_atomically(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


def dump_jsonl_atomically(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(temporary, path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise C2SError("E_JSONL_INVALID", f"invalid JSONL in {path}", path=path.name, line=lineno) from exc
    return records


def validate_chain(path: Path) -> str:
    previous = EMPTY_HASH
    for index, event in enumerate(read_jsonl(path), 1):
        validate_schema_version(event.get("schema_version"), SCHEMA_VERSION, path=path.name, record=index)
        if event.get("previous_event_hash") != previous:
            raise C2SError("E_EVENT_CHAIN", "event chain hash mismatch", path=path.name, record=index)
        event_id = event.get("event_id")
        if not isinstance(event_id, str):
            raise C2SError("E_EVENT_ID_MISSING", "event is missing event_id", path=path.name, record=index)
        expected = hash_event(event)
        if event_id != expected:
            raise C2SError("E_EVENT_HASH", "event_id does not match canonical event hash", path=path.name, record=index)
        previous = event_id
    return previous


def validate_schema_version(actual: Any, expected: str, **details: Any) -> None:
    if actual == expected:
        return
    code = "E_SCHEMA_UNSUPPORTED" if isinstance(actual, str) and actual.startswith("c2s.") else "E_SCHEMA_UNKNOWN"
    raise C2SError(code, "authority schema version is not supported", expected=expected, actual=actual, **details)


def hash_event(event: dict[str, Any]) -> str:
    payload = dict(event)
    payload.pop("event_id", None)
    return sha256_json(payload)


@dataclasses.dataclass(frozen=True)
class Repo:
    root: Path

    @property
    def project_file(self) -> Path:
        return self.root / "project.json"

    @property
    def citation_history(self) -> Path:
        return self.root / "citation-history.jsonl"

    @property
    def handle_bindings(self) -> Path:
        return self.root / "handle-bindings.jsonl"

    @property
    def artifact_index(self) -> Path:
        return self.root / "artifact-index.jsonl"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def site_dir(self) -> Path:
        return self.root / "site"

    @property
    def lock_file(self) -> Path:
        return self.root / ".write.lock"

    @property
    def project(self) -> dict[str, Any]:
        if not self.project_file.exists():
            raise C2SError("E_REPO_NOT_INITIALIZED", "Cite2Site repository is not initialized", repo=repo.root.name)
        project = load_json(self.project_file)
        validate_schema_version(project.get("schema_version") if isinstance(project, dict) else None, "c2s.project.v0.3", path=self.project_file.name)
        return project

    @property
    def repository_id(self) -> str:
        return str(self.project["repository_id"])

    @property
    def workspace_root(self) -> Path:
        return Path(self.project.get("workspace_root", str(self.root.parent))).resolve()


def repo_from_arg(repo: str | Path = ".c2s") -> Repo:
    return Repo(Path(repo).resolve())


def init_repo(repo: Repo, force: bool = False) -> dict[str, Any]:
    if repo.project_file.exists() and not force:
        raise C2SError("E_REPO_EXISTS", "Cite2Site repository already exists", repo=repo.root.name)
    repo.root.mkdir(parents=True, exist_ok=True)
    repo.exports_dir.mkdir(parents=True, exist_ok=True)
    (repo.site_dir / "docs").mkdir(parents=True, exist_ok=True)
    repository_id = sha256_json({"kind": "c2s.repository", "path": str(repo.root), "nonce": str(uuid.uuid4())})
    dump_json(
        repo.project_file,
        {
            "schema_version": "c2s.project.v0.3",
            "repository_id": repository_id,
            "workspace_root": str(repo.root.parent),
            "publication": {"privacy_mode": "metadata_only", "allow_snippet": False, "allow_private_link": False},
            "created_at": utc_now(),
            "tool": TOOL,
        },
    )
    for path in [repo.citation_history, repo.handle_bindings, repo.artifact_index]:
        path.touch(exist_ok=True)
    write_default_mkdocs(repo)
    write_site_docs(repo, {"citations": [], "summary": summarize_status([])})
    return {"ok": True, "repo": str(repo.root), "repository_id": repository_id}


@contextlib.contextmanager
def repo_lock(repo: Repo):
    repo.root.mkdir(parents=True, exist_ok=True)
    fd: int | None = None
    for _ in range(50):
        try:
            fd = os.open(str(repo.lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            break
        except FileExistsError:
            time.sleep(0.05)
    if fd is None:
        raise C2SError("E_REPO_LOCKED", "could not acquire citation repository lock", repo=repo.root.name)
    try:
        yield
    finally:
        os.close(fd)
        with contextlib.suppress(FileNotFoundError):
            repo.lock_file.unlink()


def append_event(repo: Repo, path: Path, event: dict[str, Any]) -> dict[str, Any]:
    previous = validate_chain(path)
    event = dict(event)
    event.setdefault("schema_version", SCHEMA_VERSION)
    event.setdefault("previous_event_hash", previous)
    event.setdefault("repository_id", repo.repository_id)
    event.setdefault("created_at", utc_now())
    event.setdefault("actor", {"kind": "user"})
    event.setdefault("tool", TOOL)
    event["event_id"] = hash_event(event)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return event


def adapter_for_uri(uri: str, requested: str | None = None) -> str:
    # Late import to avoid circular dependency: adapter.py imports from core.
    from . import adapter as _adapter

    return _adapter.adapter_for_uri(uri, requested)


def normalize_uri(uri: str) -> str:
    return uri.replace("\\", "/")


def resolve_artifact_path(repo: Repo, uri: str) -> Path:
    path = Path(uri)
    workspace = repo.workspace_root.resolve()
    resolved = path if path.is_absolute() else (workspace / path)
    resolved = resolved.resolve()
    try:
        resolved.relative_to(workspace)
    except ValueError:
        raise C2SError(
            "E_ARTIFACT_OUTSIDE_WORKSPACE",
            "artifact path is outside the citation workspace",
            artifact=uri,
            workspace=str(workspace),
        )
    return resolved


def read_text_artifact(repo: Repo, uri: str) -> str:
    path = resolve_artifact_path(repo, uri)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise C2SError("E_ARTIFACT_MISSING", "artifact file not found", artifact=uri) from exc
    except UnicodeDecodeError as exc:
        raise C2SError("E_ARTIFACT_TEXT_DECODE", "artifact is not valid UTF-8 text", artifact=uri) from exc


def canonical_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def line_hashes(text: str) -> list[str]:
    if text == "":
        return []
    return [sha256_bytes((line + "\n").encode("utf-8")) for line in text.split("\n")]


def evidence_for_text(text: str) -> dict[str, Any]:
    canon = canonical_text(text)
    return {
        "kind": "text",
        "canonicalization": TEXT_CANON,
        "content_hash": sha256_bytes(canon.encode("utf-8")),
        "text": canon,
        "line_hashes": line_hashes(canon),
        "byte_count": len(canon.encode("utf-8")),
        "line_count": 0 if canon == "" else len(canon.split("\n")),
    }


def line_number_at(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def make_locator(text: str, start: int, end: int) -> dict[str, Any]:
    if start < 0 or end < start or end > len(text):
        raise C2SError("E_RANGE_INVALID", "selection range is invalid", start=start, end=end, length=len(text))
    return {
        "kind": "text-range",
        "encoding": "unicode-scalar",
        "start": start,
        "end": end,
        "start_line": line_number_at(text, start),
        "end_line": line_number_at(text, end),
    }


def artifact_identity(repo: Repo, uri: str, adapter: str) -> dict[str, Any]:
    path = resolve_artifact_path(repo, uri)
    identity = {"adapter": adapter, "uri": normalize_uri(uri), "path": str(path)}
    return {"adapter": adapter, "uri": normalize_uri(uri), "artifact_id": sha256_json(identity)}


def citation_id_for(artifact: dict[str, Any], locator: dict[str, Any], evidence: dict[str, Any]) -> str:
    return sha256_json({"kind": "c2s.citation", "artifact": artifact, "locator": locator, "accepted_evidence_hash": evidence["content_hash"]})


def batch_id_for(items: list[dict[str, Any]]) -> str:
    return sha256_json({"kind": "c2s.batch", "items": items, "nonce": str(uuid.uuid4())})


def validate_expected_hash(expected: str | None, actual: str, client_item_id: str | None = None) -> None:
    if expected and expected != actual:
        raise C2SError("E_CONTENT_HASH_MISMATCH", "expected content hash does not match selected evidence", expected=expected, actual=actual, client_item_id=client_item_id)


def prepare_citation(
    repo: Repo,
    uri: str,
    start: int,
    end: int,
    adapter: str | None = None,
    expected_content_hash: str | None = None,
    label: str | None = None,
    tags: list[str] | None = None,
    note: str | None = None,
    client_item_id: str | None = None,
) -> dict[str, Any]:
    adapter_name = adapter_for_uri(uri, adapter)
    source = canonical_text(read_text_artifact(repo, uri))
    locator = make_locator(source, start, end)
    selected = source[start:end]
    if selected == "":
        raise C2SError("E_SELECTION_EMPTY", "selection is empty", client_item_id=client_item_id)
    evidence = evidence_for_text(selected)
    validate_expected_hash(expected_content_hash, evidence["content_hash"], client_item_id)
    artifact = artifact_identity(repo, uri, adapter_name)
    citation_id = citation_id_for(artifact, locator, evidence)
    return {
        "client_item_id": client_item_id,
        "citation_id": citation_id,
        "artifact": artifact,
        "locator": locator,
        "accepted_evidence": evidence,
        "metadata": {"label": label, "tags": tags or [], "note": note},
    }


def prepare_selection_from_args(repo: Repo, args: argparse.Namespace) -> tuple[dict[str, Any], str | None]:
    prepared = prepare_citation(
        repo,
        args.artifact,
        args.start,
        args.end,
        adapter=getattr(args, "adapter", None),
        expected_content_hash=getattr(args, "expected_content_hash", None),
        label=getattr(args, "label", None),
        tags=getattr(args, "tag", []),
        note=getattr(args, "note", None),
    )
    if not getattr(args, "handle_from_first_line", False):
        return prepared, getattr(args, "handle", None)
    if getattr(args, "handle", None):
        raise C2SError("E_HANDLE_MODE_CONFLICT", "--handle and --handle-from-first-line cannot be used together")
    selected = prepared["accepted_evidence"]["text"]
    first_line, separator, remainder = selected.partition("\n")
    handle = first_line.strip()
    if not separator or not remainder:
        raise C2SError("E_FIRST_LINE_HANDLE", "first-line handle mode requires a handle line followed by cited evidence")
    if not valid_handle(handle):
        raise C2SError("E_HANDLE_INVALID", "first-line handle is invalid", handle=handle)
    cited_start = int(args.start) + len(first_line) + len(separator)
    prepared = prepare_citation(
        repo,
        args.artifact,
        cited_start,
        args.end,
        adapter=getattr(args, "adapter", None),
        expected_content_hash=getattr(args, "expected_content_hash", None),
        label=getattr(args, "label", None),
        tags=getattr(args, "tag", []),
        note=getattr(args, "note", None),
    )
    return prepared, handle


def citation_event(prepared: dict[str, Any], batch_id: str, actor: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "event_type": "citation.created",
        "batch_id": batch_id,
        "citation_id": prepared["citation_id"],
        "artifact": prepared["artifact"],
        "locator": prepared["locator"],
        "accepted_evidence": prepared["accepted_evidence"],
        "metadata": prepared["metadata"],
    }
    if actor:
        event["actor"] = actor
    return event


def citation_update_event(event_type: str, citation_id: str, actor: dict[str, Any] | None = None, **payload: Any) -> dict[str, Any]:
    event = {"event_type": event_type, "citation_id": citation_id, **payload}
    if actor:
        event["actor"] = actor
    return event


def valid_handle(handle: str) -> bool:
    return bool(handle) and len(handle) <= 128 and all(ch.isalnum() or ch in "-_./:" for ch in handle)


def handle_event(
    citation_id: str,
    handle: str,
    action: str = "bind",
    previous_handle: str | None = None,
    batch_id: str | None = None,
    actor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action not in {"bind", "rename", "alias", "retire"}:
        raise C2SError("E_HANDLE_ACTION_INVALID", "handle action is invalid", action=action)
    if not valid_handle(handle):
        raise C2SError("E_HANDLE_INVALID", "handle contains unsupported characters", handle=handle)
    event = {
        "event_type": "handle.bound",
        "batch_id": batch_id or batch_id_for([{"citation_id": citation_id, "handle": handle, "action": action}]),
        "citation_id": citation_id,
        "handle": handle,
        "action": action,
        "previous_handle": previous_handle,
        "policy": {"preserve_previous_as_alias": True},
    }
    if actor:
        event["actor"] = actor
    return event


def read_events(repo: Repo) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validate_chain(repo.citation_history)
    validate_chain(repo.handle_bindings)
    return read_jsonl(repo.citation_history), read_jsonl(repo.handle_bindings)


def replay_handles(handle_events: list[dict[str, Any]]) -> dict[str, Any]:
    preferred_by_citation: dict[str, str] = {}
    aliases_by_citation: dict[str, set[str]] = {}
    handle_to_citation: dict[str, str] = {}
    binding_order: dict[str, int] = {}
    for idx, event in enumerate(handle_events):
        cid = event.get("citation_id")
        handle = event.get("handle")
        action = event.get("action")
        if not isinstance(cid, str) or not isinstance(handle, str):
            continue
        aliases_by_citation.setdefault(cid, set())
        if action == "retire":
            if preferred_by_citation.get(cid) == handle:
                preferred_by_citation.pop(cid, None)
            handle_to_citation.pop(handle, None)
            aliases_by_citation[cid].discard(handle)
            binding_order[handle] = idx
            continue
        previous = event.get("previous_handle")
        if action == "rename" and isinstance(previous, str) and event.get("policy", {}).get("preserve_previous_as_alias", True):
            aliases_by_citation[cid].add(previous)
            handle_to_citation[previous] = cid
        preferred_by_citation[cid] = handle
        aliases_by_citation[cid].add(handle)
        handle_to_citation[handle] = cid
        binding_order[handle] = idx
    return {"preferred_by_citation": preferred_by_citation, "aliases_by_citation": aliases_by_citation, "handle_to_citation": handle_to_citation, "binding_order": binding_order}


def publication_policy(repo: Repo) -> dict[str, Any]:
    policy = repo.project.get("publication", {})
    return policy if isinstance(policy, dict) else {}


def validated_private_link_base(policy: dict[str, Any]) -> str:
    """Return the normalized, externally safe base for private-link output."""
    base = policy.get("private_link_base")
    if not isinstance(base, str) or not base:
        raise C2SError("E_PRIVACY_POLICY", "private-link projection is not authorized", privacy_mode="private_link")
    parsed = urlsplit(base)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise C2SError(
            "E_PRIVACY_POLICY",
            "private_link_base must be an absolute HTTPS URL without credentials, query, or fragment",
            privacy_mode="private_link",
        )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def effective_privacy_mode(repo: Repo, requested: str | None) -> tuple[str, dict[str, Any]]:
    policy = publication_policy(repo)
    mode = requested or policy.get("privacy_mode", "metadata_only")
    if mode not in PRIVACY_MODES:
        raise C2SError("E_PRIVACY_MODE", "privacy mode is invalid", privacy_mode=mode)
    if mode == "snippet" and not policy.get("allow_snippet", False):
        raise C2SError("E_PRIVACY_POLICY", "snippet projection is not authorized", privacy_mode=mode)
    if mode == "private_link":
        if not policy.get("allow_private_link", False):
            raise C2SError("E_PRIVACY_POLICY", "private-link projection is not authorized", privacy_mode=mode)
        validated_private_link_base(policy)
    return mode, policy


def replay(repo: Repo, privacy_mode: str | None = None) -> dict[str, Any]:
    privacy_mode, policy = effective_privacy_mode(repo, privacy_mode)
    citation_events, handle_events = read_events(repo)
    citations: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for event in citation_events:
        cid = event.get("citation_id")
        if not isinstance(cid, str):
            continue
        if event.get("event_type") == "citation.created":
            if cid not in citations:
                order.append(cid)
            citations[cid] = {
                "citation_id": cid,
                "state": "active",
                "artifact": event["artifact"],
                "locator": event["locator"],
                "accepted_evidence": event["accepted_evidence"],
                "metadata": event.get("metadata", {}),
                "batch_id": event.get("batch_id"),
                "created_at": event.get("created_at"),
                "created_event_id": event.get("event_id"),
            }
        elif event.get("event_type") == "citation.accepted" and cid in citations:
            citations[cid]["accepted_evidence"] = event["accepted_evidence"]
        elif event.get("event_type") == "citation.relocated" and cid in citations:
            citations[cid]["locator"] = event["locator"]
            citations[cid]["artifact"] = event.get("artifact", citations[cid]["artifact"])
        elif event.get("event_type") == "citation.retracted" and cid in citations:
            citations[cid]["state"] = "retracted"
        elif event.get("event_type") == "citation.restored" and cid in citations:
            citations[cid]["state"] = "active"
        elif event.get("event_type") == "citation.noted" and cid in citations:
            citations[cid].setdefault("metadata", {}).setdefault("notes", []).append(
                {"text": event["note"], "event_id": event.get("event_id"), "created_at": event.get("created_at")}
            )

    handles = replay_handles(handle_events)
    for cid, citation in citations.items():
        citation["preferred_handle"] = handles["preferred_by_citation"].get(cid)
        citation["aliases"] = sorted(handles["aliases_by_citation"].get(cid, set()))
        citation["status"] = observe_status(repo, citation)
        apply_privacy(citation, privacy_mode, policy)

    projected_citations = [citations[cid] for cid in order]
    for creation_order, citation in enumerate(projected_citations):
        citation["_creation_order"] = creation_order
    projection = {
        "ok": True,
        "schema_version": "c2s.status.v0.3",
        "repository_id": repo.repository_id,
        "privacy_mode": privacy_mode,
        "citations": projected_citations,
        "summary": summarize_status(citations.values()),
    }
    projection["indexes"] = build_indexes(projection)
    for citation in projected_citations:
        citation.pop("_creation_order", None)
    return projection


def citation_sort_key(citation: dict[str, Any]) -> tuple[int, str]:
    creation_order = citation.get("_creation_order", 0)
    return (creation_order if isinstance(creation_order, int) else 0, str(citation["citation_id"]))


def index_entry(
    key: str,
    citation_ids: list[str],
    display: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {"key": key, "count": len(citation_ids), "citation_ids": citation_ids}
    if display is not None:
        entry["display"] = display
    if extra:
        entry.update(extra)
    return entry


def build_indexes(projection: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    citations = sorted(projection.get("citations", []), key=citation_sort_key)
    groups: dict[str, dict[str, list[dict[str, Any]]]] = {
        "by_artifact": {},
        "by_handle": {},
        "by_tag": {},
        "by_status": {},
        "by_batch": {},
    }
    for citation in citations:
        artifact = citation.get("artifact", {})
        artifact_uri = artifact.get("uri")
        if isinstance(artifact_uri, str):
            groups["by_artifact"].setdefault(artifact_uri, []).append(citation)
        handles = {handle for handle in [citation.get("preferred_handle"), *citation.get("aliases", [])] if isinstance(handle, str)}
        for handle in sorted(handles):
            groups["by_handle"].setdefault(handle, []).append(citation)
        for tag in sorted({tag for tag in citation.get("metadata", {}).get("tags", []) if isinstance(tag, str)}):
            groups["by_tag"].setdefault(tag, []).append(citation)
        status = citation.get("status")
        if isinstance(status, str):
            groups["by_status"].setdefault(status, []).append(citation)
        batch_id = citation.get("batch_id")
        if isinstance(batch_id, str):
            groups["by_batch"].setdefault(batch_id, []).append(citation)

    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for name, grouped in groups.items():
        index: dict[str, dict[str, Any]] = {}
        for key in sorted(grouped):
            members = sorted(grouped[key], key=citation_sort_key)
            citation_ids = [str(member["citation_id"]) for member in members]
            if name == "by_artifact":
                first = members[0]
                artifact = first["artifact"]
                timestamps = sorted(str(member["created_at"]) for member in members if member.get("created_at") is not None)
                status_counts: dict[str, int] = {}
                for member in members:
                    member_status = str(member["status"])
                    status_counts[member_status] = status_counts.get(member_status, 0) + 1
                index[key] = index_entry(
                    key,
                    citation_ids,
                    display=key,
                    extra={
                        "artifact_id": artifact.get("artifact_id"),
                        "adapter": artifact.get("adapter"),
                        "uri": key,
                        "status_counts": {status: status_counts[status] for status in sorted(status_counts)},
                        "first_seen": timestamps[0] if timestamps else None,
                        "last_seen": timestamps[-1] if timestamps else None,
                    },
                )
            else:
                index[key] = index_entry(key, citation_ids)
        indexes[name] = index
    return indexes


def populate_artifact_index(repo: Repo, projection: dict[str, Any]) -> str:
    artifact_index = projection.get("indexes", {}).get("by_artifact", {})
    records = [
        {
            "schema_version": "c2s.artifact-index.v0.3",
            "record_type": "artifact_index_snapshot",
            **artifact_index[key],
        }
        for key in sorted(artifact_index)
    ]
    dump_jsonl_atomically(repo.artifact_index, records)
    return str(repo.artifact_index)


def refresh_artifact_index(repo: Repo) -> dict[str, Any]:
    try:
        return {"refreshed": True, "path": populate_artifact_index(repo, replay(repo))}
    except C2SError as exc:
        return {"refreshed": False, "error": {"code": exc.code, "message": exc.message, "details": exc.details}}
    except OSError as exc:
        return {
            "refreshed": False,
            "error": {
                "code": "E_ARTIFACT_INDEX_CACHE",
                "message": "derived artifact index could not be refreshed",
                "details": {"path": str(repo.artifact_index), "reason": str(exc)},
            },
        }


def write_grouped_json_exports(repo: Repo, indexes: dict[str, dict[str, dict[str, Any]]]) -> dict[str, str]:
    paths: dict[str, str] = {}
    for name, index in indexes.items():
        path = repo.exports_dir / f"index-{name.replace('_', '-')}.json"
        dump_json(path, index)
        paths[name] = str(path)
    return paths


def slug_for(key: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    return slug or sha256_bytes(key.encode("utf-8")).removeprefix("sha256:")[:16]


def group_slugs(index: dict[str, dict[str, Any]]) -> dict[str, str]:
    used: set[str] = set()
    slugs: dict[str, str] = {}
    for key in sorted(index):
        base = slug_for(key)
        slug = base
        suffix = sha256_bytes(key.encode("utf-8")).removeprefix("sha256:")[:8]
        attempt = 1
        while slug in used:
            slug = f"{base}-{suffix}" if attempt == 1 else f"{base}-{suffix}-{attempt}"
            attempt += 1
        used.add(slug)
        slugs[key] = slug
    return slugs


def write_grouped_site_pages(repo: Repo, projection: dict[str, Any], indexes: dict[str, dict[str, dict[str, Any]]]) -> dict[str, list[str]]:
    group_paths = {"by_artifact": "artifacts", "by_handle": "handles", "by_tag": "tags", "by_status": "status", "by_batch": "batches"}
    citations = {citation["citation_id"]: citation_query_view(citation) for citation in projection["citations"]}
    written: dict[str, list[str]] = {}
    docs = repo.site_dir / "docs"
    for directory in group_paths.values():
        target = docs / directory
        if target.exists():
            shutil.rmtree(target)
    for name, directory in group_paths.items():
        index = indexes[name]
        if not index:
            continue
        target = docs / directory
        target.mkdir(parents=True, exist_ok=True)
        slugs = group_slugs(index)
        listing = [f"# {directory.title()}", ""]
        paths: list[str] = []
        for key in sorted(index):
            entry = index[key]
            filename = f"{slugs[key]}.md"
            display = markdown_text(str(entry.get("display", key)))
            listing.append(f"- [{display}]({filename}) ({entry['count']})")
            lines = [f"# {display}", "", f"- key: `{markdown_text(key)}`", f"- citations: {entry['count']}", "", "## Citations", ""]
            for citation_id in entry["citation_ids"]:
                citation = citations[citation_id]
                label = citation.get("preferred_handle") or citation_id
                lines.append(f"- `{markdown_text(label)}`: `{citation_id}`; `{markdown_text(citation['status'])}`; `{markdown_text(range_summary(citation['locator']))}`")
            path = target / filename
            write_text_atomically(path, "\n".join(lines) + "\n")
            paths.append(str(path))
        write_text_atomically(target / "index.md", "\n".join(listing) + "\n")
        paths.insert(0, str(target / "index.md"))
        written[name] = paths
    return written


def observe_status(repo: Repo, citation: dict[str, Any]) -> str:
    if citation.get("state") == "retracted":
        return "retracted"
    adapter_name = citation["artifact"].get("adapter", "")
    # Late import to avoid circular dependency: adapter.py imports from core.
    from . import adapter as _adapter

    try:
        ad = _adapter.get_adapter(adapter_name)
    except C2SError:
        return "unsupported"
    try:
        observed = ad.observe(repo, citation["artifact"], citation["locator"])
    except C2SError as exc:
        if exc.code in ("E_ADAPTER_MISSING", "E_ARTIFACT_MISSING", "E_ADAPTER_RANGE_INVALID", "E_RANGE_INVALID", "E_ARTIFACT_OUTSIDE_WORKSPACE"):
            return "missing"
        return "adapter_unavailable"
    except Exception:
        return "adapter_unavailable"
    return ad.compare(citation["accepted_evidence"], observed)


def apply_privacy(citation: dict[str, Any], privacy_mode: str, policy: dict[str, Any]) -> None:
    evidence = copy.deepcopy(citation.pop("accepted_evidence", {}))
    accepted_text = evidence.pop("text", None)
    if privacy_mode == "metadata_only":
        return
    if privacy_mode == "hash_only":
        citation["accepted_evidence"] = evidence
        return
    if privacy_mode == "snippet":
        citation["accepted_evidence"] = evidence
        if isinstance(accepted_text, str):
            limit = policy.get("snippet_max_chars", 240)
            limit = limit if isinstance(limit, int) and limit > 0 else 240
            citation["snippet"] = accepted_text[:limit]
        return
    base = validated_private_link_base(policy)
    citation["private_link"] = f"{base}/{quote(citation['artifact']['uri'], safe='')}"


def summarize_status(citations: Any) -> dict[str, int]:
    summary = {status: 0 for status in sorted(VALID_STATUSES)}
    for citation in citations:
        summary[citation.get("status", "unsupported")] += 1
    return summary


def actor_from_args(args: argparse.Namespace) -> dict[str, str]:
    actor = {"kind": getattr(args, "actor_kind", "user")}
    actor_id = getattr(args, "actor_id", None)
    if actor_id:
        actor["id"] = actor_id
    return actor


def cite_selection(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    prepared, selected_handle = prepare_selection_from_args(repo, args)
    bid = batch_id_for([prepared])
    with repo_lock(repo):
        created = append_event(repo, repo.citation_history, citation_event(prepared, bid, actor_from_args(args)))
        handle_created = None
        if selected_handle:
            ensure_handle_available(repo, selected_handle, prepared["citation_id"])
            handle_created = append_event(repo, repo.handle_bindings, handle_event(prepared["citation_id"], selected_handle, "bind", batch_id=bid, actor=actor_from_args(args)))
        cache_refresh = refresh_artifact_index(repo)
    result = {"ok": True, "batch_id": bid, "citation_id": prepared["citation_id"], "event_id": created["event_id"]}
    result["artifact_index"] = cache_refresh
    if handle_created:
        result["handle_event_id"] = handle_created["event_id"]
    return result


def cite_batch(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    request = load_json(Path(args.request))
    mode = request.get("mode", "all_or_nothing")
    if mode not in {"all_or_nothing", "partial"}:
        raise C2SError("E_BATCH_MODE", "batch mode is invalid", mode=mode)
    items = request.get("items")
    if not isinstance(items, list) or not items:
        raise C2SError("E_BATCH_EMPTY", "batch request must include items")
    prepared: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for item in items:
        try:
            artifact = item.get("artifact", {})
            locator = item.get("locator", {})
            prepared_item = prepare_citation(repo, artifact["uri"], int(locator["start"]), int(locator["end"]), adapter=artifact.get("adapter"), expected_content_hash=item.get("expected_content_hash"), label=item.get("label"), tags=item.get("tags", []), note=item.get("note"), client_item_id=item.get("client_item_id"))
            prepared_item["handle"] = item.get("handle")
            prepared.append(prepared_item)
        except (KeyError, ValueError) as exc:
            rejected.append({"client_item_id": item.get("client_item_id"), "code": "E_BATCH_ITEM_INVALID", "message": str(exc)})
        except C2SError as exc:
            rejected.append({"client_item_id": item.get("client_item_id"), "code": exc.code, "message": exc.message, "details": exc.details})
    if rejected and mode == "all_or_nothing":
        return {"ok": False, "batch_id": None, "created": [], "rejected": rejected}
    bid = batch_id_for(prepared)
    created: list[dict[str, Any]] = []
    with repo_lock(repo):
        for item in prepared:
            if item.get("handle"):
                ensure_handle_available(repo, item["handle"], item["citation_id"])
        for item in prepared:
            event = append_event(repo, repo.citation_history, citation_event(item, bid, actor_from_args(args)))
            created.append({"client_item_id": item.get("client_item_id"), "citation_id": item["citation_id"], "event_id": event["event_id"]})
            if item.get("handle"):
                handle_written = append_event(repo, repo.handle_bindings, handle_event(item["citation_id"], item["handle"], "bind", batch_id=bid, actor=actor_from_args(args)))
                created[-1]["handle_event_id"] = handle_written["event_id"]
        cache_refresh = refresh_artifact_index(repo)
    return {"ok": not rejected, "batch_id": bid, "created": created, "rejected": rejected, "artifact_index": cache_refresh}


def ensure_citation_exists(repo: Repo, citation_id: str) -> None:
    if citation_id not in {c["citation_id"] for c in replay(repo)["citations"]}:
        raise C2SError("E_CITATION_NOT_FOUND", "citation ID does not exist", citation_id=citation_id)


def citation_for_mutation(repo: Repo, citation_id: str) -> dict[str, Any]:
    for citation in replay(repo, privacy_mode="metadata_only")["citations"]:
        if citation["citation_id"] == citation_id:
            return citation
    raise C2SError("E_CITATION_NOT_FOUND", "citation ID does not exist", citation_id=citation_id)


def current_evidence(repo: Repo, citation: dict[str, Any], expected_content_hash: str | None = None) -> dict[str, Any]:
    uri = citation["artifact"]["uri"]
    source = canonical_text(read_text_artifact(repo, uri))
    locator = citation["locator"]
    start, end = int(locator["start"]), int(locator["end"])
    make_locator(source, start, end)
    selected = source[start:end]
    if not selected:
        raise C2SError("E_SELECTION_EMPTY", "selection is empty", citation_id=citation["citation_id"])
    evidence = evidence_for_text(selected)
    validate_expected_hash(expected_content_hash, evidence["content_hash"])
    return evidence


def preflight_selection(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    prepared, selected_handle = prepare_selection_from_args(repo, args)
    return {
        "ok": True,
        "citation_id": prepared["citation_id"],
        "artifact": prepared["artifact"],
        "locator": prepared["locator"],
        "evidence": {key: value for key, value in prepared["accepted_evidence"].items() if key != "text"},
        "handle": selected_handle,
    }


def accept_current(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    citation = citation_for_mutation(repo, args.citation_id)
    if citation["state"] == "retracted":
        raise C2SError("E_CITATION_RETRACTED", "retracted citation must be restored before acceptance", citation_id=args.citation_id)
    evidence = current_evidence(repo, citation, getattr(args, "expected_content_hash", None))
    citation_events, _ = read_events(repo)
    accepted_hash = None
    for event in citation_events:
        if event.get("citation_id") == args.citation_id and event.get("event_type") in {"citation.created", "citation.accepted"}:
            accepted_hash = event["accepted_evidence"]["content_hash"]
    if evidence["content_hash"] == accepted_hash:
        return {"ok": True, "citation_id": args.citation_id, "idempotent": True, "event_id": None}
    with repo_lock(repo):
        event = append_event(repo, repo.citation_history, citation_update_event("citation.accepted", args.citation_id, actor_from_args(args), accepted_evidence=evidence))
        cache_refresh = refresh_artifact_index(repo)
    return {"ok": True, "citation_id": args.citation_id, "event_id": event["event_id"], "artifact_index": cache_refresh}


def set_citation_state(args: argparse.Namespace, event_type: str, desired_state: str) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    citation = citation_for_mutation(repo, args.citation_id)
    if citation["state"] == desired_state:
        return {"ok": True, "citation_id": args.citation_id, "idempotent": True, "event_id": None}
    with repo_lock(repo):
        event = append_event(repo, repo.citation_history, citation_update_event(event_type, args.citation_id, actor_from_args(args)))
        cache_refresh = refresh_artifact_index(repo)
    return {"ok": True, "citation_id": args.citation_id, "event_id": event["event_id"], "artifact_index": cache_refresh}


def retract(args: argparse.Namespace) -> dict[str, Any]:
    return set_citation_state(args, "citation.retracted", "retracted")


def restore(args: argparse.Namespace) -> dict[str, Any]:
    return set_citation_state(args, "citation.restored", "active")


def relocate(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    citation = citation_for_mutation(repo, args.citation_id)
    uri = args.artifact or citation["artifact"]["uri"]
    adapter = adapter_for_uri(uri, getattr(args, "adapter", None) or citation["artifact"].get("adapter"))
    source = canonical_text(read_text_artifact(repo, uri))
    locator = make_locator(source, args.start, args.end)
    selected = source[args.start:args.end]
    if not selected:
        raise C2SError("E_SELECTION_EMPTY", "relocation selection is empty", citation_id=args.citation_id)
    evidence = evidence_for_text(selected)
    validate_expected_hash(getattr(args, "expected_content_hash", None), evidence["content_hash"])
    if locator == citation["locator"] and normalize_uri(uri) == citation["artifact"]["uri"]:
        return {"ok": True, "citation_id": args.citation_id, "idempotent": True, "event_id": None}
    artifact = artifact_identity(repo, uri, adapter)
    with repo_lock(repo):
        event = append_event(repo, repo.citation_history, citation_update_event("citation.relocated", args.citation_id, actor_from_args(args), artifact=artifact, locator=locator, observed_content_hash=evidence["content_hash"]))
        cache_refresh = refresh_artifact_index(repo)
    return {"ok": True, "citation_id": args.citation_id, "event_id": event["event_id"], "artifact_index": cache_refresh}


def note(args: argparse.Namespace) -> dict[str, Any]:
    if not isinstance(args.note, str) or not args.note.strip():
        raise C2SError("E_NOTE_EMPTY", "note text must not be empty")
    repo = repo_from_arg(args.repo)
    citation_for_mutation(repo, args.citation_id)
    with repo_lock(repo):
        event = append_event(repo, repo.citation_history, citation_update_event("citation.noted", args.citation_id, actor_from_args(args), note=args.note))
    return {"ok": True, "citation_id": args.citation_id, "event_id": event["event_id"]}


def ensure_handle_available(repo: Repo, handle: str, citation_id: str) -> None:
    _, handle_events = read_events(repo)
    bound = replay_handles(handle_events)["handle_to_citation"].get(handle)
    if bound and bound != citation_id:
        raise C2SError("E_HANDLE_COLLISION", "handle is already bound to another citation", handle=handle, citation_id=bound)


def set_handle(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    ensure_citation_exists(repo, args.citation_id)
    if args.action != "retire":
        ensure_handle_available(repo, args.handle, args.citation_id)
    with repo_lock(repo):
        event = append_event(repo, repo.handle_bindings, handle_event(args.citation_id, args.handle, args.action, previous_handle=args.previous_handle, actor=actor_from_args(args)))
        cache_refresh = refresh_artifact_index(repo)
    return {"ok": True, "citation_id": args.citation_id, "handle": args.handle, "action": args.action, "event_id": event["event_id"], "artifact_index": cache_refresh}


def status(args: argparse.Namespace) -> dict[str, Any]:
    return replay(repo_from_arg(args.repo), privacy_mode=args.privacy)


def citation_query_view(citation: dict[str, Any]) -> dict[str, Any]:
    return {
        "citation_id": citation["citation_id"],
        "state": citation["state"],
        "artifact": citation["artifact"],
        "locator": citation["locator"],
        "metadata": {"tags": list(citation.get("metadata", {}).get("tags", []))},
        "batch_id": citation.get("batch_id"),
        "preferred_handle": citation.get("preferred_handle"),
        "aliases": list(citation.get("aliases", [])),
        "status": citation["status"],
        "created_at": citation.get("created_at"),
        "created_event_id": citation.get("created_event_id"),
    }


def citations(args: argparse.Namespace) -> dict[str, Any]:
    projection = replay(repo_from_arg(args.repo), privacy_mode=args.privacy)
    filter_specs = [
        ("artifact", "by_artifact", normalize_uri(args.artifact) if args.artifact else None),
        ("handle", "by_handle", args.handle),
        ("tag", "by_tag", args.tag),
        ("status", "by_status", args.status),
        ("batch", "by_batch", args.batch),
    ]
    matching_ids: set[str] | None = None
    applied_filters: dict[str, str] = {}
    for name, index_name, value in filter_specs:
        if value is None:
            continue
        applied_filters[name] = value
        entry = projection["indexes"][index_name].get(value)
        group_ids = set(entry["citation_ids"]) if entry else set()
        matching_ids = group_ids if matching_ids is None else matching_ids & group_ids
    if matching_ids is None:
        matching_ids = {citation["citation_id"] for citation in projection["citations"]}
    results = [citation_query_view(citation) for citation in projection["citations"] if citation["citation_id"] in matching_ids]
    return {
        "ok": True,
        "schema_version": "c2s.citations.v0.3",
        "repository_id": projection["repository_id"],
        "privacy_mode": projection["privacy_mode"],
        "filters": applied_filters,
        "citations": results,
    }


def check(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    project = repo.project
    return {"ok": True, "repository_id": project["repository_id"], "citation_tip": validate_chain(repo.citation_history), "handle_tip": validate_chain(repo.handle_bindings)}


def lookup_actions(args: argparse.Namespace) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    projection = replay(repo, privacy_mode=args.privacy)
    query_range = {"start": args.start, "end": args.end}
    matches: list[dict[str, Any]] = []
    for citation in projection["citations"]:
        if normalize_uri(citation["artifact"]["uri"]) != normalize_uri(args.artifact):
            continue
        loc = citation["locator"]
        match = match_kind(query_range, loc)
        if not match:
            continue
        actions = ["open", "set_handle", "note"]
        if citation["state"] == "retracted":
            actions.append("restore")
        elif citation["status"] == "resolved":
            actions.append("retract")
        else:
            actions += ["accept_current", "relocate", "retract"]
        matches.append({"citation_id": citation["citation_id"], "preferred_handle": citation.get("preferred_handle"), "match_kind": match, "range_summary": range_summary(loc), "status": citation["status"], "actions": actions, "_sort": overlap_sort_key(query_range, loc, citation)})
    matches.sort(key=lambda m: m.pop("_sort"))
    if not matches:
        return {"ok": True, "matches": [], "actions": ["cite"]}
    return {"ok": True, "matches": matches, "requires_picker": len(matches) > 1}


def match_kind(query: dict[str, int], loc: dict[str, Any]) -> str | None:
    qs, qe = query["start"], query["end"]
    ls, le = int(loc["start"]), int(loc["end"])
    if qs == qe and ls <= qs <= le:
        return "contains"
    if qs == ls and qe == le:
        return "exact"
    if ls <= qs and qe <= le:
        return "contains"
    if qs <= ls and le <= qe:
        return "contained_by"
    if max(qs, ls) < min(qe, le):
        return "overlaps"
    return None


def overlap_sort_key(query: dict[str, int], loc: dict[str, Any], citation: dict[str, Any]) -> tuple[int, int, int, str]:
    rank = {"exact": 0, "contains": 1, "contained_by": 2, "overlaps": 3}.get(match_kind(query, loc) or "", 9)
    return (rank, int(loc["end"]) - int(loc["start"]), 0 if citation.get("preferred_handle") else 1, citation["citation_id"])


def range_summary(loc: dict[str, Any]) -> str:
    return f"lines {loc['start_line']}-{loc['end_line']}" if "start_line" in loc and "end_line" in loc else f"{loc['start']}-{loc['end']}"


def export(args: argparse.Namespace) -> dict[str, Any]:
    try:
        repo = repo_from_arg(args.repo)
        projection = replay(repo, privacy_mode=args.privacy)
        repo.exports_dir.mkdir(parents=True, exist_ok=True)
        status_path = repo.exports_dir / "c2s-status.json"
        citations_path = repo.exports_dir / "c2s-citations.jsonl"
        dump_json(status_path, projection)
        dump_jsonl_atomically(citations_path, projection["citations"])
        grouped_paths = write_grouped_json_exports(repo, projection["indexes"])
        site_groups = write_grouped_site_pages(repo, projection, projection["indexes"])
        write_default_mkdocs(repo, site_groups)
        write_site_docs(repo, projection)
        return {"ok": True, "privacy_mode": projection["privacy_mode"], "status_path": str(status_path), "citations_path": str(citations_path), "grouped_index_paths": grouped_paths, "grouped_site_paths": site_groups, "artifact_index": refresh_artifact_index(repo), "site_dir": str(repo.site_dir)}
    except OSError as exc:
        raise C2SError("E_PROJECTION_WRITE", "could not write generated projection", reason=str(exc)) from exc


def write_default_mkdocs(repo: Repo, site_groups: dict[str, list[str]] | None = None) -> None:
    mkdocs = repo.site_dir / "mkdocs.yml"
    mkdocs.parent.mkdir(parents=True, exist_ok=True)
    nav = ["site_name: Cite2Site", "nav:", "  - Home: index.md", "  - Citations: citations.md"]
    for name, paths in (site_groups or {}).items():
        if paths:
            directory = Path(paths[0]).parent.name
            nav.append(f"  - {directory.title()}: {directory}/index.md")
    write_text_atomically(mkdocs, "\n".join(nav) + "\n")


def write_site_docs(repo: Repo, projection: dict[str, Any]) -> None:
    docs = repo.site_dir / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    index = ["# Cite2Site", "", "Metadata-only citation projection.", "", "## Summary", ""]
    for key, value in sorted(projection.get("summary", {}).items()):
        index.append(f"- {key}: {value}")
    write_text_atomically(docs / "index.md", "\n".join(index) + "\n")
    lines = ["# Citations", ""]
    for citation in projection.get("citations", []):
        label = citation.get("preferred_handle") or citation["citation_id"]
        lines.extend([f"## {label}", "", f"- citation_id: `{citation['citation_id']}`", f"- status: `{citation['status']}`", f"- artifact: `{citation['artifact']['uri']}`", f"- range: `{range_summary(citation['locator'])}`", ""])
    write_text_atomically(docs / "citations.md", "\n".join(lines) + "\n")


def markdown_text(value: str) -> str:
    return html.escape(value, quote=False).replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)")
