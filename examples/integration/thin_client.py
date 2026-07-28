"""Thin replacement integration helper.

This example prepares replacement-native messages. It does not cache authority
or implement duplicate policy locally.
"""
from __future__ import annotations


def citation_create_message(
    *,
    repository: str,
    artifact: str,
    start: int,
    end: int,
    idempotency_key: str,
    group_id: str,
    handle_name: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact": artifact,
        "start": start,
        "end": end,
        "group_id": group_id,
    }
    if handle_name is not None:
        payload["handle_name"] = handle_name
    return {
        "schema_version": "c2s.integration.replacement.v1",
        "action": "citation.create",
        "repository": repository,
        "idempotency_key": idempotency_key,
        "payload": payload,
    }
