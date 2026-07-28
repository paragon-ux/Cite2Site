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
    "description": "Cite2Site native messaging host",
    "path": "",
    "type": "stdio",
    "allowed_origins": [],
}


def _host_script_path() -> Path:
    return (Path(__file__).parent.parent.parent / "browser-extension" / "native_host.py").resolve()


def _manifest_dir() -> Path:
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Local" / "Cite2Site"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Cite2Site"
    else:
        return Path.home() / ".config" / "Cite2Site"


def _create_wrapper_bat(script: Path) -> Path:
    """Create a .bat wrapper that launches the native host with python."""
    bat = script.with_suffix(".bat")
    bat.write_text(f'@echo off\r\n"{sys.executable}" "{script}"\r\n', encoding="ascii")
    return bat


def install() -> None:
    script = _host_script_path()
    if not script.exists():
        print(f"Native host script not found: {script}", file=sys.stderr)
        raise SystemExit(1)

    manifest_dir = _manifest_dir()
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest = dict(_MANIFEST_TEMPLATE)

    if sys.platform == "win32":
        wrapper = _create_wrapper_bat(script)
        manifest["path"] = str(wrapper)
    else:
        manifest["path"] = str(script)

    manifest["allowed_origins"] = ["chrome-extension://*/"]

    manifest_path = manifest_dir / f"{_HOST_NAME}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if sys.platform == "win32":
        import winreg
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Google\Chrome\NativeMessagingHosts\com.cite2site.cite"
        )
        try:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
        finally:
            winreg.CloseKey(key)

    print(f"Native host installed: {manifest_path}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Chrome extension setup:", file=sys.stderr)
    print("  1. Go to chrome://extensions", file=sys.stderr)
    print("  2. Enable 'Developer mode'", file=sys.stderr)
    print("  3. Click 'Load unpacked'", file=sys.stderr)
    print("  4. Select the browser-extension/ folder", file=sys.stderr)
    print("  5. Select text on any page, right-click -> Cite with Cite2Site", file=sys.stderr)
