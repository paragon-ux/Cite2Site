"""Install and register the Cite2Site Chrome native-messaging host."""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

from .core import C2SError
from .replacement import assert_replacement_repository

_HOST_NAME = "com.cite2site.cite"
_EXTENSION_ID_RE = re.compile(r"^[a-p]{32}$")


def _host_script_path() -> Path:
    """Return the packaged standalone host script."""
    return Path(__file__).with_name("native_host.py").resolve()


def _app_dir() -> Path:
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "Cite2Site"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Cite2Site"
    return Path.home() / ".local" / "share" / "cite2site"


def _manifest_path() -> Path:
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Google"
            / "Chrome"
            / "NativeMessagingHosts"
            / f"{_HOST_NAME}.json"
        )
    if sys.platform.startswith("linux"):
        return (
            Path.home()
            / ".config"
            / "google-chrome"
            / "NativeMessagingHosts"
            / f"{_HOST_NAME}.json"
        )
    return _app_dir() / f"{_HOST_NAME}.json"


def _validate_extension_id(extension_id: str) -> str:
    normalized = extension_id.strip().lower()
    if not _EXTENSION_ID_RE.fullmatch(normalized):
        raise C2SError(
            "E_EXTENSION_ID",
            "Chrome extension ID must be exactly 32 characters using letters a through p.",
            extension_id=extension_id,
        )
    return normalized


def _validate_repo(repo_arg: str | Path | None) -> Path:
    if repo_arg is None:
        repo_arg = str(Path.home() / ".c2s")
    repo_dir = Path(repo_arg).expanduser().resolve()
    try:
        assert_replacement_repository(repo_dir)
    except C2SError as exc:
        if exc.code != "E_REPO_NOT_INITIALIZED":
            raise
        raise C2SError(
            "E_REPO_NOT_INITIALIZED",
            "Cite2Site repository is not initialized at the configured path",
            repo=str(repo_dir),
            hint="Run c2s init with an idempotency key from the project root, then reinstall the native host.",
        ) from exc
    return repo_dir


def _write_windows_launcher(app_dir: Path, script_path: Path) -> Path:
    launcher = app_dir / "native_host.bat"
    launcher.write_text(
        f'@echo off\r\n"{sys.executable}" "{script_path}"\r\n',
        encoding="utf-8",
        newline="",
    )
    return launcher.resolve()


def _register_windows_manifest(manifest_path: Path) -> None:
    try:
        import winreg

        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            rf"Software\Google\Chrome\NativeMessagingHosts\{_HOST_NAME}",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
        finally:
            winreg.CloseKey(key)
    except OSError as exc:
        raise C2SError(
            "E_NATIVE_HOST_REGISTRY",
            "Could not register the native messaging host with Chrome",
            reason=str(exc),
            manifest=str(manifest_path),
        ) from exc


def install(extension_id: str, repo_arg: str | Path = ".c2s") -> dict[str, str]:
    extension_id = _validate_extension_id(extension_id)
    repo_dir = _validate_repo(repo_arg)

    source_script = _host_script_path()
    if not source_script.is_file():
        raise C2SError(
            "E_NATIVE_HOST_SCRIPT",
            "Packaged native-host script is missing",
            path=str(source_script),
        )

    app_dir = _app_dir()
    app_dir.mkdir(parents=True, exist_ok=True)

    installed_script = app_dir / "native_host.py"
    shutil.copy2(source_script, installed_script)

    config_path = app_dir / "config.json"
    config_path.write_text(
        json.dumps({"repo": str(repo_dir)}, indent=2) + "\n",
        encoding="utf-8",
    )

    if sys.platform == "win32":
        executable_path = _write_windows_launcher(app_dir, installed_script)
    else:
        installed_script.chmod(installed_script.stat().st_mode | 0o111)
        executable_path = installed_script.resolve()

    manifest = {
        "name": _HOST_NAME,
        "description": "Cite2Site replacement native messaging host",
        "path": str(executable_path),
        "type": "stdio",
        "allowed_origins": [f"chrome-extension://{extension_id}/"],
    }

    manifest_path = _manifest_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if sys.platform == "win32":
        _register_windows_manifest(manifest_path)

    result = {
        "manifest": str(manifest_path),
        "host": str(executable_path),
        "config": str(config_path),
        "repo": str(repo_dir),
        "extension_id": extension_id,
    }

    print("Cite2Site native host installed:", file=sys.stderr)
    for key, value in result.items():
        print(f"  {key}: {value}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Close every Chrome process, reopen Chrome, then reload Cite2Site.", file=sys.stderr)
    return result
