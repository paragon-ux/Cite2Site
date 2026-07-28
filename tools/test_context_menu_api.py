"""Verify updated context_menu API with FastCommand + cd /d pattern."""
from context_menu import menus

# Install
for entry in [
    {"name": "Cite2Site — Test Look up", "command": 'cmd /c cd /d "%~dp1" && echo Lookup "%1" && pause'},
    {"name": "Cite2Site — Test Cite", "command": 'cmd /c cd /d "%~dp1" && echo Cite "%1" && pause'},
]:
    fc = menus.FastCommand(name=entry["name"], type="FILES", command=entry["command"])
    fc.compile()

print("FastCommand compile() OK for both entries")

# Uninstall
for name in ["Cite2Site — Test Look up", "Cite2Site — Test Cite"]:
    menus.removeMenu(name, "FILES")

print("removeMenu() OK for both entries")
print("PASS: FastCommand API verified")
