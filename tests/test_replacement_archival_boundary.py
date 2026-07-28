from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import replacement
from c2s.core import C2SError


class ReplacementArchivalBoundaryTests(unittest.TestCase):
    def test_v03_repository_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp_value:
            repo = Path(tmp_value) / ".c2s"
            repo.mkdir()
            (repo / "project.json").write_text(
                json.dumps({"schema_version": "c2s.project.v0.3", "repository_id": "old"}),
                encoding="utf-8",
            )
            (repo / "citation-history.jsonl").write_text("", encoding="utf-8")
            (repo / "handle-bindings.jsonl").write_text("", encoding="utf-8")
            before = {path.name: path.read_bytes() for path in repo.iterdir()}

            with self.assertRaises(C2SError) as raised:
                replacement.assert_replacement_repository(repo)

            self.assertEqual("E_ARCHIVED_PROTOCOL_UNSUPPORTED", raised.exception.code)
            self.assertEqual(before, {path.name: path.read_bytes() for path in repo.iterdir()})

    def test_replacement_repository_metadata_loads(self):
        with tempfile.TemporaryDirectory() as tmp_value:
            repo = Path(tmp_value) / ".c2s"
            repo.mkdir()
            expected = {
                "schema_version": replacement.REPLACEMENT_PROJECT_SCHEMA,
                "repository_id": "replacement",
            }
            (repo / "project.json").write_text(json.dumps(expected), encoding="utf-8")

            self.assertEqual(expected, replacement.assert_replacement_repository(repo))


if __name__ == "__main__":
    unittest.main()
