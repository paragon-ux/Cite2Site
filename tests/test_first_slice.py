import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest import mock
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

    def test_replay_builds_deterministic_indexes_and_populates_artifact_cache(self):
        source_before = self.note.read_bytes()
        alpha = core.cite_selection(args(self.repo, start=0, end=11, handle="ALPHA", tag=["overview", "priority"]))["citation_id"]
        beta = core.cite_batch(
            ns(
                repo=str(self.repo.root),
                request=str(self.write_batch_request([batch_item("beta", 12, 22, "BETA", ["overview", "detail"])])),
                actor_kind="agent",
                actor_id="index-test",
            )
        )["created"][0]["citation_id"]
        core.set_handle(
            ns(
                repo=str(self.repo.root),
                citation_id=alpha,
                handle="ALPHA-RENAMED",
                action="rename",
                previous_handle="ALPHA",
                actor_kind="user",
                actor_id=None,
            )
        )

        first = core.replay(self.repo)
        second = core.replay(self.repo)
        self.assertEqual(first["indexes"], second["indexes"])
        self.assertEqual([alpha, beta], first["indexes"]["by_artifact"]["notes.md"]["citation_ids"])
        self.assertEqual([alpha], first["indexes"]["by_handle"]["ALPHA"]["citation_ids"])
        self.assertEqual([alpha], first["indexes"]["by_handle"]["ALPHA-RENAMED"]["citation_ids"])
        self.assertEqual([alpha, beta], first["indexes"]["by_tag"]["overview"]["citation_ids"])
        self.assertEqual([beta], first["indexes"]["by_tag"]["detail"]["citation_ids"])
        self.assertEqual([alpha, beta], first["indexes"]["by_status"]["resolved"]["citation_ids"])
        self.assertEqual(2, len(first["indexes"]["by_batch"]))
        self.assertEqual(source_before, self.note.read_bytes())

        cache_records = core.read_jsonl(self.repo.artifact_index)
        self.assertEqual(1, len(cache_records))
        self.assertEqual("notes.md", cache_records[0]["key"])
        self.assertEqual([alpha, beta], cache_records[0]["citation_ids"])
        self.assertEqual("artifact_index_snapshot", cache_records[0]["record_type"])

    def test_artifact_cache_is_not_replay_authority(self):
        citation_id = self.create_citation("ALPHA")
        expected = core.replay(self.repo)
        self.repo.artifact_index.unlink()
        actual = core.replay(self.repo)
        self.assertEqual(expected, actual)
        self.assertEqual(citation_id, actual["indexes"]["by_artifact"]["notes.md"]["citation_ids"][0])

    def test_cache_refresh_failure_does_not_fail_committed_citation(self):
        source_before = self.note.read_bytes()
        with mock.patch.object(core, "dump_jsonl_atomically", side_effect=OSError("disk full")):
            result = core.cite_selection(args(self.repo, handle="ALPHA"))
        self.assertTrue(result["ok"])
        self.assertFalse(result["artifact_index"]["refreshed"])
        self.assertEqual("E_ARTIFACT_INDEX_CACHE", result["artifact_index"]["error"]["code"])
        self.assertEqual(source_before, self.note.read_bytes())
        self.assertEqual(result["citation_id"], core.replay(self.repo)["citations"][0]["citation_id"])

    def test_citations_query_uses_indexes_and_preserves_metadata_only_view(self):
        alpha = core.cite_selection(args(self.repo, start=0, end=11, handle="ALPHA", tag=["overview"]))["citation_id"]
        batch = core.cite_batch(
            ns(
                repo=str(self.repo.root),
                request=str(self.write_batch_request([batch_item("beta", 12, 22, "BETA", ["detail"])])),
                actor_kind="agent",
                actor_id="query-test",
            )
        )
        beta = batch["created"][0]["citation_id"]
        core.set_handle(ns(repo=str(self.repo.root), citation_id=alpha, handle="ALPHA-RENAMED", action="rename", previous_handle="ALPHA", actor_kind="user", actor_id=None))

        self.assertEqual([alpha], query(self.repo, handle="ALPHA")["citations_ids"])
        self.assertEqual([alpha], query(self.repo, handle="ALPHA-RENAMED")["citations_ids"])
        self.assertEqual([alpha], query(self.repo, artifact="notes.md", tag="overview", status="resolved")["citations_ids"])
        self.assertEqual([beta], query(self.repo, tag="detail", batch=batch["batch_id"])["citations_ids"])
        response = query(self.repo, tag="overview")
        self.assertEqual({"tag": "overview"}, response["filters"])
        self.assertNotIn("accepted_evidence", response["citations"][0])
        self.assertNotIn("Alpha claim", json.dumps(response, sort_keys=True))

    def test_citations_cli_supports_jsonl_and_structured_invalid_filter_error(self):
        citation_id = self.create_citation("ALPHA")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--repo", str(self.repo.root), "citations", "--handle", "ALPHA", "--format", "jsonl"])
        self.assertEqual(0, code)
        records = [json.loads(line) for line in stdout.getvalue().splitlines() if line]
        self.assertEqual([citation_id], [record["citation_id"] for record in records])
        self.assertNotIn("accepted_evidence", records[0])

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["--repo", str(self.repo.root), "citations", "--status", "unknown"])
        self.assertEqual(1, code)
        self.assertEqual("E_USAGE", json.loads(stderr.getvalue())["error"]["code"])

    def test_export_writes_deterministic_grouped_indexes_and_site_pages(self):
        source_before = self.note.read_bytes()
        alpha = core.cite_selection(args(self.repo, start=0, end=11, handle="ALPHA", tag=["overview"]))["citation_id"]
        batch = core.cite_batch(ns(repo=str(self.repo.root), request=str(self.write_batch_request([batch_item("beta", 12, 22, "BETA", ["detail"])])), actor_kind="agent", actor_id="export-test"))
        beta = batch["created"][0]["citation_id"]
        core.set_handle(ns(repo=str(self.repo.root), citation_id=alpha, handle="ALPHA-RENAMED", action="rename", previous_handle="ALPHA", actor_kind="user", actor_id=None))

        first = core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        generated = [Path(path) for path in first["grouped_index_paths"].values()]
        self.assertEqual(
            {"index-by-artifact.json", "index-by-handle.json", "index-by-tag.json", "index-by-status.json", "index-by-batch.json"},
            {path.name for path in generated},
        )
        generated.extend(Path(path) for paths in first["grouped_site_paths"].values() for path in paths)
        self.assertTrue(all(path.exists() for path in generated))
        snapshot = {path: path.read_bytes() for path in generated}
        second = core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertEqual(first["grouped_index_paths"], second["grouped_index_paths"])
        self.assertEqual(snapshot, {path: path.read_bytes() for path in generated})
        self.assertEqual(source_before, self.note.read_bytes())

        nav = (self.repo.site_dir / "mkdocs.yml").read_text(encoding="utf-8")
        for directory in ["artifacts", "handles", "tags", "status", "batches"]:
            self.assertIn(f"{directory}/index.md", nav)
        pages = "\n".join(path.read_text(encoding="utf-8") for path in generated if path.suffix == ".md")
        self.assertIn(alpha, pages)
        self.assertIn(beta, pages)
        self.assertNotIn("Alpha claim", pages)

    def test_grouped_export_escapes_metadata_prunes_stale_pages_and_handles_slug_chains(self):
        unsafe_tag = "<script>alert(1)</script>"
        self.create_citation("ALPHA", start=0, end=11)
        core.cite_selection(args(self.repo, start=12, end=22, handle="BETA", tag=[unsafe_tag]))
        core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        tag_pages = "\n".join(path.read_text(encoding="utf-8") for path in (self.repo.site_dir / "docs" / "tags").glob("*.md"))
        self.assertNotIn("<script>", tag_pages)
        self.assertIn("&lt;script&gt;", tag_pages)

        suffix = core.sha256_bytes("a~".encode("utf-8")).removeprefix("sha256:")[:8]
        slugs = core.group_slugs({"a": {}, f"a-{suffix}": {}, "a~": {}})
        self.assertEqual(3, len(set(slugs.values())))

        resolved_page = self.repo.site_dir / "docs" / "status" / "resolved.md"
        self.assertTrue(resolved_page.exists())
        self.note.write_text("Changed claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertFalse(resolved_page.exists())
        self.assertTrue((self.repo.site_dir / "docs" / "status" / "changed.md").exists())

    def test_export_write_errors_are_structured(self):
        self.create_citation("ALPHA")
        with mock.patch.object(core, "write_grouped_json_exports", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(core.C2SError, "generated projection") as raised:
                core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertEqual("E_PROJECTION_WRITE", raised.exception.code)

    def test_privacy_modes_enforce_policy_and_keep_default_export_evidence_free(self):
        self.create_citation("ALPHA")
        metadata = core.replay(self.repo, "metadata_only")
        self.assertNotIn("accepted_evidence", metadata["citations"][0])
        self.assertNotIn("Alpha claim", json.dumps(metadata, sort_keys=True))
        hashed = core.replay(self.repo, "hash_only")
        self.assertIn("accepted_evidence", hashed["citations"][0])
        self.assertNotIn("text", hashed["citations"][0]["accepted_evidence"])

        with self.assertRaisesRegex(core.C2SError, "not authorized") as denied:
            core.replay(self.repo, "snippet")
        self.assertEqual("E_PRIVACY_POLICY", denied.exception.code)

        self.set_publication_policy(allow_snippet=True, allow_private_link=True, private_link_base="https://private.example/citations")
        snippet = core.replay(self.repo, "snippet")["citations"][0]
        self.assertEqual("Alpha claim", snippet["snippet"])
        self.assertNotIn("text", snippet["accepted_evidence"])
        private_link = core.replay(self.repo, "private_link")["citations"][0]
        self.assertEqual("https://private.example/citations/notes.md", private_link["private_link"])
        self.assertNotIn("accepted_evidence", private_link)

        self.set_publication_policy(private_link_base="javascript:alert(1)")
        with self.assertRaisesRegex(core.C2SError, "absolute HTTPS URL") as unsafe_base:
            core.replay(self.repo, "private_link")
        self.assertEqual("E_PRIVACY_POLICY", unsafe_base.exception.code)
        self.set_publication_policy(private_link_base="https://private.example/citations")
        traversal = {"artifact": {"uri": "../outside.md"}, "accepted_evidence": {"text": "private"}}
        core.apply_privacy(traversal, "private_link", core.publication_policy(self.repo))
        self.assertEqual("https://private.example/citations/..%2Foutside.md", traversal["private_link"])

        result = core.export(ns(repo=str(self.repo.root), privacy="metadata_only"))
        default_result = core.export(ns(repo=str(self.repo.root), privacy=None))
        self.assertEqual("metadata_only", default_result["privacy_mode"])
        generated = "\n".join(Path(path).read_text(encoding="utf-8") for path in [result["status_path"], result["citations_path"]])
        self.assertNotIn("Alpha claim", generated)

    def test_workflow_commands_are_append_only_and_first_line_handles_are_opt_in(self):
        source_before = self.note.read_bytes()
        citation_id = self.create_citation("ALPHA")
        history_before = len(core.read_jsonl(self.repo.citation_history))
        preflight = core.preflight_selection(args(self.repo, artifact="notes.md", start=0, end=11, handle=None, handle_from_first_line=False))
        self.assertEqual(citation_id, preflight["citation_id"])
        self.assertEqual(history_before, len(core.read_jsonl(self.repo.citation_history)))
        self.assertEqual(source_before, self.note.read_bytes())

        self.note.write_text("Updated claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        accepted = core.accept_current(ns(repo=str(self.repo.root), citation_id=citation_id, expected_content_hash=None, actor_kind="user", actor_id=None))
        self.assertIsNotNone(accepted["event_id"])
        self.assertEqual("resolved", core.replay(self.repo)["citations"][0]["status"])
        self.assertTrue(core.accept_current(ns(repo=str(self.repo.root), citation_id=citation_id, expected_content_hash=None, actor_kind="user", actor_id=None))["idempotent"])

        core.retract(ns(repo=str(self.repo.root), citation_id=citation_id, actor_kind="user", actor_id=None))
        self.assertEqual("retracted", core.replay(self.repo)["citations"][0]["status"])
        core.restore(ns(repo=str(self.repo.root), citation_id=citation_id, actor_kind="user", actor_id=None))
        self.assertEqual("active", core.replay(self.repo)["citations"][0]["state"])
        noted = core.note(ns(repo=str(self.repo.root), citation_id=citation_id, note="reviewed", actor_kind="user", actor_id=None))
        self.assertIsNotNone(noted["event_id"])
        self.assertEqual("reviewed", core.replay(self.repo)["citations"][0]["metadata"]["notes"][0]["text"])

        self.note.write_text("Prefix\nUpdated claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        relocated = core.relocate(ns(repo=str(self.repo.root), citation_id=citation_id, artifact=None, adapter=None, start=7, end=20, expected_content_hash=None, actor_kind="user", actor_id=None))
        self.assertIsNotNone(relocated["event_id"])
        self.assertEqual(7, core.replay(self.repo)["citations"][0]["locator"]["start"])

        self.note.write_text("FIRST-HANDLE\nBody claim\n", encoding="utf-8")
        first_line = core.cite_selection(args(self.repo, artifact="notes.md", start=0, end=24, handle=None, handle_from_first_line=True))
        cited = [citation for citation in core.replay(self.repo)["citations"] if citation["citation_id"] == first_line["citation_id"]][0]
        self.assertEqual("FIRST-HANDLE", cited["preferred_handle"])
        self.assertEqual("Body claim\n", core.read_jsonl(self.repo.citation_history)[-1]["accepted_evidence"]["text"])

    def test_unknown_authority_schema_refuses_without_rewrite(self):
        project = core.load_json(self.repo.project_file)
        project["schema_version"] = "foreign.project.v1"
        core.dump_json(self.repo.project_file, project)
        before = self.repo.project_file.read_bytes()
        with self.assertRaisesRegex(core.C2SError, "schema version") as raised:
            core.status(ns(repo=str(self.repo.root), privacy=None))
        self.assertEqual("E_SCHEMA_UNKNOWN", raised.exception.code)
        self.assertEqual(before, self.repo.project_file.read_bytes())

    def set_publication_policy(self, **values):
        project = core.load_json(self.repo.project_file)
        project["publication"].update(values)
        core.dump_json(self.repo.project_file, project)

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

    def write_batch_request(self, items):
        request = self.root / "batch.json"
        request.write_text(json.dumps({"items": items}), encoding="utf-8")
        return request


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


def batch_item(client_item_id, start, end, handle=None, tags=None):
    item = {"client_item_id": client_item_id, "artifact": {"adapter": "markdown", "uri": "notes.md"}, "locator": {"start": start, "end": end}}
    if handle:
        item["handle"] = handle
    if tags:
        item["tags"] = tags
    return item


def query(repo, **filters):
    defaults = {"repo": str(repo.root), "artifact": None, "handle": None, "tag": None, "status": None, "batch": None, "privacy": "metadata_only", "format": "json"}
    defaults.update(filters)
    response = core.citations(ns(**defaults))
    response["citations_ids"] = [citation["citation_id"] for citation in response["citations"]]
    return response


if __name__ == "__main__":
    unittest.main()
