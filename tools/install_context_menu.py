#!/usr/bin/env python3
"""Install Cite2Site into the Windows right-click context menu.

Usage::

    python tools/install_context_menu.py          # install
    python tools/install_context_menu.py --remove # uninstall

After installation, right-click any file → Cite2Site:
  - Look up citations here — runs c2s lookup-actions against the file
  - Cite selected text here — runs c2s cite-selection (all-text placeholder)
"""
from __future__ import annotations

import argparse
import sys


def install() -> None:
    try:
        from context_menu import menus
    except ImportError:
        print("context-menu is required. pip install context-menu")
        sys.exit(1)

    menu = menus.ContextMenu(
        name="Cite2Site",
        type="FILES",
        entries=[
            menus.ContextCommand(
                name="Look up citations here",
                command='cmd /k c2s lookup-actions --artifact "%1" --start 0 --end 0',
            ),
            menus.ContextCommand(
                name="Cite selection here",
                command='cmd /k c2s cite-selection --artifact "%1" --start 0 --end 0',
            ),
        ],
    )
    menu.compile()
    print("Cite2Site added to Windows right-click menu.")
    print("Right-click any file -> Cite2Site -> Look up citations here / Cite selection here")


def remove() -> None:
    try:
        from context_menu import menus
    except ImportError:
        print("context-menu is required. pip install context-menu")
        sys.exit(1)

    menus.ContextMenu(name="Cite2Site", type="FILES", entries=[]).remove()
    print("Cite2Site removed from Windows right-click menu.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Install Cite2Site Windows context menu.")
    p.add_argument("--remove", action="store_true")
    args = p.parse_args()
    remove() if args.remove else install()
