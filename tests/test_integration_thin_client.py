import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c2s import core

CLIENT_PATH = ROOT / "examples" / "integration" / "thin_client.py"
spec = importlib.util.spec_from_file_location("thin_client", CLIENT_PATH)
thin_client = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["thin_client"] = thin_client
spec.loader.exec_module(thin_client)


class ThinClientIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = core.Repo(self.root / ".c2s")
        self.note = self.root / "notes.md"
        self.note.write_text("Alpha claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        core.init_repo(self.repo)
        self.client = thin_client.C2SThinClient(self.repo.root)

    def test_fixtures_are_json_and_match_basic_contract(self):
        fixture_dir = ROOT / "examples" / "integration" / "fixtures"
        fixtures = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in fixture_dir.glob("*.json")}
        self.assertEqual(
            {
                "lookup-overlap-picker.json",
                "lookup-uncited-response.json",
                "picker-cancelled.json",
                "selection-citation-request.json",
                "unavailable-actions.json",
            },
            set(fixtures),
        )
        self.assertEqual("unicode_scalar_offset", fixtures["selection-citation-request.json"]["selection"]["encoding"])
        self.assertFalse(fixtures["lookup-uncited-response.json"]["overlay_state_persisted"])
        self.assertTrue(fixtures["lookup-overlap-picker.json"]["requires_picker"])
        self.assertFalse(fixtures["unavailable-actions.json"]["actions"][0]["available"])

    def test_selection_citation_uses_cli_and_preserves_source_bytes(self):
        before = self.note.read_bytes()
        prepared = self.client.prepare_citation_request("notes.md", 0, 11, handle="OPENING-CLAIM")
        self.assertEqual("cite-selection", prepared["command"][0])
        result = self.client.cite_selection("notes.md", 0, 11, handle="OPENING-CLAIM")
        self.assertTrue(result["ok"])
        self.assertEqual(before, self.note.read_bytes())
        projection = core.replay(self.repo)
        self.assertEqual([result["citation_id"]], [citation["citation_id"] for citation in projection["citations"]])
        self.assertEqual("OPENING-CLAIM", projection["citations"][0]["preferred_handle"])

    def test_uncited_lookup_prepares_cite_action_without_overlay_state(self):
        context = self.client.lookup_context("notes.md", 0, 11)
        self.assertTrue(context["ok"])
        self.assertEqual([], context["matches"])
        self.assertEqual("cite", context["actions"][0]["id"])
        self.assertTrue(context["actions"][0]["available"])
        self.assertFalse(context["overlay_state_persisted"])

    def test_single_match_maps_only_currently_implemented_actions_as_available(self):
        citation_id = self.client.cite_selection("notes.md", 0, 11, handle="OPENING-CLAIM")["citation_id"]
        context = self.client.lookup_context("notes.md", 0, 11)
        self.assertFalse(context["requires_picker"])
        self.assertEqual(citation_id, context["matches"][0]["citation_id"])
        actions = {action["id"]: action for action in context["matches"][0]["actions"]}
        self.assertTrue(actions["set_handle"]["available"])
        self.assertEqual("set-handle", actions["set_handle"]["command"])
        self.assertEqual("rename", actions["set_handle"]["handle_action"])
        self.assertIn("--previous-handle", actions["set_handle"]["command_template"])
        self.assertEqual("alias", actions["add_alias"]["handle_action"])
        self.assertNotIn("--previous-handle", actions["add_alias"]["command_template"])
        for recovery_action in ["undo", "redo"]:
            if recovery_action in actions:
                self.assertFalse(actions[recovery_action]["available"])

    def test_overlap_picker_requires_concrete_citation_id_and_cancellation_is_read_only(self):
        broad = self.client.cite_selection("notes.md", 0, 22, handle="BROAD")["citation_id"]
        narrow = self.client.cite_selection("notes.md", 0, 11, handle="NARROW")["citation_id"]
        source_before = self.note.read_bytes()
        citation_history_before = self.repo.citation_history.read_bytes()
        handle_history_before = self.repo.handle_bindings.read_bytes()

        context = self.client.lookup_context("notes.md", 0, 11)
        self.assertTrue(context["requires_picker"])
        self.assertEqual([narrow, broad], [match["citation_id"] for match in context["matches"]])
        refused = self.client.select_action(context, None, "set_handle")
        self.assertFalse(refused["ok"])
        self.assertEqual("E_INTEGRATION_PICKER_REQUIRED", refused["error"]["code"])

        cancelled = self.client.cancel_picker(context)
        self.assertTrue(cancelled["cancelled"])
        self.assertFalse(cancelled["mutation_performed"])
        self.assertEqual(citation_history_before, self.repo.citation_history.read_bytes())
        self.assertEqual(handle_history_before, self.repo.handle_bindings.read_bytes())
        self.assertEqual(source_before, self.note.read_bytes())

    def test_changed_or_missing_recovery_actions_are_unavailable(self):
        citation_id = self.client.cite_selection("notes.md", 0, 11, handle="OPENING-CLAIM")["citation_id"]
        self.note.write_text("Changed claim\nBeta claim\nGamma claim\n", encoding="utf-8")
        context = self.client.lookup_context("notes.md", 0, 11)
        actions = {action["id"]: action for action in context["matches"][0]["actions"]}
        self.assertEqual(citation_id, context["matches"][0]["citation_id"])
        self.assertFalse(actions["accept_current"]["available"])
        self.assertFalse(actions["relocate"]["available"])
        if "retire" in actions:
            self.assertFalse(actions["retire"]["available"])
        selected = self.client.select_action(context, citation_id, "accept_current")
        self.assertFalse(selected["ok"])
        self.assertEqual("E_INTEGRATION_ACTION_UNAVAILABLE", selected["error"]["code"])

    def test_cli_example_smoke_lookup_uses_json_contract(self):
        self.client.cite_selection("notes.md", 0, 11, handle="OPENING-CLAIM")
        completed = subprocess.run(
            [
                sys.executable,
                str(CLIENT_PATH),
                "--repo",
                str(self.repo.root),
                "lookup",
                "--artifact",
                "notes.md",
                "--start",
                "0",
                "--end",
                "11",
            ],
            check=False,
            capture_output=True,
            encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual("c2s.integration.thin-client.v0.1", payload["schema_version"])


if __name__ == "__main__":
    unittest.main()
