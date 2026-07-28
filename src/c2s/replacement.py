from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapter import TEXT_CANON, evidence_hash, read_text_artifact, select_text
from .core import C2SError, append_jsonl, new_id, read_json, sha256_json, utc_now, write_json

ARCHIVED_PROJECT_SCHEMAS = {"c2s.project.v0.3"}
REPLACEMENT_PROJECT_SCHEMA = "c2s.project.replacement.v1"
OPERATION_SCHEMA = "c2s.operation.replacement.v1"
PROJECTION_SCHEMA = "c2s.projection.replacement.v1"


def repo_from_arg(repo: str | Path | None) -> Path:
    return Path(repo).expanduser().resolve() if repo is not None else (Path.home() / ".c2s").resolve()


def _project_path(repo: Path) -> Path:
    return repo / "project.json"


def _operations_path(repo: Path) -> Path:
    return repo / "operations.jsonl"


def _load_project_json(repo_dir: Path) -> dict[str, Any]:
    project = _project_path(repo_dir)
    try:
        data = read_json(project)
    except C2SError as exc:
        if exc.code == "E_FILE_NOT_FOUND":
            raise C2SError("E_REPO_NOT_INITIALIZED", "replacement repository is not initialized") from exc
        raise
    if not isinstance(data, dict):
        raise C2SError("E_JSON_INVALID", "replacement repository project file must be a JSON object")
    return data


def assert_replacement_repository(repo: str | Path) -> dict[str, Any]:
    repo_dir = Path(repo).expanduser().resolve()
    project = _load_project_json(repo_dir)
    schema = project.get("schema_version")
    if schema in ARCHIVED_PROJECT_SCHEMAS or (
        (repo_dir / "citation-history.jsonl").exists()
        and (repo_dir / "handle-bindings.jsonl").exists()
    ):
        raise C2SError(
            "E_ARCHIVED_PROTOCOL_UNSUPPORTED",
            "repository uses an archived Cite2Site authority format unsupported by the replacement protocol",
            archived_schema=schema,
        )
    if schema != REPLACEMENT_PROJECT_SCHEMA:
        raise C2SError(
            "E_SCHEMA_UNSUPPORTED",
            "replacement repository schema version is not supported",
            expected=REPLACEMENT_PROJECT_SCHEMA,
            actual=schema,
        )
    return project


def _semantic_hash(payload: dict[str, Any]) -> str:
    return sha256_json(payload)


def _operation_id(idempotency_key: str, command: str, payload_hash: str) -> str:
    digest = sha256_json({"idempotency_key": idempotency_key, "command": command, "payload_hash": payload_hash})
    return "op_" + digest.removeprefix("sha256:")[:32]


def _read_operations(repo: Path) -> list[dict[str, Any]]:
    path = _operations_path(repo)
    if not path.exists():
        return []
    operations: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        import json

        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise C2SError("E_JSON_INVALID", "operation log contains invalid JSON", line=number) from exc
        if item.get("status") != "completed":
            raise C2SError("E_OPERATION_INCOMPLETE", "operation log contains an incomplete operation", line=number)
        operations.append(item)
    return operations


def _existing_operation(repo: Path, idempotency_key: str, command: str, payload_hash: str) -> dict[str, Any] | None:
    for operation in _read_operations(repo):
        if operation.get("idempotency_key") != idempotency_key:
            continue
        if operation.get("command") == command and operation.get("semantic_payload_hash") == payload_hash:
            result = dict(operation.get("result", {}))
            result["idempotent_replay"] = True
            return result
        raise C2SError("E_IDEMPOTENCY_CONFLICT", "idempotency key was already used with a different payload")
    return None


def _append_operation(
    repo: Path,
    *,
    idempotency_key: str,
    command: str,
    payload_hash: str,
    events: list[dict[str, Any]],
    result: dict[str, Any],
) -> dict[str, Any]:
    operation_id = _operation_id(idempotency_key, command, payload_hash)
    record = {
        "schema_version": OPERATION_SCHEMA,
        "operation_id": operation_id,
        "idempotency_key": idempotency_key,
        "command": command,
        "semantic_payload_hash": payload_hash,
        "status": "completed",
        "created_at": utc_now(),
        "events": events,
        "result": {"ok": True, "operation_id": operation_id, **result},
    }
    append_jsonl(_operations_path(repo), record)
    return dict(record["result"])


