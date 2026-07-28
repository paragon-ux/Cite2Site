from __future__ import annotations

from pathlib import Path

from .core import C2SError, sha256_bytes

TEXT_CANON = "text-utf8-lf-v1"


def read_text_artifact(artifact: str) -> str:
    path = Path(artifact)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise C2SError("E_ARTIFACT_MISSING", "artifact file does not exist", artifact=artifact) from exc
    except UnicodeDecodeError as exc:
        raise C2SError("E_ARTIFACT_UTF8", "artifact is not valid UTF-8 text", artifact=artifact) from exc


def select_text(source: str, start: int, end: int) -> str:
    if start < 0 or end < start or end > len(source):
        raise C2SError("E_RANGE_INVALID", "selection range is outside artifact bounds", start=start, end=end, length=len(source))
    selected = source[start:end]
    if selected == "":
        raise C2SError("E_EMPTY_SELECTION", "selection captured zero characters", start=start, end=end)
    return selected


def evidence_hash(selected: str) -> str:
    return sha256_bytes(selected.encode("utf-8"))
