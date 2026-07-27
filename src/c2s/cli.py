from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from . import core


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise core.C2SError("E_USAGE", message)


def emit(value: dict[str, Any]) -> int:
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0 if value.get("ok", False) else 1


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
    p_cite.add_argument("--adapter", choices=["filesystem-text", "markdown"])
    p_cite.add_argument("--start", required=True, type=int)
    p_cite.add_argument("--end", required=True, type=int)
    p_cite.add_argument("--expected-content-hash")
    p_cite.add_argument("--handle")
    p_cite.add_argument("--label")
    p_cite.add_argument("--tag", action="append", default=[])
    p_cite.add_argument("--note")
    add_actor(p_cite)
    p_cite.set_defaults(func=core.cite_selection)

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

    p_lookup = sub.add_parser("lookup-actions")
    p_lookup.add_argument("--artifact", required=True)
    p_lookup.add_argument("--start", required=True, type=int)
    p_lookup.add_argument("--end", required=True, type=int)
    p_lookup.add_argument("--privacy", default="metadata_only", choices=["metadata_only", "hash_only", "snippet", "private_link"])
    p_lookup.set_defaults(func=core.lookup_actions)

    p_status = sub.add_parser("status")
    p_status.add_argument("--privacy", default="metadata_only", choices=["metadata_only", "hash_only", "snippet", "private_link"])
    p_status.set_defaults(func=core.status)

    p_export = sub.add_parser("export")
    p_export.add_argument("--privacy", default="metadata_only", choices=["metadata_only", "hash_only", "snippet", "private_link"])
    p_export.set_defaults(func=core.export)

    p_check = sub.add_parser("check")
    p_check.set_defaults(func=core.check)

    try:
        args = parser.parse_args(argv)
        func: Callable[[argparse.Namespace], dict[str, Any]] = args.func
        return emit(func(args))
    except core.C2SError as exc:
        print(json.dumps(exc.to_json(), indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
