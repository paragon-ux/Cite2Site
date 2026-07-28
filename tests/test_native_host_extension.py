from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import native_host


class NativeHostExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / ".c2s"
        self.repo.mkdir()

    def test_lookup_file_selection_sanitizes_persisted_filename(self):
        calls = []

        def fake_run(repo_dir, arguments, timeout=30):
            calls.append((repo_dir, arguments, timeout))
            return {"ok": True, "matches": []}

        message = {
            "action": "lookup-file-selection",
            "file": {"name": "..\\..\\outside.md", "content": "Alpha claim\n"},
            "start": 0,
            "end": 5,
        }
        with mock.patch.object(native_host, "_load_repo_dir", return_value=self.repo):
            with mock.patch.object(native_host, "_run_c2s", side_effect=fake_run):
                result = native_host.dispatch(message)

        self.assertTrue(result["ok"])
        file_hash = hashlib.sha256("Alpha claim\n".encode()).hexdigest()
        captured = self.repo / "captured" / "files" / file_hash / "outside.md"
        self.assertEqual("Alpha claim\n", captured.read_text(encoding="utf-8"))
        self.assertEqual(str(captured), calls[0][1][2])
        self.assertFalse((self.repo / "captured" / "outside.md").exists())
        self.assertEqual("1.0", result["protocol_version"])

    def test_cite_file_selection_export_failure_preserves_citation_result(self):
        selected = "Alpha"
        message = {
            "action": "cite-file-selection",
            "file": {"name": "../notes.md", "content": "Alpha claim\n"},
            "selection": {
                "start": 0,
                "end": len(selected),
                "selectedText": selected,
                "contentHash": native_host._content_hash(selected),
            },
        }
        side_effects = [
            {"ok": True, "citation_id": "sha256:test"},
            {"ok": False, "error": {"code": "E_PROJECTION_WRITE", "message": "disk full"}},
        ]

        with mock.patch.object(native_host, "_load_repo_dir", return_value=self.repo):
            with mock.patch.object(native_host, "_run_c2s", side_effect=side_effects):
                result = native_host.dispatch(message)

        self.assertFalse(result["ok"])
        self.assertEqual("E_EXTENSION_EXPORT", result["error"]["code"])
        self.assertEqual({"ok": True, "citation_id": "sha256:test"}, result["citation"])
        file_hash = hashlib.sha256("Alpha claim\n".encode()).hexdigest()
        self.assertTrue((self.repo / "captured" / "files" / file_hash / "notes.md").is_file())

    def test_mutation_export_failure_preserves_mutation_result(self):
        side_effects = [
            {"ok": True, "event_id": "event-1"},
            {"ok": False, "error": {"code": "E_PROJECTION_WRITE", "message": "disk full"}},
        ]

        with mock.patch.object(native_host, "_run_c2s", side_effect=side_effects):
            result = native_host._mutate(self.repo, "retract", "sha256:test")

        self.assertFalse(result["ok"])
        self.assertEqual("E_EXTENSION_EXPORT", result["error"]["code"])
        self.assertEqual({"ok": True, "event_id": "event-1"}, result["mutation"])

    def test_dispatch_normalizes_missing_config_for_mutation_handlers(self):
        with mock.patch.object(native_host, "_load_repo_dir", side_effect=RuntimeError("missing config")):
            result = native_host.dispatch({"action": "retract", "citation_id": "sha256:test"})

        self.assertFalse(result["ok"])
        self.assertEqual("E_EXTENSION_CONFIG", result["error"]["code"])
        self.assertEqual("1.0", result["protocol_version"])


if __name__ == "__main__":
    unittest.main()
