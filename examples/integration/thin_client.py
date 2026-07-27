from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


IMPLEMENTED_C2S_ACTIONS = {
    "cite": {"command": "cite-selection", "label": "Cite with C2S", "action": None},
    "set_handle": {"command": "set-handle", "label": "Rename handle", "action": "rename"},
    "note": {"command": "note", "label": "Add note", "action": None},
    "accept_current": {"command": "accept-current", "label": "Accept current evidence", "action": None},
    "relocate": {"command": "relocate", "label": "Relocate citation", "action": None},
    "retract": {"command": "retract", "label": "Retract citation", "action": None},
    "restore": {"command": "restore", "label": "Restore citation", "action": None},
}

HOST_ACTIONS = {
    "open": {"command": None, "label": "Open citation"},
}

UNAVAILABLE_ACTIONS = {
    "retire": "Citation retirement is not implemented in this runtime.",
    "undo": "Undo is not implemented in this runtime.",
    "redo": "Redo is not implemented in this runtime.",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_SRC = PROJECT_ROOT / "src"


@dataclass(frozen=True)
class C2SThinClient:
    """Transport-neutral example client that delegates all authority to C2S."""

    repo: Path
    python: str = sys.executable

    def run_c2s(self, args: Sequence[str]) -> dict[str, Any]:
        env = os.environ.copy()
        if PROJECT_SRC.exists():
            existing = env.get("PYTHONPATH")
            env["PYTHONPATH"] = str(PROJECT_SRC) if not existing else os.pathsep.join([str(PROJECT_SRC), existing])
        completed = subprocess.run(
            [self.python, "-m", "c2s", "--repo", str(self.repo), *args],
            check=False,
            capture_output=True,
            encoding="utf-8",
            env=env,
        )
        payload_text = completed.stdout if completed.returncode == 0 else completed.stderr
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "error": {
                    "code": "E_INTEGRATION_BAD_JSON",
                    "message": "C2S did not return a JSON envelope.",
                    "details": {"returncode": completed.returncode, "output": payload_text},
                },
            }
        return payload

    def prepare_citation_request(
        self,
        artifact: str,
        start: int,
        end: int,
        *,
        adapter: str = "markdown",
        handle: str | None = None,
        label: str | None = None,
    ) -> dict[str, Any]:
        args = ["cite-selection", "--artifact", artifact, "--adapter", adapter, "--start", str(start), "--end", str(end)]
        if handle:
            args += ["--handle", handle]
        if label:
            args += ["--label", label]
        return {
            "schema_version": "c2s.integration.thin-client.v0.1",
            "operation": "cite_selection",
            "transport": "cli",
            "command": args,
            "artifact": {"uri": artifact, "adapter": adapter},
            "selection": {"start": start, "end": end, "encoding": "unicode_scalar_offset"},
        }

    def cite_selection(
        self,
        artifact: str,
        start: int,
        end: int,
        *,
        adapter: str = "markdown",
        handle: str | None = None,
        label: str | None = None,
    ) -> dict[str, Any]:
        request = self.prepare_citation_request(artifact, start, end, adapter=adapter, handle=handle, label=label)
        return self.run_c2s(request["command"])

    def lookup_context(self, artifact: str, start: int, end: int, *, privacy: str = "metadata_only") -> dict[str, Any]:
        response = self.run_c2s(["lookup-actions", "--artifact", artifact, "--start", str(start), "--end", str(end), "--privacy", privacy])
        if not response.get("ok"):
            return self.present_error(response)

        matches = []
        for raw_match in response.get("matches", []):
            matches.append(
                {
                    "citation_id": raw_match["citation_id"],
                    "preferred_handle": raw_match.get("preferred_handle"),
                    "match_kind": raw_match["match_kind"],
                    "range_summary": raw_match["range_summary"],
                    "status": raw_match["status"],
                    "actions": [self.action_contract(action, raw_match["citation_id"], raw_match.get("preferred_handle")) for action in raw_match.get("actions", [])],
                }
            )

        top_level_actions = [self.action_contract(action, None) for action in response.get("actions", [])]
        return {
            "ok": True,
            "schema_version": "c2s.integration.thin-client.v0.1",
            "artifact": {"uri": artifact},
            "selection": {"start": start, "end": end, "encoding": "unicode_scalar_offset"},
            "requires_picker": bool(response.get("requires_picker", False)),
            "matches": matches,
            "actions": top_level_actions,
            "authoritative_state": "c2s_cli",
            "overlay_state_persisted": False,
        }

    def action_contract(self, action_id: str, citation_id: str | None, preferred_handle: str | None = None) -> dict[str, Any]:
        if action_id in IMPLEMENTED_C2S_ACTIONS:
            meta = IMPLEMENTED_C2S_ACTIONS[action_id]
            action = {
                "id": action_id,
                "label": meta["label"],
                "available": True,
                "transport": "cli",
                "command": meta["command"],
                "requires_citation_id": action_id != "cite",
                "citation_id": citation_id,
            }
            if meta["command"] == "set-handle":
                command_template = ["set-handle", "--citation-id", citation_id or "<citation_id>", "--handle", "<handle>", "--action", meta["action"]]
                required_inputs = ["handle"]
                if meta["action"] == "rename":
                    command_template += ["--previous-handle", preferred_handle or "<previous_handle>"]
                    required_inputs.append("previous_handle")
                action["command_template"] = command_template
                action["handle_action"] = meta["action"]
                action["required_inputs"] = required_inputs
            elif meta["command"] == "note":
                action["command_template"] = ["note", "--citation-id", citation_id or "<citation_id>", "--note", "<note>"]
                action["required_inputs"] = ["note"]
            elif meta["command"] == "accept-current":
                action["command_template"] = ["accept-current", "--citation-id", citation_id or "<citation_id>"]
            elif meta["command"] == "relocate":
                action["command_template"] = ["relocate", "--citation-id", citation_id or "<citation_id>", "--start", "<start>", "--end", "<end>"]
                action["required_inputs"] = ["start", "end"]
            elif meta["command"] in {"retract", "restore"}:
                action["command_template"] = [meta["command"], "--citation-id", citation_id or "<citation_id>"]
            return action
        if action_id in HOST_ACTIONS:
            meta = HOST_ACTIONS[action_id]
            return {
                "id": action_id,
                "label": meta["label"],
                "available": True,
                "transport": "host",
                "command": meta["command"],
                "requires_citation_id": True,
                "citation_id": citation_id,
            }
        return {
            "id": action_id,
            "label": action_id.replace("_", " ").title(),
            "available": False,
            "transport": None,
            "command": None,
            "requires_citation_id": True,
            "citation_id": citation_id,
            "unavailable_reason": UNAVAILABLE_ACTIONS.get(action_id, "Action is not implemented in this runtime."),
        }

    def cancel_picker(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "schema_version": "c2s.integration.thin-client.v0.1",
            "operation": "picker_cancelled",
            "cancelled": True,
            "mutation_performed": False,
            "matches_count": len(context.get("matches", [])),
        }

    def select_action(self, context: dict[str, Any], citation_id: str | None, action_id: str) -> dict[str, Any]:
        if context.get("requires_picker") and not citation_id:
            return {
                "ok": False,
                "error": {
                    "code": "E_INTEGRATION_PICKER_REQUIRED",
                    "message": "Overlapping citations require a selected citation ID before mutation.",
                    "details": {"action": action_id},
                },
            }
        matches = context.get("matches", [])
        selected_matches = [match for match in matches if match.get("citation_id") == citation_id]
        if citation_id and not selected_matches:
            return {
                "ok": False,
                "error": {
                    "code": "E_INTEGRATION_CITATION_NOT_IN_CONTEXT",
                    "message": "Selected citation ID is not present in this lookup context.",
                    "details": {"citation_id": citation_id},
                },
            }
        actions = selected_matches[0].get("actions", []) if selected_matches else context.get("actions", [])
        for action in actions:
            if action["id"] == action_id:
                if not action["available"]:
                    return {
                        "ok": False,
                        "error": {
                            "code": "E_INTEGRATION_ACTION_UNAVAILABLE",
                            "message": action["unavailable_reason"],
                            "details": {"action": action_id, "citation_id": citation_id},
                        },
                    }
                return {"ok": True, "selected_citation_id": citation_id, "action": action}
        return {
            "ok": False,
            "error": {
                "code": "E_INTEGRATION_ACTION_NOT_OFFERED",
                "message": "Action is not available for this context.",
                "details": {"action": action_id, "citation_id": citation_id},
            },
        }

    def present_error(self, response: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": False,
            "schema_version": "c2s.integration.thin-client.v0.1",
            "display": {"kind": "error", "error": response.get("error", {})},
        }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Minimal Cite2Site thin-client integration example.")
    parser.add_argument("--repo", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    cite = sub.add_parser("cite-selection")
    cite.add_argument("--artifact", required=True)
    cite.add_argument("--start", required=True, type=int)
    cite.add_argument("--end", required=True, type=int)
    cite.add_argument("--adapter", default="markdown")
    cite.add_argument("--handle")
    cite.add_argument("--label")

    lookup = sub.add_parser("lookup")
    lookup.add_argument("--artifact", required=True)
    lookup.add_argument("--start", required=True, type=int)
    lookup.add_argument("--end", required=True, type=int)
    lookup.add_argument("--privacy", default="metadata_only")

    args = parser.parse_args(argv)
    client = C2SThinClient(Path(args.repo))
    if args.command == "cite-selection":
        result = client.cite_selection(args.artifact, args.start, args.end, adapter=args.adapter, handle=args.handle, label=args.label)
    else:
        result = client.lookup_context(args.artifact, args.start, args.end, privacy=args.privacy)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
