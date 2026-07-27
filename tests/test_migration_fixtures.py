"""Migration fixture tests for G8 — Release And Migration Hardening.

Tests that authority schema version validation, corrupt-file rejection,
and hash-chain integrity checks preserve authority files unchanged.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import core


class MigrationFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(self._rmtree)
        self.repo = core.Repo(self.tmp / ".c2s")
        core.init_repo(self.repo)
        self.note = self.tmp / "notes.md"
        self.note.write_text("Alpha claim\n", encoding="utf-8")
        core.cite_selection(_ns(
            repo=str(self.repo.root), artifact="notes.md", start=0, end=11,
            handle="ALPHA",
        ))

    def _rmtree(self):
        import shutil
        if self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    # -- schema version validation ----------------------------------------

    def _assert_no_path_leak(self, error: core.C2SError) -> None:
        """Error details must not expose resolved filesystem paths."""
        details_str = str(error.details)
        self.assertNotIn(str(self.repo.root.resolve()), details_str)
        self.assertNotIn(str(self.tmp.resolve()), details_str)

    def _assert_no_evidence_leak(self, error: core.C2SError) -> None:
        """Error messages must not contain cited evidence text."""
        self.assertNotIn("Alpha claim", error.message)
        self.assertNotIn("Alpha claim", str(error.details))

    def test_unknown_project_schema_refuses_without_rewrite(self):
        """Project with an unknown schema_version must be refused;
        authority files must remain byte-for-byte unchanged."""
        project = core.load_json(self.repo.project_file)
        project["schema_version"] = "foreign.project.v1"
        core.dump_json(self.repo.project_file, project)

        before_project = self.repo.project_file.read_bytes()
        before_cite = self.repo.citation_history.read_bytes()
        before_handle = self.repo.handle_bindings.read_bytes()

        with self.assertRaises(core.C2SError) as ctx:
            core.status(_ns(repo=str(self.repo.root), privacy=None))
        self.assertEqual("E_SCHEMA_UNKNOWN", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)

        self.assertEqual(before_project, self.repo.project_file.read_bytes())
        self.assertEqual(before_cite, self.repo.citation_history.read_bytes())
        self.assertEqual(before_handle, self.repo.handle_bindings.read_bytes())

    def test_unsupported_but_recognized_schema_refuses(self):
        """A schema starting with 'c2s.' but not matching current version
        must be refused with E_SCHEMA_UNSUPPORTED."""
        project = core.load_json(self.repo.project_file)
        project["schema_version"] = "c2s.project.v0.4"
        core.dump_json(self.repo.project_file, project)

        before = self.repo.project_file.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.status(_ns(repo=str(self.repo.root), privacy=None))
        self.assertEqual("E_SCHEMA_UNSUPPORTED", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.project_file.read_bytes())

    def test_unknown_event_schema_refuses_at_chain_validation(self):
        """An event with an unknown schema_version in the citation history
        must cause validate_chain to refuse."""
        events = core.read_jsonl(self.repo.citation_history)
        self.assertTrue(len(events) > 0)
        events[0]["schema_version"] = "foreign.event.v2"
        core.dump_jsonl_atomically(self.repo.citation_history, events)

        before = self.repo.citation_history.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.check(_ns(repo=str(self.repo.root)))
        self.assertEqual("E_SCHEMA_UNKNOWN", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.citation_history.read_bytes())

    # -- corrupt file rejection -------------------------------------------

    def test_corrupt_project_json_refuses(self):
        """A project.json that is not valid JSON must fail with E_JSON_INVALID."""
        self.repo.project_file.write_text("{ not json", encoding="utf-8")
        before = self.repo.project_file.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.status(_ns(repo=str(self.repo.root), privacy=None))
        self.assertEqual("E_JSON_INVALID", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.project_file.read_bytes())
        # Source artifact unchanged.
        self.assertEqual("Alpha claim\n", self.note.read_text(encoding="utf-8"))

    def test_corrupt_jsonl_record_refuses(self):
        """A JSONL line that is not valid JSON must fail with E_JSONL_INVALID."""
        events = core.read_jsonl(self.repo.citation_history)
        # Write the corrupt JSONL by hand.
        lines = [json.dumps(e, sort_keys=True, separators=(",", ":")) for e in events[:-1]]
        lines.append('{"bad": "json"')  # missing closing brace
        self.repo.citation_history.write_text("\n".join(lines) + "\n", encoding="utf-8")
        before = self.repo.citation_history.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.check(_ns(repo=str(self.repo.root)))
        self.assertEqual("E_JSONL_INVALID", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.citation_history.read_bytes())

    # -- hash chain integrity ---------------------------------------------

    def test_hash_chain_mismatch_refuses(self):
        """A tampered event in the chain must cause validate_chain to fail
        with E_EVENT_CHAIN, and no authority bytes are rewritten."""
        events = core.read_jsonl(self.repo.citation_history)
        self.assertTrue(len(events) >= 1)
        # Tamper the event payload without updating the hash.
        events[0]["artifact"]["uri"] = "tampered.md"
        core.dump_jsonl_atomically(self.repo.citation_history, events)
        before = self.repo.citation_history.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.check(_ns(repo=str(self.repo.root)))
        self.assertIn(ctx.exception.code, ("E_EVENT_HASH", "E_EVENT_CHAIN"))
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.citation_history.read_bytes())

    def test_missing_event_id_refuses(self):
        """An event without event_id must fail chain validation."""
        events = core.read_jsonl(self.repo.citation_history)
        events[0].pop("event_id", None)
        core.dump_jsonl_atomically(self.repo.citation_history, events)
        before = self.repo.citation_history.read_bytes()
        with self.assertRaises(core.C2SError) as ctx:
            core.check(_ns(repo=str(self.repo.root)))
        self.assertEqual("E_EVENT_ID_MISSING", ctx.exception.code)
        self._assert_no_path_leak(ctx.exception)
        self._assert_no_evidence_leak(ctx.exception)
        self.assertEqual(before, self.repo.citation_history.read_bytes())

    # -- source artifact preserved ----------------------------------------

    def test_refused_operations_preserve_source_artifact(self):
        """When any operation is refused, the cited artifact must remain unchanged."""
        before = self.note.read_bytes()
        # Corrupt project to trigger refusal.
        self.repo.project_file.write_text("garbage", encoding="utf-8")
        try:
            core.status(_ns(repo=str(self.repo.root), privacy=None))
        except core.C2SError:
            pass
        self.assertEqual(before, self.note.read_bytes())

    # -- exports are projections (can be regenerated) ----------------------

    def test_exports_are_replay_projections_not_authority(self):
        """Generated exports must be deletable and reproducible from authority."""
        core.export(_ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertTrue((self.repo.exports_dir / "c2s-status.json").exists())
        # Delete generated exports.
        import shutil
        shutil.rmtree(self.repo.exports_dir)
        shutil.rmtree(self.repo.site_dir)
        self.assertFalse(self.repo.exports_dir.exists())
        # Regenerate.
        core.export(_ns(repo=str(self.repo.root), privacy="metadata_only"))
        self.assertTrue((self.repo.exports_dir / "c2s-status.json").exists())


def _ns(**kwargs):
    return type("Args", (), kwargs)()


if __name__ == "__main__":
    unittest.main()
