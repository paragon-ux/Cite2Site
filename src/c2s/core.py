from __future__ import annotations

import argparse
import contextlib
import dataclasses
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
        raise C2SError("E_FILE_NOT_FOUND", f"file not found: {path}", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise C2SError("E_JSON_INVALID", f"invalid JSON in {path}", path=str(path), line=exc.lineno) from exc


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(value, fh, indent=2, sort_keys=True)
        fh.write("\n")


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
                raise C2SError("E_JSONL_INVALID", f"invalid JSONL in {path}", path=str(path), line=lineno) from exc
    return records


def validate_chain(path: Path) -> str:
    previous = EMPTY_HASH
    for index, event in enumerate(read_jsonl(path), 1):
        if event.get("previous_event_hash") != previous:
            raise C2SError("E_EVENT_CHAIN", "event chain hash mismatch", path=str(path), record=index)
        event_id = event.get("event_id")
        if not isinstance(event_id, str):
            raise C2SError("E_EVENT_ID_MISSING", "event is missing event_id", path=str(path), record=index)
        expected = hash_event(event)
        if event_id != expected:
            raise C2SError("E_EVENT_HASH", "event_id does not match canonical event hash", path=str(path), record=index)
        previous = event_id
    return previous


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
            raise C2SError("E_REPO_NOT_INITIALIZED", "Cite2Site repository is not initialized", repo=str(self.root))
        return load_json(self.project_file)

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
        raise C2SError("E_REPO_EXISTS", "Cite2Site repository already exists", repo=str(repo.root))
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
            "publication": {"privacy_mode": "metadata_only"},
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
        raise C2SError("E_REPO_LOCKED", "could not acquire citation repository lock", repo=str(repo.root))
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
    if requested:
        if requested not in {"filesystem-text", "markdown"}:
            raise C2SError("E_ADAPTER_UNSUPPORTED", "adapter is unsupported", adapter=requested)
        return requested
    return "markdown" if uri.lower().endswith((".md", ".markdown")) else "filesystem-text"


def normalize_uri(uri: str) -> str:
    return uri.replace("\\", "/")


def resolve_artifact_path(repo: Repo, uri: str) -> Path:
    path = Path(uri)
    return path if path.is_absolute() else (repo.workspace_root / path).resolve()


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


def replay(repo: Repo, privacy_mode: str = "metadata_only") -> dict[str, Any]:
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
                "created_at": event.get("created_at"),
                "created_event_id": event.get("event_id"),
            }
        elif event.get("event_type") == "citation.accepted" and cid in citations:
            citations[cid]["accepted_evidence"] = event["accepted_evidence"]
        elif event.get("event_type") == "citation.relocated" and cid in citations:
            citations[cid]["locator"] = event["locator"]
        elif event.get("event_type") == "citation.retracted" and cid in citations:
            citations[cid]["state"] = "retracted"
        elif event.get("event_type") == "citation.restored" and cid in citations:
            citations[cid]["state"] = "active"

    handles = replay_handles(handle_events)
    for cid, citation in citations.items():
        citation["preferred_handle"] = handles["preferred_by_citation"].get(cid)
        citation["aliases"] = sorted(handles["aliases_by_citation"].get(cid, set()))
        citation["status"] = observe_status(repo, citation)
        apply_privacy(citation, privacy_mode)

    return {
        "ok": True,
        "schema_version": "c2s.status.v0.3",
        "repository_id": repo.repository_id,
        "privacy_mode": privacy_mode,
        "citations": [citations[cid] for cid in order],
        "summary": summarize_status(citations.values()),
    }


def observe_status(repo: Repo, citation: dict[str, Any]) -> str:
    if citation.get("state") == "retracted":
        return "retracted"
    if citation["artifact"].get("adapter") not in {"filesystem-text", "markdown"}:
        return "unsupported"
    try:
        text = canonical_text(read_text_artifact(repo, citation["artifact"]["uri"]))
    except C2SError as exc:
        return "missing" if exc.code == "E_ARTIFACT_MISSING" else "adapter_unavailable"
    locator = citation["locator"]
    start, end = int(locator["start"]), int(locator["end"])
    if end > len(text):
        return "missing"
    observed = evidence_for_text(text[start:end])
    return "resolved" if observed["content_hash"] == citation["accepted_evidence"]["content_hash"] else "changed"