def init_repo(repo: str | Path | None, *, idempotency_key: str) -> dict[str, Any]:
    repo_dir = repo_from_arg(repo)
    if _project_path(repo_dir).exists():
        project = assert_replacement_repository(repo_dir)
        return {"ok": True, "message": "Already initialized", "repository_id": project["repository_id"], "default_group_id": project["default_group_id"]}
    if (repo_dir / "citation-history.jsonl").exists() or (repo_dir / "handle-bindings.jsonl").exists():
        raise C2SError("E_ARCHIVED_PROTOCOL_UNSUPPORTED", "repository uses an archived Cite2Site authority format unsupported by the replacement protocol")
    repo_dir.mkdir(parents=True, exist_ok=True)
    repository_id = new_id("repo")
    default_group_id = new_id("grp")
    project = {
        "schema_version": REPLACEMENT_PROJECT_SCHEMA,
        "repository_id": repository_id,
        "default_group_id": default_group_id,
        "created_at": utc_now(),
    }
    write_json(_project_path(repo_dir), project)
    payload = {"repository_id": repository_id, "default_group_id": default_group_id}
    payload_hash = _semantic_hash(payload)
    replay = _existing_operation(repo_dir, idempotency_key, "repository.init", payload_hash)
    if replay is not None:
        return replay
    events = [
        {"event_type": "repository.initialized", "repository_id": repository_id},
        {
            "event_type": "group.created",
            "group_id": default_group_id,
            "name": "Inbox",
            "parent_group_id": None,
            "duplicate_policy": "handle",
        },
    ]
    return _append_operation(repo_dir, idempotency_key=idempotency_key, command="repository.init", payload_hash=payload_hash, events=events, result={"repository_id": repository_id, "default_group_id": default_group_id})


def replay(repo: str | Path) -> dict[str, Any]:
    repo_dir = repo_from_arg(repo)
    project = assert_replacement_repository(repo_dir)
    state: dict[str, Any] = {
        "schema_version": PROJECTION_SCHEMA,
        "repository_id": project["repository_id"],
        "default_group_id": project["default_group_id"],
        "groups": {},
        "handles": {},
        "citations": {},
        "supersessions": [],
    }
    for operation in _read_operations(repo_dir):
        for event in operation.get("events", []):
            typ = event.get("event_type")
            if typ == "group.created":
                gid = event["group_id"]
                state["groups"][gid] = {
                    "group_id": gid,
                    "name": event.get("name", ""),
                    "parent_group_id": event.get("parent_group_id"),
                    "duplicate_policy": event.get("duplicate_policy", "handle"),
                    "tally": [],
                }
            elif typ == "handle.created":
                hid = event["handle_id"]
                state["handles"][hid] = {"handle_id": hid, "group_id": event["group_id"], "name": event["name"], "tally": []}
            elif typ == "citation.created":
                state["citations"][event["citation_id"]] = dict(event)
            elif typ == "group.membership.added":
                group = state["groups"][event["group_id"]]
                if event["citation_id"] not in group["tally"]:
                    group["tally"].append(event["citation_id"])
            elif typ == "handle.binding.added":
                handle = state["handles"][event["handle_id"]]
                if event["citation_id"] not in handle["tally"]:
                    handle["tally"].append(event["citation_id"])
            elif typ == "scoped.supersession.applied":
                state["supersessions"].append(dict(event))
    for group in state["groups"].values():
        group["tally"] = sorted(group["tally"])
    for handle in state["handles"].values():
        handle["tally"] = sorted(handle["tally"])
    return state


def _resolve_handle(state: dict[str, Any], group_id: str, handle_name: str | None, handle_id: str | None) -> tuple[str | None, list[dict[str, Any]]]:
    if handle_id:
        handle = state["handles"].get(handle_id)
        if handle is None or handle["group_id"] != group_id:
            raise C2SError("E_HANDLE_NOT_FOUND", "handle_id does not exist in group", handle_id=handle_id, group_id=group_id)
        return handle_id, []
    if not handle_name:
        return None, []
    matches = [h for h in state["handles"].values() if h["group_id"] == group_id and h["name"] == handle_name]
    if len(matches) > 1:
        raise C2SError("E_HANDLE_NAME_AMBIGUOUS", "handle name resolves to multiple handle IDs", group_id=group_id, handle=handle_name)
    if len(matches) == 1:
        return matches[0]["handle_id"], []
    new_handle_id = new_id("hdl")
    return new_handle_id, [{"event_type": "handle.created", "handle_id": new_handle_id, "group_id": group_id, "name": handle_name}]


