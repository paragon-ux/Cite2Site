"""Verify context_menu library API for install and uninstall."""
from context_menu import menus

# Install
menu = menus.ContextMenu(name="TestCite2Site", type="FILES")
menu.add_items([
    menus.ContextCommand(name="Look up", command='cmd /k echo hello "%1"'),
])
menu.compile()
print("compile() OK")

# Uninstall
menus.removeMenu("TestCite2Site", "FILES")
print("removeMenu() OK")
print("PASS: context_menu install + uninstall API verified")


