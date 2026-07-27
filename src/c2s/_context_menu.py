"""Windows context-menu integration for Cite2Site.

Provides `c2s install-context-menu` and `c2s uninstall-context-menu` CLI
commands.  Registers Cite2Site entries in the Windows Explorer right-click
menu so users can look up citations and cite selections directly from any
file.
"""
from __future__ import annotations


def _menu_entries() -> list[dict[str, str]]:
    """Return the context-menu entries to register."""
    return [
        {
            "name": "Look up citations here",
            "command": 'cmd /k c2s lookup-actions --artifact "%1" --start 0 --end 0',
        },
        {
            "name": "Cite selection here",
            "command": 'cmd /k c2s cite-selection --artifact "%1" --start 0 --end 0',
        },
    ]


def install() -> None:
    """Register Cite2Site in the Windows Explorer context menu."""
    from context_menu import menus

    entries = [
        menus.ContextCommand(name=e["name"], command=e["command"])
        for e in _menu_entries()
    ]
    menu = menus.ContextMenu(name="Cite2Site", type="FILES", entries=entries)
    menu.compile()
    print("Cite2Site added to Windows right-click menu.")
    print("Right-click any file -> Cite2Site -> Look up citations here / Cite selection here")


def uninstall() -> None:
    """Remove Cite2Site from the Windows Explorer context menu."""
    from context_menu import menus

    menus.ContextMenu(name="Cite2Site", type="FILES", entries=[]).remove()
    print("Cite2Site removed from Windows right-click menu.")
