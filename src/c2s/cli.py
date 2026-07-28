from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from . import replacement
from .core import C2SError


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise C2SError("E_USAGE", message)


def emit(value: dict[str, Any]) -> int:
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0 if value.get("ok", False) else 1


def main(argv: list[str] | None = None) -> int:
    parser = JsonArgumentParser(prog="c2s")
    parser.add_argument("--repo", default=None, help="citation repository path")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=JsonArgumentParser)

    p_init = sub.add_parser("init")
    p_init.add_argument("--idempotency-key", required=True)
    p_init.set_defaults(func=lambda args: replacement.init_repo(args.repo, idempotency_key=args.idempotency_key))

    p_cite = sub.add_parser("cite-selection")
    p_cite.add_argument("--artifact", required=True)
    p_cite.add_argument("--start", required=True, type=int)
    p_cite.add_argument("--end", required=True, type=int)
    p_cite.add_argument("--group-id")
    p_cite.add_argument("--handle")
    p_cite.add_argument("--handle-id")
    p_cite.add_argument("--idempotency-key", required=True)
    p_cite.set_defaults(func=replacement.cite_selection)

    p_lookup = sub.add_parser("lookup-actions")
    p_lookup.add_argument("--artifact", required=True)
    p_lookup.add_argument("--start", required=True, type=int)
    p_lookup.add_argument("--end", required=True, type=int)
    p_lookup.set_defaults(func=replacement.lookup_actions)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=replacement.status)

    p_export = sub.add_parser("export")
    p_export.set_defaults(func=replacement.export)

    p_check = sub.add_parser("check")
    p_check.set_defaults(func=replacement.check)

    p_reconcile = sub.add_parser("reconcile")
    p_reconcile.add_argument("--other-repo", required=True)
    p_reconcile.set_defaults(func=replacement.reconcile)

    def _install_native_host(_args: argparse.Namespace) -> dict[str, Any]:
        from ._native_host import install

        ext_id = getattr(_args, "extension_id", None)
        if not ext_id:
            return {"ok": False, "error": {"code": "E_USAGE", "message": "--extension-id required"}}
        details = install(ext_id, _args.repo)
        return {"ok": True, **details}

    p_nh = sub.add_parser("install-native-host")
    p_nh.add_argument("--extension-id", required=True, help="Chrome extension ID from chrome://extensions")
    p_nh.set_defaults(func=_install_native_host)

    try:
        args = parser.parse_args(argv)
        func: Callable[[argparse.Namespace], dict[str, Any]] = args.func
        return emit(func(args))
    except C2SError as exc:
        print(json.dumps(exc.to_json(), indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
