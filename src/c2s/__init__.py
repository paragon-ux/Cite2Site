"""Cite2Site first-slice implementation."""

__all__ = [
    "__version__",
    "BaseAdapter",
    "FilesystemTextAdapter",
    "MarkdownAdapter",
    "AdapterArtifact",
    "get_adapter",
    "adapter_for_uri",
    "adapter_diagnostics",
]

__version__ = "1.0.4"

from .adapter import (  # noqa: E402  — re-export after version
    AdapterArtifact,
    BaseAdapter,
    FilesystemTextAdapter,
    MarkdownAdapter,
    adapter_diagnostics,
    adapter_for_uri,
    get_adapter,
)