def _supersession_events(state: dict[str, Any], group_id: str, handle_id: str | None, new_citation_id: str, target_fingerprint: str) -> list[dict[str, Any]]:
    group = state["groups"][group_id]
    policy = group.get("duplicate_policy", "handle")
    if policy == "none":
        return []
    if policy == "handle" and handle_id is None:
        return []
    candidates: list[str] = [new_citation_id]
    if policy == "group":
        scope = "group"
        for cid in group.get("tally", []):
            if state["citations"][cid].get("target_fingerprint") == target_fingerprint:
                candidates.append(cid)
    else:
        scope = "handle"
        for cid in state["handles"].get(handle_id, {}).get("tally", []):
            if state["citations"][cid].get("target_fingerprint") == target_fingerprint:
                candidates.append(cid)
    candidates = sorted(set(candidates))
    if len(candidates) < 2:
        return []
    dominant = max(candidates)
    events = []
    for cid in candidates:
        if cid == dominant:
            continue
        event = {
            "event_type": "scoped.supersession.applied",
            "scope": scope,
            "group_id": group_id,
            "superseded_citation_id": cid,
            "dominant_citation_id": dominant,
            "target_fingerprint": target_fingerprint,
            "reason": "superseded",
        }
        if scope == "handle":
            event["handle_id"] = handle_id
        events.append(event)
    return events


def cite_selection(args: Any) -> dict[str, Any]:
    repo_dir = repo_from_arg(args.repo)
    project = assert_replacement_repository(repo_dir)
    group_id = getattr(args, "group_id", None) or project["default_group_id"]
    supplied_text = getattr(args, "selected_text", None)
    if supplied_text is None:
        source = read_text_artifact(args.artifact)
        selected = select_text(source, int(args.start), int(args.end))
    else:
        selected = str(supplied_text)
        if selected == "":
            raise C2SError("E_EMPTY_SELECTION", "selection captured zero characters", start=int(args.start), end=int(args.end))
    locator = {"start": int(args.start), "end": int(args.end)}
    fingerprint_payload = {
        "artifact": args.artifact,
        "locator": locator,
        "evidence_hash": evidence_hash(selected),
        "canonicalization": TEXT_CANON,
    }
    target_fingerprint = sha256_json(fingerprint_payload)
    payload = {
        "artifact": args.artifact,
        "locator": locator,
        "group_id": group_id,
        "handle": getattr(args, "handle", None),
        "handle_id": getattr(args, "handle_id", None),
        "target_fingerprint": target_fingerprint,
    }
    payload_hash = _semantic_hash(payload)
    replayed = _existing_operation(repo_dir, args.idempotency_key, "citation.create", payload_hash)
    if replayed is not None:
        return replayed
    state = replay(repo_dir)
    if group_id not in state["groups"]:
        raise C2SError("E_GROUP_NOT_FOUND", "group_id does not exist", group_id=group_id)
    handle_id, handle_events = _resolve_handle(state, group_id, getattr(args, "handle", None), getattr(args, "handle_id", None))
    citation_id = new_id("cit")
    events = [
        {
            "event_type": "citation.created",
            "citation_id": citation_id,
            "target_fingerprint": target_fingerprint,
            "artifact": args.artifact,
            "locator": locator,
            "evidence_hash": evidence_hash(selected),
            "canonicalization": TEXT_CANON,
        },
        {"event_type": "group.membership.added", "group_id": group_id, "citation_id": citation_id},
        *handle_events,
    ]
    if handle_id is not None:
        events.append({"event_type": "handle.binding.added", "handle_id": handle_id, "group_id": group_id, "citation_id": citation_id})
    events.extend(_supersession_events(state, group_id, handle_id, citation_id, target_fingerprint))
    return _append_operation(
        repo_dir,
        idempotency_key=args.idempotency_key,
        command="citation.create",
        payload_hash=payload_hash,
        events=events,
        result={"citation_id": citation_id, "group_id": group_id, "handle_id": handle_id, "target_fingerprint": target_fingerprint},
    )


def cite_integration_payload(repo: str | Path, message: dict[str, Any]) -> dict[str, Any]:
    from types import SimpleNamespace

    payload = message.get("payload", {})
    if not isinstance(payload, dict):
        raise C2SError("E_EXTENSION_INVALID", "payload must be an object")
    return cite_selection(
        SimpleNamespace(
            repo=repo,
            artifact=str(payload.get("artifact", "")),
            start=int(payload.get("start", 0)),
            end=int(payload.get("end", 0)),
            group_id=payload.get("group_id"),
            handle=payload.get("handle_name"),
            handle_id=payload.get("handle_id"),
            idempotency_key=message["idempotency_key"],
            selected_text=payload.get("selected_text"),
        )
    )


