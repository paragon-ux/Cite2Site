"""Chrome native messaging host installation for Cite2Site.

Provides `c2s install-native-host` CLI command.  Registers the host
manifest and Windows registry entry so Chrome can discover it.

Requires the extension ID from chrome://extensions:
    c2s install-native-host --extension-id abcdefghijklmnopqrstuvwxyzabcdef
"""
from __future__ import annotations

import json, shutil, sys
from pathlib import Path

_HOST_NAME = "com.cite2site.cite"


def _host_script_path() -> Path:
    return (Path(__file__).parent.parent.parent / "browser-extension" / "native_host.py").resolve()


def _host_bat_path() -> Path:
    return _host_script_path().with_suffix(".bat")


def install(extension_id: str) -> None:
    script = _host_script_path()
    bat = _host_bat_path()
    if not script.exists():
        print(f"Native host script not found: {script}", file=sys.stderr)
        raise SystemExit(1)

    if sys.platform == "win32":
        manifest_dir = Path.home() / "AppData" / "Local" / "Cite2Site"
    elif sys.platform == "darwin":
        manifest_dir = Path.home() / "Library" / "Application Support" / "Cite2Site"
    else:
        manifest_dir = Path.home() / ".config" / "Cite2Site"

    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Copy script and .bat wrapper to manifest directory
    shutil.copy2(script, manifest_dir / "native_host.py")
    if bat.exists():
        dest_bat = manifest_dir / "native_host.bat"
        shutil.copy2(bat, dest_bat)
        content = dest_bat.read_text(encoding="utf-8")
        content = content.replace("__PYTHON__", sys.executable)
        dest_bat.write_text(content, encoding="utf-8")
        exe_path = str(dest_bat)
    else:
        exe_path = str(script)

    manifest = {
        "name": _HOST_NAME,
        "description": "Cite2Site native messaging host",
        "path": exe_path,
        "type": "stdio",
        "allowed_origins": [f"chrome-extension://{extension_id}/"],
    }

    manifest_path = manifest_dir / f"{_HOST_NAME}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Register with Windows registry
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Google\Chrome\NativeMessagingHosts\com.cite2site.cite"
            )
            try:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
            finally:
                winreg.CloseKey(key)
        except Exception as exc:
            print(f"Note: could not register with registry ({exc})", file=sys.stderr)

    print(f"Native host installed: {manifest_path}", file=sys.stderr)
    print(f"Extension ID: {extension_id}", file=sys.stderr)
    print("", file=sys.stderr)
    print("  1. Close ALL Chrome windows completely", file=sys.stderr)
    print("  2. Start Chrome, go to chrome://extensions, reload the extension", file=sys.stderr)
    print("  3. Select text on any page, right-click -> Cite with Cite2Site", file=sys.stderr)
