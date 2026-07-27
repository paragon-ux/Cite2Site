#!/usr/bin/env python3
"""Install Cite2Site into the Windows right-click context menu.

Thin wrapper — delegates to ``c2s install-context-menu`` / ``c2s uninstall-context-menu``.
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> None:
    p = argparse.ArgumentParser(description="Install Cite2Site Windows context menu.")
    p.add_argument("--remove", action="store_true")
    args = p.parse_args()
    cmd = ["c2s", "uninstall-context-menu"] if args.remove else ["c2s", "install-context-menu"]
    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
