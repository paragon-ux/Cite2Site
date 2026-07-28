"""Windows context-menu integration for Cite2Site.

Provides `c2s install-context-menu` and `c2s uninstall-context-menu` CLI
commands.  Registers a cascading Cite2Site menu in the Windows Explorer
right-click menu.
"""
from __future__ import annotations

import sys


def install() -> None:
    """Register Cite2Site in the Windows Explorer right-click menu."""
    from context_menu import menus

    menu = menus.ContextMenu(name="Cite2Site", type="FILES")
    menu.add_items([
        menus.ContextCommand(
            name="Look up citations here",
            command='cmd /k cd /d "%~dp1" && c2s lookup-actions --artifact "%1" --start 0 --end 0',
        ),
    ])
    menu.compile()
    print("Cite2Site added to Windows right-click menu.", file=sys.stderr)
    print("Right-click any file -> Cite2Site -> Look up citations here", file=sys.stderr)


def uninstall() -> None:
    """Remove Cite2Site from the Windows Explorer right-click menu."""
    from context_menu import menus

    menus.removeMenu("Cite2Site", "FILES")
    print("Cite2Site removed from Windows right-click menu.", file=sys.stderr)
