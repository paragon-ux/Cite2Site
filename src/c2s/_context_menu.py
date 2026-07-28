"""Windows context-menu integration for Cite2Site.

Provides `c2s install-context-menu` and `c2s uninstall-context-menu` CLI
commands.  Registers Cite2Site in the Windows Explorer right-click menu.
"""
from __future__ import annotations

import sys


def _menu_entries() -> list[dict[str, str]]:
    """Return the context-menu entries to register."""
    return [
        {
            "name": "Look up citations here",
            "command": 'cmd /k c2s lookup-actions --artifact "%1" --start 0 --end 0',
        },
    ]


def install() -> None:
    """Register Cite2Site in the Windows Explorer context menu."""
    from context_menu import menus

    menu = menus.ContextMenu(name="Cite2Site", type="FILES")
    items = [
        menus.ContextCommand(name=e["name"], command=e["command"])
        for e in _menu_entries()
    ]
    menu.add_items(items)
    menu.compile()
    print("Cite2Site added to Windows right-click menu.", file=sys.stderr)
    print("Right-click any file -> Cite2Site -> Look up citations here", file=sys.stderr)


def uninstall() -> None:
    """Remove Cite2Site from the Windows Explorer context menu."""
    from context_menu import menus

    menus.removeMenu("Cite2Site", "FILES")
    print("Cite2Site removed from Windows right-click menu.", file=sys.stderr)
