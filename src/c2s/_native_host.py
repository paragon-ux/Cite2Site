"""Chrome native messaging host installation for Cite2Site.

Provides `c2s install-native-host` CLI command.  Registers the native
messaging host manifest so the Chrome extension can communicate with c2s.

Writes the manifest to the platform-specific directory AND to every Chrome
profile folder found on disk, because Chrome can be finicky about where it
looks for native hosts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HOST_NAME = "com.cite2site.cite"


def _host_script_path() -> Path:
    return (Path(__file__).parent.parent.parent / "browser-extension" / "native_host.py").resolve()


def _create_wrapper_bat(script: Path, dest_dir: Path) -> Path:
    """Copy native_host.py and native_host.bat to dest_dir, return .bat path."""
    import shutil
    shutil.copy2(script, dest_dir / script.name)
    # Also copy the .bat wrapper alongside it
    bat_src = script.with_suffix(".bat")
    bat_dst = dest_dir / bat_src.name
    if bat_src.exists():
        shutil.copy2(bat_src, bat_dst)
        # Replace __PYTHON__ placeholder with actual Python path
        content = bat_dst.read_text(encoding="utf-8")
        content = content.replace("__PYTHON__", sys.executable)
        bat_dst.write_text(content, encoding="utf-8")
        return bat_dst
    else:
        # Fallback: create .bat wrapper from scratch
        bat = dest_dir / script.with_suffix(".bat").name
        bat.write_text(f'@echo off\r\n"{sys.executable}" "{script}"\r\n', encoding="utf-8")
        return bat


def _build_manifest(script: Path, manifest_dir: Path) -> tuple[dict, Path]:
    """Build manifest dict and return (manifest, wrapper_path_or_script)."""
    if sys.platform == "win32":
        wrapper = _create_wrapper_bat(script, manifest_dir)
        exe_path = str(wrapper)
    else:
        exe_path = str(script)
    manifest = {
        "name": _HOST_NAME,
        "description": "Cite2Site native messaging host",
        "path": exe_path,
        "type": "stdio",
        "allowed_origins": ["chrome-extension://*/"],
    }
    return manifest, Path(exe_path) if sys.platform == "win32" else script


def _write_manifest(manifest: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _register_registry(manifest_path: Path) -> bool:
    """Register the manifest path in Windows registry. Returns True on success."""
    if sys.platform != "win32":
        return True
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
        return True
    except Exception as exc:
        print(f"Note: could not register with Chrome registry ({exc}).", file=sys.stderr)
        return False


def _write_to_chrome_profiles(manifest: dict) -> None:
    """Write manifest to every REAL Chrome profile's NativeMessagingHosts dir.
    A real profile has a 'Preferences' file."""
    if sys.platform != "win32":
        return
    chrome_dir = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    if not chrome_dir.exists():
        return
    written = 0
    for profile in chrome_dir.iterdir():
        if not profile.is_dir():
            continue
        # Only real Chrome profiles have a Preferences file
        if not (profile / "Preferences").exists():
            continue
        nh_dir = profile / "NativeMessagingHosts"
        nh_dir.mkdir(parents=True, exist_ok=True)
        dest = nh_dir / f"{_HOST_NAME}.json"
        _write_manifest(manifest, dest)
        written += 1
    if written == 0:
        print("  No Chrome profiles found", file=sys.stderr)
    else:
        print(f"  Synced to {written} Chrome profile(s)", file=sys.stderr)


def install() -> None:
    script = _host_script_path()
    if not script.exists():
        print(f"Native host script not found: {script}", file=sys.stderr)
        raise SystemExit(1)

    # Determine manifest directory
    if sys.platform == "win32":
        manifest_dir = Path.home() / "AppData" / "Local" / "Cite2Site"
    elif sys.platform == "darwin":
        manifest_dir = Path.home() / "Library" / "Application Support" / "Cite2Site"
    else:
        manifest_dir = Path.home() / ".config" / "Cite2Site"

    manifest, exe = _build_manifest(script, manifest_dir)
    manifest_path = manifest_dir / f"{_HOST_NAME}.json"

    # Check idempotent — but still update Chrome profiles
    already = False
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if existing.get("path") == manifest.get("path", ""):
                already = True
        except (json.JSONDecodeError, OSError):
            pass

    if not already:
        _write_manifest(manifest, manifest_path)
        _register_registry(manifest_path)
        print(f"Native host installed: {manifest_path}", file=sys.stderr)
    else:
        print(f"Native host already installed: {manifest_path}", file=sys.stderr)

    # Always sync to Chrome profiles (belt and suspenders)
    _write_to_chrome_profiles(manifest)

    print("", file=sys.stderr)
    print("Chrome extension setup:", file=sys.stderr)
    print("  1. CLOSE all Chrome windows completely (check Task Manager)", file=sys.stderr)
    print("  2. Start Chrome fresh", file=sys.stderr)
    print("  3. Go to chrome://extensions, enable Developer mode", file=sys.stderr)
    print("  4. Click 'Load unpacked' -> select the browser-extension/ folder", file=sys.stderr)
    print("  5. Select text on any page, right-click -> Cite with Cite2Site", file=sys.stderr)
