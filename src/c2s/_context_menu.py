"""Windows context-menu integration for Cite2Site.

Provides `c2s install-context-menu` and `c2s uninstall-context-menu` CLI
commands.  Registers Cite2Site entries directly in the Windows Explorer
right-click menu using FastCommand for top-level placement.
"""
from __future__ import annotations

import sys

# Each entry changes to the artifact's directory before running c2s,
# so the .c2s repo is found relative to the file, not the CWD (which
# Explorer sets to System32).

_ENTRIES = [
    {
        "name": "Cite2Site — Look up citations here",
        "command": 'cmd /c cd /d "%~dp1" && c2s lookup-actions --artifact "%1" --start 0 --end 0 && pause',
    },
    {
        "name": "Cite2Site — Cite selection here",
        "command": 'cmd /c cd /d "%~dp1" && c2s cite-selection --artifact "%1" --start 0 --end 0 && pause',
    },
]


def install() -> None:
    """Register Cite2Site in the Windows Explorer context menu."""
    from context_menu import menus

    for entry in _ENTRIES:
        fc = menus.FastCommand(
            name=entry["name"],
            type="FILES",
            command=entry["command"],
        )
        fc.compile()
    print("Cite2Site added to Windows right-click menu.", file=sys.stderr)
    print("Right-click any file in File Explorer.", file=sys.stderr)
    print("  If not visible, restart Explorer or check 'Show more options'.", file=sys.stderr)


def uninstall() -> None:
    """Remove Cite2Site from the Windows Explorer context menu."""
    from context_menu import menus

    for entry in _ENTRIES:
        menus.removeMenu(entry["name"], "FILES")
    print("Cite2Site removed from Windows right-click menu.", file=sys.stderr)
