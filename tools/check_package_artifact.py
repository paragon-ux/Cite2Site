from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


REQUIRED_EXPORTS = [
    Path(".c2s/exports/c2s-status.json"),
    Path(".c2s/exports/c2s-citations.jsonl"),
    Path(".c2s/exports/index-by-artifact.json"),
    Path(".c2s/exports/index-by-handle.json"),
    Path(".c2s/exports/index-by-tag.json"),
    Path(".c2s/exports/index-by-status.json"),
    Path(".c2s/exports/index-by-batch.json"),
    Path(".c2s/site/docs/index.md"),
    Path(".c2s/site/docs/citations.md"),
]


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    completed.check_returncode()
    return completed


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def snapshot(paths: list[Path], *, cwd: Path) -> dict[str, bytes]:
    return {str(path): (cwd / path).read_bytes() for path in paths}


def parse_json_stdout(completed: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(completed.stdout)


def build_wheel(repo: Path, wheelhouse: Path, *, no_build_isolation: bool) -> Path:
    command = [
        sys.executable,
        "-m",
        "pip",
        "wheel",
        "--no-deps",
        "--wheel-dir",
        str(wheelhouse),
    ]
    if no_build_isolation:
        command.append("--no-build-isolation")
    command.append(str(repo))
    run(command, cwd=repo)
    wheels = sorted(wheelhouse.glob("cite2site-*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"expected exactly one cite2site wheel, found {len(wheels)} in {wheelhouse}")
    return wheels[0]


def smoke_installed_package(python: Path, work_dir: Path, wheel: Path) -> None:
    run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], cwd=work_dir)
    run([str(python), "-m", "c2s", "--help"], cwd=work_dir)

    artifact = work_dir / "notes.md"
    artifact.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
    before = sha256(artifact)

    run([str(python), "-m", "c2s", "--repo", ".c2s", "init"], cwd=work_dir)
    run(
        [
            str(python),
            "-m",
            "c2s",
            "--repo",
            ".c2s",
            "cite-selection",
            "--artifact",
            "notes.md",
            "--start",
            "0",
            "--end",
            "11",
            "--handle",
            "ALPHA",
            "--tag",
            "release-smoke",
        ],
        cwd=work_dir,
    )
    lookup = parse_json_stdout(
        run(
            [
                str(python),
                "-m",
                "c2s",
                "--repo",
                ".c2s",
                "lookup-actions",
                "--artifact",
                "notes.md",
                "--start",
                "0",
                "--end",
                "11",
            ],
            cwd=work_dir,
        )
    )
    if not lookup.get("ok"):
        raise SystemExit("lookup-actions did not return ok=true")

    status = parse_json_stdout(run([str(python), "-m", "c2s", "--repo", ".c2s", "status"], cwd=work_dir))
    if (
        not status.get("ok")
        or len(status.get("citations", [])) != 1
        or status.get("summary", {}).get("resolved") != 1
    ):
        raise SystemExit("status did not report the expected single citation")

    citations = parse_json_stdout(
        run([str(python), "-m", "c2s", "--repo", ".c2s", "citations", "--handle", "ALPHA"], cwd=work_dir)
    )
    if len(citations.get("citations", [])) != 1:
        raise SystemExit("citations query did not return the expected handle match")

    run([str(python), "-m", "c2s", "--repo", ".c2s", "export"], cwd=work_dir)
    for path in REQUIRED_EXPORTS:
        if not (work_dir / path).exists():
            raise SystemExit(f"expected generated file missing: {path}")
    first = snapshot(REQUIRED_EXPORTS, cwd=work_dir)
    run([str(python), "-m", "c2s", "--repo", ".c2s", "export"], cwd=work_dir)
    second = snapshot(REQUIRED_EXPORTS, cwd=work_dir)
    if first != second:
        raise SystemExit("export projections changed across repeated export")

    run([str(python), "-m", "c2s", "--repo", ".c2s", "check"], cwd=work_dir)
    after = sha256(artifact)
    if before != after:
        raise SystemExit("cited artifact bytes changed during installed-package smoke flow")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate a Cite2Site package artifact locally.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="repository root")
    parser.add_argument("--keep-temp", action="store_true", help="preserve temporary build and smoke directories")
    parser.add_argument(
        "--no-build-isolation",
        action="store_true",
        help="disable pip build isolation; useful only when local build requirements are already installed",
    )
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    temp_root = Path(tempfile.mkdtemp(prefix="c2s-package-check-"))
    try:
        wheelhouse = temp_root / "wheelhouse"
        smoke_dir = temp_root / "smoke"
        venv_dir = temp_root / "venv"
        wheelhouse.mkdir()
        smoke_dir.mkdir()
        wheel = build_wheel(repo, wheelhouse, no_build_isolation=args.no_build_isolation)
        venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
        smoke_installed_package(venv_python(venv_dir), smoke_dir, wheel)
        print(json.dumps({"ok": True, "wheel": str(wheel), "smoke_dir": str(smoke_dir)}, indent=2, sort_keys=True))
        return 0
    finally:
        if args.keep_temp:
            print(f"kept temporary directory: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
