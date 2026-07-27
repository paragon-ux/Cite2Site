"""End-to-end test: run c2s export, patch mkdocs.yml for Material, build site."""
import re, subprocess, sys, tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="c2s-material-e2e-"))
try:
    # Setup
    (tmp / "notes.md").write_text("Alpha claim\nBeta claim\n", encoding="utf-8")
    subprocess.run(["c2s", "--repo", str(tmp / ".c2s"), "init"], check=True, capture_output=True)
    subprocess.run([
        "c2s", "--repo", str(tmp / ".c2s"), "cite-selection",
        "--artifact", "notes.md", "--start", "0", "--end", "11",
        "--handle", "TEST", "--tag", "e2e"
    ], check=True, capture_output=True)
    subprocess.run([
        "c2s", "--repo", str(tmp / ".c2s"), "export"
    ], check=True, capture_output=True)

    # Patch mkdocs.yml with Material theme
    mkdocs_yml = tmp / ".c2s" / "site" / "mkdocs.yml"
    content = mkdocs_yml.read_text()
    theme_block = """theme:
  name: material
  features:
    - navigation.tabs
    - navigation.indexes
    - content.code.copy
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
"""
    patched = re.sub(
        r"(site_name:.*\n)",
        r"\1\n" + theme_block + "\n",
        content,
        count=1,
    )
    mkdocs_yml.write_text(patched)

    # Build with MkDocs
    result = subprocess.run(
        ["python", "-m", "mkdocs", "build", "-f", str(mkdocs_yml)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"MkDocs build FAILED:\n{result.stderr}")
        sys.exit(1)

    # Verify site output exists
    site_dir = tmp / ".c2s" / "site" / "site"
    assert (site_dir / "index.html").exists(), "index.html missing"
    assert (site_dir / "citations").exists() or (site_dir / "citations.html").exists(), "citations page missing"

    print("PASS: c2s export -> Material theme -> MkDocs build works end-to-end")
finally:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
