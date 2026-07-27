from __future__ import annotations

import abc
import dataclasses
from pathlib import Path
from typing import Any

from .core import (
    C2SError,
    Repo,
    canonical_text,
    evidence_for_text,
    line_hashes,
    line_number_at,
    make_locator,
    normalize_uri,
    resolve_artifact_path,
    sha256_json,
    TEXT_CANON,
)

# ---------------------------------------------------------------------------
# Adapter diagnostics — stable structured codes for adapter-level failures
# ---------------------------------------------------------------------------

_ADAPTER_DIAGNOSTICS = {
    "E_ADAPTER_UNSUPPORTED": "the requested adapter is not installed or recognized",
    "E_ADAPTER_UTF8": "artifact content is not valid UTF-8 text",
    "E_ADAPTER_MISSING": "artifact file does not exist at the resolved path",
    "E_ADAPTER_EMPTY_SELECTION": "selection range captured zero characters",
    "E_ADAPTER_RANGE_INVALID": "selection range is outside artifact bounds",
    "E_ADAPTER_AMBIGUOUS": "adapter cannot resolve a single authoritative evidence",
}

# ---------------------------------------------------------------------------
# Adapter contract types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AdapterArtifact:
    """Stable artifact identity produced by an adapter."""

    adapter: str
    uri: str
    artifact_id: str


# ---------------------------------------------------------------------------
# Abstract adapter protocol
# ---------------------------------------------------------------------------


class BaseAdapter(abc.ABC):
    """Protocol every Cite2Site adapter must fulfil.

    Concrete adapters implement eight contract methods:
      identify    – stable artifact identity
      canonicalize – read artifact and return canonical text
      evidence    – produce canonical evidence from selected text
      locate      – produce unambiguous locator coordinates
      observe     – read current artifact bytes at a locator (no mutation)
      compare     – deterministic resolved/changed status
      summarize   – metadata-safe human-readable range summary
      privacy     – comply with the active publication privacy mode
    """

    # Subclasses override this.
    name: str = "base"

    # ------------------------------------------------------------------
    # Contract methods (must be implemented)
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def identify(self, repo: Repo, uri: str) -> AdapterArtifact:
        """Return stable artifact identity for *uri*."""

    @abc.abstractmethod
    def canonicalize(self, repo: Repo, uri: str) -> str:
        """Read artifact and return canonical text.

        Raises structured C2SError with an adapter-level diagnostic on failure.
        """

    @abc.abstractmethod
    def evidence(self, selected_text: str) -> dict[str, Any]:
        """Produce canonical evidence dict for *selected_text*."""

    @abc.abstractmethod
    def locate(self, source_text: str, start: int, end: int) -> dict[str, Any]:
        """Produce an unambiguous locator from *start*/*end* scalar offsets."""

    @abc.abstractmethod
    def observe(self, repo: Repo, artifact: dict[str, Any], locator: dict[str, Any]) -> dict[str, Any]:
        """Read current artifact content at *locator* without mutation.

        Returns an evidence dict for the currently observed selection.
        """

    @abc.abstractmethod
    def compare(self, accepted_evidence: dict[str, Any], observed_evidence: dict[str, Any]) -> str:
        """Return 'resolved' or 'changed'.  'missing' and 'unsupported' are
        determined externally by core.observe_status()."""

    @abc.abstractmethod
    def summarize(self, locator: dict[str, Any]) -> str:
        """Return a metadata-safe human-readable range summary."""

    @abc.abstractmethod
    def privacy(self, citation: dict[str, Any], mode: str, policy: dict[str, Any]) -> None:
        """Mutate *citation* in-place to comply with *mode*/*policy*.

        The default implementation delegates to the core apply_privacy,
        which is adapter-agnostic.  Adapters that need specialised
        redaction (e.g. stripping structured fields) override this.
        """

    # ------------------------------------------------------------------
    # Derived helpers (not part of the conformance surface)
    # ------------------------------------------------------------------

    def citation_id_for(self, artifact: AdapterArtifact, locator: dict[str, Any], evidence: dict[str, Any]) -> str:
        return sha256_json(
            {
                "kind": "c2s.citation",
                "artifact": {"adapter": artifact.adapter, "uri": artifact.uri, "artifact_id": artifact.artifact_id},
                "locator": locator,
                "accepted_evidence_hash": evidence["content_hash"],
            }
        )

    def validate_selection(self, source_text: str, start: int, end: int) -> str:
        """Return the selected text, or raise a structured diagnostic."""
        if start < 0 or end < start or end > len(source_text):
            raise C2SError(
                "E_ADAPTER_RANGE_INVALID",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_RANGE_INVALID"],
                start=start,
                end=end,
                length=len(source_text),
            )
        selected = source_text[start:end]
        if selected == "":
            raise C2SError(
                "E_ADAPTER_EMPTY_SELECTION",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_EMPTY_SELECTION"],
                start=start,
                end=end,
            )
        return selected


