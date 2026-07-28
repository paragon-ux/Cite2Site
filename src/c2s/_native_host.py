"""Chrome native messaging host installation for Cite2Site.

Provides `c2s install-native-host` CLI command.  Registers the native
messaging host manifest so the Chrome extension can communicate with c2s.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HOST_NAME = "com.cite2site.cite"
_MANIFEST_TEMPLATE = {
    "name": _HOST_NAME,
    "description": "Cite2Site native messaging host — bridges Chrome extension to c2s CLI",
    "path": "",  # filled at install time
    "type": "stdio",
    "allowed_origins": [
        "chrome-extension://EXTENSION_ID_PLACEHOLDER/"
    ],
}


def _host_script_path() -> Path:
    """Return the absolute path to the native host Python script."""
    return (Path(__file__).parent.parent.parent / "browser-extension" / "native_host.py").resolve()


def _manifest_dir() -> Path:
    """Return the platform-specific native messaging manifest directory."""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Local" / "Cite2Site"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Cite2Site"
    else:  # linux
        return Path.home() / ".config" / "Cite2Site"


def install() -> None:
    """Write the native messaging host manifest and print Chrome setup instructions."""
    script = _host_script_path()
    if not script.exists():
        print(
            f"Native host script not found at: {script}\n"
            "Make sure browser-extension/native_host.py exists.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    manifest_dir = _manifest_dir()
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest = dict(_MANIFEST_TEMPLATE)
    manifest["path"] = str(script)
    # On Windows, the extension ID is fixed when loaded unpacked — use a
    # wildcard origin so any unpacked extension can connect.
    manifest["allowed_origins"] = ["chrome-extension://*/"]

    manifest_path = manifest_dir / f"{_HOST_NAME}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Register with Chrome on Windows via registry
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Google\Chrome\NativeMessagingHosts\com.cite2site.cite"
            )
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
            winreg.CloseKey(key)
        except Exception as exc:
            print(f"Note: could not register with Chrome registry ({exc}).", file=sys.stderr)
            print(f"Manifest written to: {manifest_path}", file=sys.stderr)
            print("You may need to register it manually.", file=sys.stderr)
            return

    print(f"Native host installed: {manifest_path}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Chrome extension setup:", file=sys.stderr)
    print("  1. Go to chrome://extensions", file=sys.stderr)
    print("  2. Enable 'Developer mode' (top right)", file=sys.stderr)
    print("  3. Click 'Load unpacked'", file=sys.stderr)
    print(f"  4. Select the browser-extension/ folder", file=sys.stderr)
    print("  5. Select text on any page, right-click → Cite with Cite2Site", file=sys.stderr)