def apply_privacy(citation: dict[str, Any], privacy_mode: str) -> None:
    if privacy_mode not in {"metadata_only", "hash_only", "snippet", "private_link"}:
        raise C2SError("E_PRIVACY_MODE", "privacy mode is invalid", privacy_mode=privacy_mode)


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
    prepared = prepare_citation(repo, args.artifact, args.start, args.end, adapter=args.adapter, expected_content_hash=args.expected_content_hash, label=args.label, tags=args.tag, note=args.note)
    bid = batch_id_for([prepared])
    with repo_lock(repo):
        created = append_event(repo, repo.citation_history, citation_event(prepared, bid, actor_from_args(args)))
        handle_created = None
        if args.handle:
            ensure_handle_available(repo, args.handle, prepared["citation_id"])
            handle_created = append_event(repo, repo.handle_bindings, handle_event(prepared["citation_id"], args.handle, "bind", batch_id=bid, actor=actor_from_args(args)))
    result = {"ok": True, "batch_id": bid, "citation_id": prepared["citation_id"], "event_id": created["event_id"]}
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
    return {"ok": not rejected, "batch_id": bid, "created": created, "rejected": rejected}


def ensure_citation_exists(repo: Repo, citation_id: str) -> None:
    if citation_id not in {c["citation_id"] for c in replay(repo)["citations"]}:
        raise C2SError("E_CITATION_NOT_FOUND", "citation ID does not exist", citation_id=citation_id)


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
    return {"ok": True, "citation_id": args.citation_id, "handle": args.handle, "action": args.action, "event_id": event["event_id"]}


def status(args: argparse.Namespace) -> dict[str, Any]:
    return replay(repo_from_arg(args.repo), privacy_mode=args.privacy)


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
        actions = ["open"]
        actions += ["set_handle", "add_alias", "undo", "redo"] if citation["status"] == "resolved" else ["set_handle", "accept_current", "relocate", "retire"]
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
    repo = repo_from_arg(args.repo)
    projection = replay(repo, privacy_mode=args.privacy)
    repo.exports_dir.mkdir(parents=True, exist_ok=True)
    status_path = repo.exports_dir / "c2s-status.json"
    citations_path = repo.exports_dir / "c2s-citations.jsonl"
    dump_json(status_path, projection)
    with citations_path.open("w", encoding="utf-8", newline="\n") as fh:
        for citation in projection["citations"]:
            fh.write(json.dumps(citation, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    write_default_mkdocs(repo)
    write_site_docs(repo, projection)
    return {"ok": True, "privacy_mode": args.privacy, "status_path": str(status_path), "citations_path": str(citations_path), "site_dir": str(repo.site_dir)}


def write_default_mkdocs(repo: Repo) -> None:
    mkdocs = repo.site_dir / "mkdocs.yml"
    mkdocs.parent.mkdir(parents=True, exist_ok=True)
    mkdocs.write_text("site_name: Cite2Site\nnav:\n  - Home: index.md\n  - Citations: citations.md\n", encoding="utf-8", newline="\n")


def write_site_docs(repo: Repo, projection: dict[str, Any]) -> None:
    docs = repo.site_dir / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    index = ["# Cite2Site", "", "Metadata-only citation projection.", "", "## Summary", ""]
    for key, value in sorted(projection.get("summary", {}).items()):
        index.append(f"- {key}: {value}")
    (docs / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
    lines = ["# Citations", ""]
    for citation in projection.get("citations", []):
        label = citation.get("preferred_handle") or citation["citation_id"]
        lines.extend([f"## {label}", "", f"- citation_id: `{citation['citation_id']}`", f"- status: `{citation['status']}`", f"- artifact: `{citation['artifact']['uri']}`", f"- range: `{range_summary(citation['locator'])}`", ""])
    (docs / "citations.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