# ---------------------------------------------------------------------------
# Filesystem text adapter — the canonical plain-text adapter
# ---------------------------------------------------------------------------


class FilesystemTextAdapter(BaseAdapter):
    """Plain-text filesystem adapter (UTF-8, LF-normalised)."""

    name = "filesystem-text"

    # -- contract -------------------------------------------------------

    def identify(self, repo: Repo, uri: str) -> AdapterArtifact:
        path = resolve_artifact_path(repo, uri)
        identity = {"adapter": self.name, "uri": normalize_uri(uri), "path": str(path)}
        return AdapterArtifact(adapter=self.name, uri=normalize_uri(uri), artifact_id=sha256_json(identity))

    def canonicalize(self, repo: Repo, uri: str) -> str:
        path = resolve_artifact_path(repo, uri)
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise C2SError(
                "E_ADAPTER_MISSING",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_MISSING"],
                artifact=uri,
            ) from exc
        except UnicodeDecodeError as exc:
            raise C2SError(
                "E_ADAPTER_UTF8",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_UTF8"],
                artifact=uri,
            ) from exc
        return canonical_text(raw)

    def evidence(self, selected_text: str) -> dict[str, Any]:
        return evidence_for_text(selected_text)

    def locate(self, source_text: str, start: int, end: int) -> dict[str, Any]:
        selected = self.validate_selection(source_text, start, end)
        return make_locator(source_text, start, end)

    def observe(self, repo: Repo, artifact: dict[str, Any], locator: dict[str, Any]) -> dict[str, Any]:
        uri = str(artifact["uri"])
        source = self.canonicalize(repo, uri)
        start, end = int(locator["start"]), int(locator["end"])
        if end > len(source):
            raise C2SError(
                "E_ADAPTER_RANGE_INVALID",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_RANGE_INVALID"],
                artifact=uri,
                start=start,
                end=end,
                length=len(source),
            )
        selected = source[start:end]
        if selected == "":
            raise C2SError(
                "E_ADAPTER_EMPTY_SELECTION",
                _ADAPTER_DIAGNOSTICS["E_ADAPTER_EMPTY_SELECTION"],
                artifact=uri,
                start=start,
                end=end,
            )
        return self.evidence(selected)

    def compare(self, accepted_evidence: dict[str, Any], observed_evidence: dict[str, Any]) -> str:
        if accepted_evidence["content_hash"] == observed_evidence["content_hash"]:
            return "resolved"
        return "changed"

    def summarize(self, locator: dict[str, Any]) -> str:
        if "start_line" in locator and "end_line" in locator:
            return f"lines {locator['start_line']}-{locator['end_line']}"
        return f"{locator['start']}-{locator['end']}"

    def privacy(self, citation: dict[str, Any], mode: str, policy: dict[str, Any]) -> None:
        # Delegate to core.apply_privacy — adapter-agnostic transform.
        from .core import apply_privacy as _apply_privacy

        _apply_privacy(citation, mode, policy)


# ---------------------------------------------------------------------------
# Markdown adapter — text semantics with explicit Markdown awareness marker
# ---------------------------------------------------------------------------


class MarkdownAdapter(FilesystemTextAdapter):
    """Markdown adapter using text-line semantics.

    Block-aware locators, summaries, and observation are not yet
    implemented.  This adapter intentionally inherits the plain-text
    contract until the block-level spec and test suite are delivered.
    """

    name = "markdown"


# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------

_SUPPORTED: dict[str, BaseAdapter] = {
    "filesystem-text": FilesystemTextAdapter(),
    "markdown": MarkdownAdapter(),
}


def get_adapter(name: str) -> BaseAdapter:
    """Return the adapter instance for *name*.

    Raises E_ADAPTER_UNSUPPORTED when *name* is not a supported adapter.
    """
    if name not in _SUPPORTED:
        raise C2SError(
            "E_ADAPTER_UNSUPPORTED",
            _ADAPTER_DIAGNOSTICS["E_ADAPTER_UNSUPPORTED"],
            adapter=name,
            supported=sorted(_SUPPORTED.keys()),
        )
    return _SUPPORTED[name]


def adapter_for_uri(uri: str, requested: str | None = None) -> str:
    """Resolve the adapter name for *uri*, optionally overriding with *requested*."""
    if requested:
        get_adapter(requested)  # validates
        return requested
    return "markdown" if uri.lower().endswith((".md", ".markdown")) else "filesystem-text"


def adapter_diagnostics() -> dict[str, str]:
    """Return the stable adapter diagnostic code→message map (for docs/tests)."""
    return dict(_ADAPTER_DIAGNOSTICS)
