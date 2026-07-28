from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import native_host, replacement
from c2s.core import C2SError


class ReplacementRuntimeTests(unittest.TestCase):
    def test_init_creates_replacement_repository_and_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / ".c2s"
            result = replacement.init_repo(repo, idempotency_key="init-1")

            self.assertTrue(result["ok"])
            project = json.loads((repo / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(replacement.REPLACEMENT_PROJECT_SCHEMA, project["schema_version"])
            operations = (repo / "operations.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(operations))
            self.assertIn("group.created", operations[0])

    def test_duplicate_evidence_creates_distinct_citations_and_scoped_supersession(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / ".c2s"
            artifact = root / "notes.md"
            artifact.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
            before = artifact.read_bytes()
            replacement.init_repo(repo, idempotency_key="init-1")

            base = {
                "repo": repo,
                "artifact": str(artifact),
                "start": 0,
                "end": 11,
                "handle": "ALPHA",
                "handle_id": None,
                "group_id": None,
            }
            first = replacement.cite_selection(SimpleNamespace(**base, idempotency_key="cite-1"))
            second = replacement.cite_selection(SimpleNamespace(**base, idempotency_key="cite-2"))
            replayed = replacement.cite_selection(SimpleNamespace(**base, idempotency_key="cite-1"))
            state = replacement.replay(repo)

            self.assertNotEqual(first["citation_id"], second["citation_id"])
            self.assertEqual(first["citation_id"], replayed["citation_id"])
            self.assertTrue(replayed["idempotent_replay"])
            self.assertEqual(before, artifact.read_bytes())
            handle = next(iter(state["handles"].values()))
            self.assertEqual(2, len(handle["tally"]))
            self.assertEqual(2, len(next(iter(state["groups"].values()))["tally"]))
            self.assertGreaterEqual(len(state["supersessions"]), 1)
            self.assertEqual({"handle"}, {item["scope"] for item in state["supersessions"]})

    def test_idempotency_conflict_rejects_different_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / ".c2s"
            artifact = root / "notes.md"
            artifact.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
            replacement.init_repo(repo, idempotency_key="init-1")

            replacement.cite_selection(
                SimpleNamespace(repo=repo, artifact=str(artifact), start=0, end=11, handle="ALPHA", handle_id=None, group_id=None, idempotency_key="same")
            )
            with self.assertRaises(C2SError) as raised:
                replacement.cite_selection(
                    SimpleNamespace(repo=repo, artifact=str(artifact), start=12, end=22, handle="ALPHA", handle_id=None, group_id=None, idempotency_key="same")
                )
            self.assertEqual("E_IDEMPOTENCY_CONFLICT", raised.exception.code)

    def test_cli_smoke_replacement_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / ".c2s"
            artifact = root / "notes.md"
            artifact.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
            commands = [
                ["init", "--idempotency-key", "init-1"],
                ["cite-selection", "--artifact", str(artifact), "--start", "0", "--end", "11", "--handle", "ALPHA", "--idempotency-key", "cite-1"],
                ["cite-selection", "--artifact", str(artifact), "--start", "0", "--end", "11", "--handle", "ALPHA", "--idempotency-key", "cite-2"],
                ["lookup-actions", "--artifact", str(artifact), "--start", "0", "--end", "11"],
                ["status"],
                ["export"],
                ["check"],
            ]
            for command in commands:
                completed = subprocess.run(
                    [sys.executable, "-m", "c2s", "--repo", str(repo), *command],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertTrue((repo / "operations.jsonl").exists())
            self.assertTrue((repo / "exports" / "c2s-status.json").exists())
            self.assertTrue((repo / "site" / "docs" / "index.md").exists())

    def test_native_host_dispatch_uses_replacement_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / ".c2s"
            replacement.init_repo(repo, idempotency_key="init-1")
            response = native_host.dispatch(
                {
                    "schema_version": native_host.INTEGRATION_SCHEMA,
                    "action": "citation.create",
                    "repository": str(repo),
                    "idempotency_key": "native-1",
                    "payload": {
                        "artifact": "https://example.test/page",
                        "start": 0,
                        "end": 11,
                        "selected_text": "Alpha claim",
                        "handle_name": "Inbox",
                    },
                }
            )

            self.assertTrue(response["ok"])
            self.assertIn("citation_id", response)

    def test_reconciliation_imports_replacement_operations_deterministically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo" / ".c2s"
            other_parent = root / "other"
            other = other_parent / ".c2s"
            artifact = root / "notes.md"
            artifact.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
            replacement.init_repo(repo, idempotency_key="init-1")
            other_parent.mkdir()
            shutil.copytree(repo, other)

            replacement.cite_selection(
                SimpleNamespace(repo=repo, artifact=str(artifact), start=0, end=11, handle="ALPHA", handle_id=None, group_id=None, idempotency_key="left")
            )
            replacement.cite_selection(
                SimpleNamespace(repo=other, artifact=str(artifact), start=12, end=22, handle="BETA", handle_id=None, group_id=None, idempotency_key="right")
            )
            result = replacement.reconcile(SimpleNamespace(repo=repo, other_repo=other))
            state = replacement.replay(repo)

            self.assertTrue(result["ok"])
            self.assertEqual(1, result["operations_imported"])
            self.assertEqual(2, len(state["citations"]))


if __name__ == "__main__":
    unittest.main()