def lookup_actions(args: Any) -> dict[str, Any]:
    repo_dir = repo_from_arg(args.repo)
    state = replay(repo_dir)
    matches = []
    for citation in state["citations"].values():
        if citation.get("artifact") != args.artifact:
            continue
        loc = citation.get("locator", {})
        if int(loc.get("start", -1)) < int(args.end) and int(args.start) < int(loc.get("end", -1)):
            matches.append({
                "citation_id": citation["citation_id"],
                "target_fingerprint": citation["target_fingerprint"],
                "locator": loc,
            })
    return {
        "ok": True,
        "schema_version": "c2s.integration.replacement.v1",
        "matches": sorted(matches, key=lambda m: m["citation_id"]),
        "actions": [
            {
                "action": "citation.create",
                "requires_idempotency_key": True,
                "group_id": state["default_group_id"],
            }
        ],
    }


def status(args: Any) -> dict[str, Any]:
    state = replay(repo_from_arg(args.repo))
    return {"ok": True, **_projection_lists(state)}


def _projection_lists(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PROJECTION_SCHEMA,
        "repository_id": state["repository_id"],
        "default_group_id": state["default_group_id"],
        "groups": sorted(state["groups"].values(), key=lambda g: g["group_id"]),
        "handles": sorted(state["handles"].values(), key=lambda h: h["handle_id"]),
        "citations": sorted(state["citations"].values(), key=lambda c: c["citation_id"]),
        "supersessions": sorted(state["supersessions"], key=lambda s: (s["group_id"], s.get("handle_id", ""), s["superseded_citation_id"], s["dominant_citation_id"])),
    }


def export(args: Any) -> dict[str, Any]:
    repo_dir = repo_from_arg(args.repo)
    projection = status(args)
    exports = repo_dir / "exports"
    site_docs = repo_dir / "site" / "docs"
    write_json(exports / "c2s-status.json", projection)
    lines = ["# Cite2Site", "", f"Repository: `{projection['repository_id']}`", "", "## Groups", ""]
    for group in projection["groups"]:
        lines.append(f"- `{group['group_id']}` {group['name']} ({len(group['tally'])} citations)")
    (site_docs).mkdir(parents=True, exist_ok=True)
    (site_docs / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "exports": [str(exports / "c2s-status.json"), str(site_docs / "index.md")]}


def check(args: Any) -> dict[str, Any]:
    state = replay(repo_from_arg(args.repo))
    return {"ok": True, "repository_id": state["repository_id"], "operations": len(_read_operations(repo_from_arg(args.repo)))}


def reconcile(args: Any) -> dict[str, Any]:
    repo = repo_from_arg(args.repo)
    other = repo_from_arg(args.other_repo)
    project = assert_replacement_repository(repo)
    other_project = assert_replacement_repository(other)
    if project["repository_id"] != other_project["repository_id"]:
        raise C2SError("E_RECONCILE_REPOSITORY_MISMATCH", "repositories do not share replacement repository identity")

    current_ops = _read_operations(repo)
    other_ops = _read_operations(other)
    current_by_id = {op["operation_id"]: op for op in current_ops}
    current_by_key = {op["idempotency_key"]: op for op in current_ops}
    to_import: list[dict[str, Any]] = []
    for operation in sorted(other_ops, key=lambda item: item["operation_id"]):
        existing = current_by_id.get(operation["operation_id"])
        if existing is not None:
            if existing.get("semantic_payload_hash") != operation.get("semantic_payload_hash"):
                raise C2SError("E_OPERATION_ID_CONFLICT", "same operation_id has different payload")
            continue
        by_key = current_by_key.get(operation["idempotency_key"])
        if by_key is not None and by_key.get("semantic_payload_hash") != operation.get("semantic_payload_hash"):
            raise C2SError("E_IDEMPOTENCY_CONFLICT", "idempotency key conflicts during reconciliation")
        to_import.append(operation)

    for operation in to_import:
        append_jsonl(_operations_path(repo), operation)
    export(type("Args", (), {"repo": repo})())
    return {
        "ok": True,
        "schema_version": "c2s.reconciliation.replacement.v1",
        "operations_imported": len(to_import),
        "conflicts": [],
    }
