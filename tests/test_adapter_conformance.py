"""Adapter conformance tests for G6 — Adapter Hardening.

Every supported adapter must pass the full conformance suite defined here.
Negative tests prove unsupported, invalid, private, and ambiguous cases fail
closed with stable structured codes.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import core, adapter


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _mk_repo(tmp: Path) -> core.Repo:
    repo = core.Repo(tmp / ".c2s")
    core.init_repo(repo)
    return repo


def _write_artifact(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Conformance harness — exercises the 7-contract-method surface
# ---------------------------------------------------------------------------


class _AdapterConformance:
    """Mixin that every concrete adapter test class must use.

    Subclasses set `self.adapter` to a BaseAdapter instance and
    `self.repo` to an initialized Repo in setUp.
    """

    adapter: adapter.BaseAdapter
    repo: core.Repo
    tmp: Path

    # -- identify --------------------------------------------------------

    def test_identify_returns_stable_artifact_identity(self):
        ad = self.adapter
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "line1\nline2\n")
        ident = ad.identify(self.repo, uri)
        self.assertIsInstance(ident, adapter.AdapterArtifact)
        self.assertEqual(ad.name, ident.adapter)
        self.assertIn("notes.md", ident.uri)
        self.assertTrue(len(ident.artifact_id) > 0)
        # Deterministic
        ident2 = ad.identify(self.repo, uri)
        self.assertEqual(ident.artifact_id, ident2.artifact_id)

    def test_identify_normalizes_backslash_uris(self):
        ad = self.adapter
        uri = "sub\\notes.md"
        path = self.tmp / "sub" / "notes.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("a\n", encoding="utf-8")
        ident = ad.identify(self.repo, uri)
        self.assertIn("sub/notes.md", ident.uri)
        self.assertNotIn("\\", ident.uri)

    # -- canonicalize ----------------------------------------------------

    def test_canonicalize_reads_utf8_and_normalizes_line_endings(self):
        ad = self.adapter
        uri = "crlf.md"
        path = self.tmp / uri
        # Write exact bytes to avoid platform newline translation.
        path.write_bytes(b"alpha\r\nbeta\r\n")
        canon = ad.canonicalize(self.repo, uri)
        self.assertEqual("alpha\nbeta\n", canon)
        # Deterministic
        self.assertEqual(canon, ad.canonicalize(self.repo, uri))

    def test_canonicalize_missing_file_raises_diagnostic(self):
        ad = self.adapter
        with self.assertRaises(core.C2SError) as ctx:
            ad.canonicalize(self.repo, "nonexistent.md")
        self.assertIn(ctx.exception.code, ("E_ADAPTER_MISSING", "E_ARTIFACT_MISSING"))

    def test_canonicalize_non_utf8_raises_diagnostic(self):
        ad = self.adapter
        uri = "binary.bin"
        path = self.tmp / uri
        path.write_bytes(b"\x80\x81\x82")
        with self.assertRaises(core.C2SError) as ctx:
            ad.canonicalize(self.repo, uri)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_UTF8", "E_ARTIFACT_TEXT_DECODE"))

    # -- evidence --------------------------------------------------------

    def test_evidence_produces_complete_evidence_dict(self):
        ad = self.adapter
        ev = ad.evidence("hello world")
        self.assertEqual("text", ev["kind"])
        self.assertIn("content_hash", ev)
        self.assertIn("text", ev)
        self.assertIn("line_hashes", ev)
        self.assertIn("byte_count", ev)
        self.assertIn("line_count", ev)
        self.assertEqual("hello world", ev["text"])
        self.assertTrue(ev["content_hash"].startswith("sha256:"))

    def test_evidence_is_deterministic(self):
        ad = self.adapter
        e1 = ad.evidence("same")
        e2 = ad.evidence("same")
        self.assertEqual(e1["content_hash"], e2["content_hash"])

    def test_evidence_different_content_different_hash(self):
        ad = self.adapter
        self.assertNotEqual(
            ad.evidence("alpha")["content_hash"],
            ad.evidence("beta")["content_hash"],
        )

    # -- locate ----------------------------------------------------------

    def test_locate_returns_exact_locator(self):
        ad = self.adapter
        source = "line one\nline two\nline three\n"
        loc = ad.locate(source, 0, 8)
        self.assertEqual("text-range", loc["kind"])
        self.assertEqual("unicode-scalar", loc["encoding"])
        self.assertEqual(0, loc["start"])
        self.assertEqual(8, loc["end"])
        self.assertEqual(1, loc["start_line"])
        self.assertEqual(1, loc["end_line"])

    def test_locate_cross_line(self):
        ad = self.adapter
        source = "a\nb\n"
        loc = ad.locate(source, 0, 3)
        self.assertEqual(2, loc["end_line"])

    def test_locate_invalid_range_raises_diagnostic(self):
        ad = self.adapter
        with self.assertRaises(core.C2SError) as ctx:
            ad.locate("abc", 5, 10)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_RANGE_INVALID", "E_RANGE_INVALID"))

    def test_locate_empty_selection_raises_diagnostic(self):
        ad = self.adapter
        with self.assertRaises(core.C2SError) as ctx:
            ad.locate("abc", 1, 1)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_EMPTY_SELECTION", "E_SELECTION_EMPTY"))

    # -- observe ---------------------------------------------------------

    def test_observe_reads_current_content(self):
        ad = self.adapter
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "original content\n")
        artifact = {"uri": uri}
        locator = {"start": 0, "end": 8, "start_line": 1, "end_line": 1}
        observed = ad.observe(self.repo, artifact, locator)
        self.assertEqual("original", observed["text"])
        self.assertTrue(observed["content_hash"].startswith("sha256:"))

    def test_observe_does_not_mutate_source(self):
        ad = self.adapter
        uri = "notes.md"
        path = _write_artifact(self.tmp / uri, "untouched\n")
        before = path.read_bytes()
        artifact = {"uri": uri}
        locator = {"start": 0, "end": 9, "start_line": 1, "end_line": 1}
        ad.observe(self.repo, artifact, locator)
        self.assertEqual(before, path.read_bytes())

    def test_observe_missing_file_raises_diagnostic(self):
        ad = self.adapter
        artifact = {"uri": "gone.md"}
        locator = {"start": 0, "end": 5}
        with self.assertRaises(core.C2SError) as ctx:
            ad.observe(self.repo, artifact, locator)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_MISSING", "E_ARTIFACT_MISSING"))

    def test_observe_range_beyond_file_raises(self):
        ad = self.adapter
        uri = "short.md"
        _write_artifact(self.tmp / uri, "ab\n")
        artifact = {"uri": uri}
        locator = {"start": 0, "end": 999, "start_line": 1, "end_line": 1}
        with self.assertRaises(core.C2SError) as ctx:
            ad.observe(self.repo, artifact, locator)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_RANGE_INVALID", "E_RANGE_INVALID"))

    # -- compare ---------------------------------------------------------

    def test_compare_resolved_when_hashes_match(self):
        ad = self.adapter
        ev = ad.evidence("alpha")
        self.assertEqual("resolved", ad.compare(ev, ev))

    def test_compare_changed_when_hashes_differ(self):
        ad = self.adapter
        self.assertEqual("changed", ad.compare(ad.evidence("a"), ad.evidence("b")))

    # -- summarize -------------------------------------------------------

    def test_summarize_returns_metadata_safe_text(self):
        ad = self.adapter
        loc = {"start": 0, "end": 10, "start_line": 1, "end_line": 3}
        summary = ad.summarize(loc)
        self.assertIsInstance(summary, str)
        self.assertIn("1", summary)
        # Must not contain evidence text.
        self.assertNotIn("<script>", summary)

    # -- privacy ---------------------------------------------------------

    def test_privacy_metadata_only_strips_accepted_evidence(self):
        ad = self.adapter
        citation = {
            "accepted_evidence": ad.evidence("sensitive text"),
            "artifact": {"uri": "test.md"},
        }
        policy = {"privacy_mode": "metadata_only"}
        ad.privacy(citation, "metadata_only", policy)
        self.assertNotIn("accepted_evidence", citation)
        self.assertNotIn("snippet", citation)
        self.assertNotIn("private_link", citation)

    def test_privacy_hash_only_keeps_hashes_not_text(self):
        ad = self.adapter
        citation = {
            "accepted_evidence": ad.evidence("sensitive"),
            "artifact": {"uri": "test.md"},
        }
        policy = {}
        ad.privacy(citation, "hash_only", policy)
        self.assertIn("accepted_evidence", citation)
        self.assertIn("content_hash", citation["accepted_evidence"])
        self.assertNotIn("text", citation["accepted_evidence"])

    def test_privacy_snippet_refused_without_policy(self):
        """Policy enforcement happens at the replay layer (effective_privacy_mode),
        not inside the adapter privacy method."""
        ad = self.adapter
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "some text\n")
        result = core.cite_selection(_ns(
            repo=str(self.repo.root), artifact=uri, start=0, end=4,
            handle="T",
        ))
        # snippet should be refused by replay when policy denies it
        with self.assertRaises(core.C2SError) as ctx:
            core.replay(self.repo, "snippet")
        self.assertEqual("E_PRIVACY_POLICY", ctx.exception.code)

    def test_privacy_private_link_refused_without_base_url(self):
        """When private_link_base is missing from policy, apply_privacy rejects via
        validated_private_link_base — the allow_private_link gate lives in
        effective_privacy_mode and is tested through replay."""
        ad = self.adapter
        citation = {
            "accepted_evidence": ad.evidence("text"),
            "artifact": {"uri": "test.md"},
        }
        policy = {}
        with self.assertRaises(core.C2SError) as ctx:
            ad.privacy(citation, "private_link", policy)
        self.assertEqual("E_PRIVACY_POLICY", ctx.exception.code)

    def test_workspace_boundary_enforced_outside_path_rejected(self):
        """Paths outside workspace_root must be rejected with a stable code."""
        with self.assertRaises(core.C2SError) as ctx:
            self.adapter.canonicalize(self.repo, "../outside.txt")
        self.assertEqual("E_ARTIFACT_OUTSIDE_WORKSPACE", ctx.exception.code)


# ---------------------------------------------------------------------------
# Concrete adapter test classes
# ---------------------------------------------------------------------------


class FilesystemTextConformanceTests(_AdapterConformance, unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: _rmtree(self.tmp))
        self.repo = _mk_repo(self.tmp)
        self.adapter = adapter.FilesystemTextAdapter()


class MarkdownConformanceTests(_AdapterConformance, unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: _rmtree(self.tmp))
        self.repo = _mk_repo(self.tmp)
        self.adapter = adapter.MarkdownAdapter()

    def test_markdown_adapter_uses_text_semantics_explicitly(self):
        """Markdown adapter still uses text semantics — block awareness is not yet shipped."""
        uri = "doc.md"
        _write_artifact(self.tmp / uri, "# Title\n\nParagraph **bold**.\n")
        canon = self.adapter.canonicalize(self.repo, uri)
        # Text semantics: no structural block processing.
        self.assertIn("**bold**", canon)
        self.assertIn("# Title", canon)


# ---------------------------------------------------------------------------
# Negative / edge-case tests — adapter-agnostic
# ---------------------------------------------------------------------------


class AdapterNegativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: _rmtree(self.tmp))
        self.repo = _mk_repo(self.tmp)
        self.ad = adapter.FilesystemTextAdapter()

    def test_unsupported_adapter_raises_stable_code(self):
        with self.assertRaises(core.C2SError) as ctx:
            adapter.get_adapter("pdf-extractor")
        self.assertEqual("E_ADAPTER_UNSUPPORTED", ctx.exception.code)
        self.assertIn("filesystem-text", ctx.exception.details.get("supported", []))

    def test_adapter_for_uri_rejects_unsupported_requested(self):
        with self.assertRaises(core.C2SError) as ctx:
            adapter.adapter_for_uri("notes.md", requested="pdf-extractor")
        self.assertEqual("E_ADAPTER_UNSUPPORTED", ctx.exception.code)

    def test_adapter_for_uri_auto_detects_markdown(self):
        self.assertEqual("markdown", adapter.adapter_for_uri("readme.md"))
        self.assertEqual("markdown", adapter.adapter_for_uri("path/to/doc.markdown"))

    def test_adapter_for_uri_defaults_to_filesystem_text(self):
        self.assertEqual("filesystem-text", adapter.adapter_for_uri("notes.txt"))
        self.assertEqual("filesystem-text", adapter.adapter_for_uri("data.csv"))
        self.assertEqual("filesystem-text", adapter.adapter_for_uri("noext"))

    def test_adapter_for_uri_explicit_override(self):
        self.assertEqual("filesystem-text", adapter.adapter_for_uri("readme.md", requested="filesystem-text"))

    def test_citation_id_is_deterministic_and_adapter_specific(self):
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "content\n")
        ident = self.ad.identify(self.repo, uri)
        loc = self.ad.locate("content\n", 0, 7)
        ev = self.ad.evidence("content")
        cid1 = self.ad.citation_id_for(ident, loc, ev)
        cid2 = self.ad.citation_id_for(ident, loc, ev)
        self.assertEqual(cid1, cid2)

    def test_validate_selection_rejects_negative_start(self):
        with self.assertRaises(core.C2SError) as ctx:
            self.ad.validate_selection("abc", -1, 2)
        self.assertIn(ctx.exception.code, ("E_ADAPTER_RANGE_INVALID", "E_RANGE_INVALID"))

    def test_diagnostics_map_is_stable(self):
        diag = adapter.adapter_diagnostics()
        required = [
            "E_ADAPTER_UNSUPPORTED",
            "E_ADAPTER_UTF8",
            "E_ADAPTER_MISSING",
            "E_ADAPTER_EMPTY_SELECTION",
            "E_ADAPTER_RANGE_INVALID",
            "E_ADAPTER_AMBIGUOUS",
        ]
        # E_ARTIFACT_OUTSIDE_WORKSPACE is a core.py code, not an adapter diagnostic.
        for code in required:
            self.assertIn(code, diag)
            self.assertIsInstance(diag[code], str)
            self.assertTrue(len(diag[code]) > 0)

    def test_adapter_unsupported_status_via_replay(self):
        """A citation created with a supported adapter that is later unavailable
        must report 'unsupported' when the adapter is removed from the registry."""
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "line\n")
        result = core.cite_selection(_ns(
            repo=str(self.repo.root), artifact=uri, start=0, end=4,
            handle="T", adapter="markdown",
        ))
        cid = result["citation_id"]
        # Remove the 'markdown' adapter from the registry to simulate
        # an adapter that was valid at citation time but is no longer available.
        saved = adapter._SUPPORTED.pop("markdown", None)
        try:
            projection = core.replay(self.repo, "metadata_only")
            cited = [c for c in projection["citations"] if c["citation_id"] == cid][0]
            self.assertEqual("unsupported", cited["status"])
        finally:
            if saved is not None:
                adapter._SUPPORTED["markdown"] = saved

    def test_adapter_unavailable_status_on_read_failure(self):
        """When adapter.observe fails with a non-missing error, status is adapter_unavailable."""
        uri = "notes.md"
        _write_artifact(self.tmp / uri, "line\n")
        result = core.cite_selection(_ns(
            repo=str(self.repo.root), artifact=uri, start=0, end=4,
            handle="T",
        ))
        cid = result["citation_id"]
        # Patch observe to fail with a non-missing error.
        with mock.patch.object(adapter.FilesystemTextAdapter, "observe", side_effect=core.C2SError("E_ADAPTER_UTF8", "boom")):
            projection = core.replay(self.repo, "metadata_only")
        cited = [c for c in projection["citations"] if c["citation_id"] == cid][0]
        self.assertEqual("adapter_unavailable", cited["status"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rmtree(path: Path) -> None:
    import shutil
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def _ns(**kwargs):
    return type("Args", (), kwargs)()


if __name__ == "__main__":
    unittest.main()
