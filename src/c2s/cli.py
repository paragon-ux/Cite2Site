from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from . import core
from .adapter import _SUPPORTED as _ADAPTER_CHOICES

_ADAPTER_NAMES = sorted(_ADAPTER_CHOICES.keys())


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise core.C2SError("E_USAGE", message)


def emit(value: dict[str, Any]) -> int:
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0 if value.get("ok", False) else 1


def emit_jsonl(value: dict[str, Any]) -> int:
    for citation in value["citations"]:
        print(json.dumps(citation, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = JsonArgumentParser(prog="c2s")
    parser.add_argument("--repo", default=".c2s", help="citation repository path")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=JsonArgumentParser)

    p_init = sub.add_parser("init")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=lambda args: core.init_repo(core.repo_from_arg(args.repo), force=args.force))

    def add_actor(p: argparse.ArgumentParser) -> None:
        p.add_argument("--actor-kind", default="user", choices=["user", "agent", "machine"])
        p.add_argument("--actor-id")

    p_cite = sub.add_parser("cite-selection")
    p_cite.add_argument("--artifact", required=True)
    p_cite.add_argument("--adapter", choices=_ADAPTER_NAMES)
    p_cite.add_argument("--start", required=True, type=int)
    p_cite.add_argument("--end", required=True, type=int)
    p_cite.add_argument("--expected-content-hash")
    p_cite.add_argument("--handle")
    p_cite.add_argument("--label")
    p_cite.add_argument("--tag", action="append", default=[])
    p_cite.add_argument("--note")
    p_cite.add_argument("--handle-from-first-line", action="store_true")
    add_actor(p_cite)
    p_cite.set_defaults(func=core.cite_selection)

    p_preflight = sub.add_parser("preflight-selection")
    p_preflight.add_argument("--artifact", required=True)
    p_preflight.add_argument("--adapter", choices=_ADAPTER_NAMES)
    p_preflight.add_argument("--start", required=True, type=int)
    p_preflight.add_argument("--end", required=True, type=int)
    p_preflight.add_argument("--expected-content-hash")
    p_preflight.add_argument("--handle")
    p_preflight.add_argument("--label")
    p_preflight.add_argument("--tag", action="append", default=[])
    p_preflight.add_argument("--note")
    p_preflight.add_argument("--handle-from-first-line", action="store_true")
    p_preflight.set_defaults(func=core.preflight_selection)

    p_batch = sub.add_parser("cite-batch")
    p_batch.add_argument("--request", required=True)
    add_actor(p_batch)
    p_batch.set_defaults(func=core.cite_batch)

    p_handle = sub.add_parser("set-handle")
    p_handle.add_argument("--citation-id", required=True)
    p_handle.add_argument("--handle", required=True)
    p_handle.add_argument("--action", default="bind", choices=["bind", "rename", "alias", "retire"])
    p_handle.add_argument("--previous-handle")
    add_actor(p_handle)
    p_handle.set_defaults(func=core.set_handle)

    p_accept = sub.add_parser("accept-current")
    p_accept.add_argument("--citation-id", required=True)
    p_accept.add_argument("--expected-content-hash")
    add_actor(p_accept)
    p_accept.set_defaults(func=core.accept_current)

    for command, func in [("retract", core.retract), ("restore", core.restore)]:
        action = sub.add_parser(command)
        action.add_argument("--citation-id", required=True)
        add_actor(action)
        action.set_defaults(func=func)

    p_relocate = sub.add_parser("relocate")
    p_relocate.add_argument("--citation-id", required=True)
    p_relocate.add_argument("--artifact")
    p_relocate.add_argument("--adapter", choices=_ADAPTER_NAMES)
    p_relocate.add_argument("--start", required=True, type=int)
    p_relocate.add_argument("--end", required=True, type=int)
    p_relocate.add_argument("--expected-content-hash")
    add_actor(p_relocate)
    p_relocate.set_defaults(func=core.relocate)

    p_note = sub.add_parser("note")
    p_note.add_argument("--citation-id", required=True)
    p_note.add_argument("--note", required=True)
    add_actor(p_note)
    p_note.set_defaults(func=core.note)

    p_lookup = sub.add_parser("lookup-actions")
    p_lookup.add_argument("--artifact", required=True)
    p_lookup.add_argument("--start", required=True, type=int)
    p_lookup.add_argument("--end", required=True, type=int)
    p_lookup.add_argument("--privacy", default=None, choices=sorted(core.PRIVACY_MODES))
    p_lookup.set_defaults(func=core.lookup_actions)

    p_status = sub.add_parser("status")
    p_status.add_argument("--privacy", default=None, choices=sorted(core.PRIVACY_MODES))
    p_status.set_defaults(func=core.status)

    p_citations = sub.add_parser("citations")
    p_citations.add_argument("--artifact")
    p_citations.add_argument("--handle")
    p_citations.add_argument("--tag")
    p_citations.add_argument("--status", choices=sorted(core.VALID_STATUSES))
    p_citations.add_argument("--batch")
    p_citations.add_argument("--privacy", default=None, choices=sorted(core.PRIVACY_MODES))
    p_citations.add_argument("--format", default="json", choices=["json", "jsonl"])
    p_citations.set_defaults(func=core.citations)

    p_export = sub.add_parser("export")
    p_export.add_argument("--privacy", default=None, choices=sorted(core.PRIVACY_MODES))
    p_export.set_defaults(func=core.export)

    p_check = sub.add_parser("check")
    p_check.set_defaults(func=core.check)

    try:
        args = parser.parse_args(argv)
        func: Callable[[argparse.Namespace], dict[str, Any]] = args.func
        value = func(args)
        return emit_jsonl(value) if args.command == "citations" and args.format == "jsonl" else emit(value)
    except core.C2SError as exc:
        print(json.dumps(exc.to_json(), indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
