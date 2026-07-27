#!/usr/bin/env python3
"""Install Cite2Site into the Windows right-click context menu.

Requires the ``context-menu`` package (optional — core c2s stays stdlib-only)::

    pip install context-menu

Usage::

    python tools/install_context_menu.py          # install
    python tools/install_context_menu.py --remove # uninstall

After installation, right-click any file → Cite2Site → Look up citations here.
This opens the right-click demo tool against that file in a terminal window.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_SCRIPT = str(PROJECT_ROOT / "tools" / "right_click_demo.py")
PYTHON = sys.executable


def _build_command() -> str:
    return (
        f'cmd /k "{PYTHON}" "{DEMO_SCRIPT}"'
        f' --repo "%CD%\\.c2s"'
        f' --artifact "%1"'
        f' --start 0 --end 0'
    )


def install() -> None:
    try:
        from context_menu import menus  # type: ignore[import-untyped]
    except ImportError:
        print(
            "The 'context-menu' package is required for Windows context-menu\n"
            "installation. This is an optional dependency — the core c2s CLI\n"
            "remains stdlib-only.\n\n"
            "  pip install context-menu"
        )
        sys.exit(1)

    menu = menus.ContextMenu(
        name="Cite2Site",
        type="FILES",
        entries=[
            menus.ContextCommand(
                name="Look up citations here",
                command=_build_command(),
            ),
        ],
    )
    menu.compile()
    print("Cite2Site added to Windows right-click menu.")
    print("Right-click any file → Cite2Site → Look up citations here.")
    print(f"  Demo script: {DEMO_SCRIPT}")
    print(f"  To remove:   python {__file__} --remove")


def remove() -> None:
    try:
        from context_menu import menus  # type: ignore[import-untyped]
    except ImportError:
        print("The 'context-menu' package is required. pip install context-menu")
        sys.exit(1)

    menus.ContextMenu(name="Cite2Site", type="FILES", entries=[]).remove()
    print("Cite2Site removed from Windows right-click menu.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Install Cite2Site Windows context menu.")
    p.add_argument("--remove", action="store_true")
    args = p.parse_args()
    remove() if args.remove else install()
