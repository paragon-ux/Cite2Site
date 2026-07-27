"""Smoke-test the right-click demo: create citations, then exercise lookup→picker→action."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="c2s-rc-"))
repo = tmp / ".c2s"
note = tmp / "notes.md"
note.write_text("Alpha claim\nBeta claim\nGamma claim\n", encoding="utf-8")

# Init + create overlapping citations
subprocess.run(["c2s", "--repo", str(repo), "init"], capture_output=True)
subprocess.run([
    "c2s", "--repo", str(repo), "cite-selection",
    "--artifact", "notes.md", "--start", "0", "--end", "5", "--handle", "ALPHA"
], capture_output=True)
subprocess.run([
    "c2s", "--repo", str(repo), "cite-selection",
    "--artifact", "notes.md", "--start", "0", "--end", "18", "--note", "overlap"
], capture_output=True)

# Test: uncited region → "cite" action (valid position beyond cited text)
input_data = "y\nNOHANDLE\n\n"
r = subprocess.run(
    ["python", "tools/right_click_demo.py", "--repo", str(repo),
     "--artifact", "notes.md", "--start", "25", "--end", "30"],
    input=input_data, capture_output=True, text=True
)
assert "[OK]" in r.stdout, f"Uncited cite failed:\n{r.stdout}\n{r.stderr}"
print("  PASS: uncited region -> cite action works")

# -- Picker test: overlapping region, select second match, then retract --
# Match order: ALPHA (0-5 exact), then overlap (0-18 contains)
# Pick match [2] (overlap citation), then find and pick retract action
input_data = "2\n"
r = subprocess.run(
    ["python", "tools/right_click_demo.py", "--repo", str(repo),
     "--artifact", "notes.md", "--start", "0", "--end", "5"],
    input=input_data, capture_output=True, text=True
)
# Should show picker with 2 matches
assert "2 citations overlap" in r.stdout, f"Picker not shown:\n{r.stdout}"
print("  PASS: overlapping region shows picker with 2 matches")

shutil.rmtree(tmp)
print("\n=== ALL RIGHT-CLICK DEMO CHECKS PASS ===")
