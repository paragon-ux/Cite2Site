"""Replacement-protocol repository boundary checks.

This module is intentionally narrow: it detects archived v0.3/v1 repositories
and refuses them before any replacement replay or mutation code exists.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import C2SError

ARCHIVED_PROJECT_SCHEMAS = {"c2s.project.v0.3"}
REPLACEMENT_PROJECT_SCHEMA = "c2s.project.replacement.v1"


def _load_project_json(repo_dir: Path) -> dict[str, Any]:
    project = repo_dir / "project.json"
    try:
        data = json.loads(project.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise C2SError("E_REPO_NOT_INITIALIZED", "replacement repository is not initialized") from exc
    except json.JSONDecodeError as exc:
        raise C2SError("E_JSON_INVALID", "replacement repository project file is not valid JSON") from exc
    if not isinstance(data, dict):
        raise C2SError("E_JSON_INVALID", "replacement repository project file must be a JSON object")
    return data


def assert_replacement_repository(repo: str | Path) -> dict[str, Any]:
    """Return replacement project metadata or fail closed.

    Archived repositories are rejected before callers can replay, mutate,
    reconcile, project, or publish them as replacement authority.
    """
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
