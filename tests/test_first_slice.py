import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import core
from c2s.cli import main


class FirstSliceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = core.Repo(self.root / ".c2s")
        self.note = self.root / "notes.md"
        self.note.write_text("Alpha claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        core.init_repo(self.repo)

    def test_init_creates_dedicated_repo_layout(self):
        self.assertTrue((self.root / ".c2s" / "project.json").exists())
        self.assertTrue((self.root / ".c2s" / "citation-history.jsonl").exists())
        self.assertTrue((self.root / ".c2s" / "handle-bindings.jsonl").exists())
        self.assertTrue((self.root / ".c2s" / "site" / "mkdocs.yml").exists())

    def test_cite_selection_does_not_rewrite_source_and_status_resolves(self):
        before = self.note.read_text(encoding="utf-8")
        result = core.cite_selection(args(self.repo, artifact="notes.md", start=0, end=11, handle="ALPHA"))
        self.assertTrue(result["ok"])
        self.assertEqual(before, self.note.read_text(encoding="utf-8"))
        projection = core.replay(self.repo)
        self.assertEqual(projection["citations"][0]["status"], "resolved")
        self.assertEqual(projection["citations"][0]["preferred_handle"], "ALPHA")

    def test_batch_all_or_nothing_rejects_without_partial_append(self):
        request = self.root / "batch.json"
        request.write_text(json.dumps({"items": [batch_item("ok", 0, 11), batch_item("bad", 999, 1000)]}), encoding="utf-8")
        result = core.cite_batch(ns(repo=str(self.repo.root), request=str(request), actor_kind="agent", actor_id="test-agent"))
        self.assertFalse(result["ok"])
        self.assertEqual([], result["created"])
        self.assertEqual([], core.replay(self.repo)["citations"])

    def test_batch_partial_appends_valid_items_and_reports_rejected_items(self):
        request = self.root / "batch.json"
        request.write_text(json.dumps({"mode": "partial", "items": [batch_item("ok", 0, 11, "ALPHA"), batch_item("bad", 999, 1000)]}), encoding="utf-8")
        result = core.cite_batch(ns(repo=str(self.repo.root), request=str(request), actor_kind="agent", actor_id="test-agent"))
        self.assertFalse(result["ok"])
        self.assertEqual(1, len(result["created"]))
        self.assertEqual(1, len(result["rejected"]))
        self.assertEqual("ALPHA", core.replay(self.repo)["citations"][0]["preferred_handle"])

    def test_set_handle_renames_without_changing_citation_id(self):
        citation_id = self.create_citation("ALPHA")
        result = core.set_handle(ns(repo=str(self.repo.root), citation_id=citation_id, handle="ALPHA-RENAMED", action="rename", previous_handle="ALPHA", actor_kind="user", actor_id=None))
        self.assertTrue(result["ok"])
        citation = core.replay(self.repo)["citations"][0]
        self.assertEqual(citation_id, citation["citation_id"])
        self.assertEqual("ALPHA-RENAMED", citation["preferred_handle"])
        self.assertIn("ALPHA", citation["aliases"])

    def test_lookup_actions_orders_overlapping_citations_deterministically(self):
        broad = self.create_citation("BROAD", start=0, end=22)
        narrow = self.create_citation("NARROW", start=0, end=11)
        result = core.lookup_actions(ns(repo=str(self.repo.root), artifact="notes.md", start=0, end=11, privacy="metadata_only"))
        self.assertTrue(result["requires_picker"])
        self.assertEqual(narrow, result["matches"][0]["citation_id"])
        self.assertEqual(broad, result["matches"][1]["citation_id"])

    def test_status_changes_when_artifact_changes(self):
        self.create_citation("ALPHA")
        self.note.write_text("Changed claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        self.assertEqual("changed", core.replay(self.repo)["citations"][0]["status"])

    def test_export_writes_metadata_only_json_and_mkdocs_files(self):
        self.create_citation("ALPHA")
        result = core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertTrue(result["ok"])
        self.assertTrue((self.repo.exports_dir / "c2s-status.json").exists())
        self.assertTrue((self.repo.exports_dir / "c2s-citations.jsonl").exists())
        self.assertTrue((self.repo.site_dir / "docs" / "index.md").exists())
        self.assertTrue((self.repo.site_dir / "docs" / "citations.md").exists())
        exported = json.loads((self.repo.exports_dir / "c2s-status.json").read_text(encoding="utf-8"))
        self.assertEqual("metadata_only", exported["privacy_mode"])

    def test_cli_errors_are_structured_json(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["--repo", str(self.repo.root), "cite-selection", "--artifact", "missing.md", "--start", "0", "--end", "1"])
        self.assertEqual(1, code)
        payload = json.loads(stderr.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual("E_ARTIFACT_MISSING", payload["error"]["code"])

    def test_cli_usage_errors_are_structured_json(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["--repo", str(self.repo.root), "cite-selection", "--artifact", "notes.md"])
        self.assertEqual(1, code)
        payload = json.loads(stderr.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual("E_USAGE", payload["error"]["code"])

    def create_citation(self, handle, start=0, end=11):
        return core.cite_selection(args(self.repo, artifact="notes.md", start=start, end=end, handle=handle))["citation_id"]


def ns(**kwargs):
    return type("Args", (), kwargs)()


def args(repo, **kwargs):
    defaults = {
        "repo": str(repo.root),
        "artifact": "notes.md",
        "adapter": "markdown",
        "start": 0,
        "end": 11,
        "expected_content_hash": None,
        "handle": None,
        "label": None,
        "tag": [],
        "note": None,
        "actor_kind": "user",
        "actor_id": None,
    }
    defaults.update(kwargs)
    return ns(**defaults)


def batch_item(client_item_id, start, end, handle=None):
    item = {"client_item_id": client_item_id, "artifact": {"adapter": "markdown", "uri": "notes.md"}, "locator": {"start": start, "end": end}}
    if handle:
        item["handle"] = handle
    return item


if __name__ == "__main__":
    unittest.main()
