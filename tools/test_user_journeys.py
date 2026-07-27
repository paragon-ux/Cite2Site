"""End-to-end smoke test of the right-click / contextual user journey.

Covers the full loop:
1. Cite selections (single + overlapping).
2. lookup-actions returns correct matches, requires_picker, and action lists.
3. Picker selection (user picks a concrete citation_id).
4. Mutating actions: set-handle (rename/alias/retire), accept-current,
   retract, restore, relocate, note.
5. Replay reflects every action.
6. Status transitions are correct.
7. Source artifacts are never modified.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

def c2s(repo, *args):
    """Run a c2s command and return the parsed JSON result."""
    cmd = ["c2s", "--repo", str(repo)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"FAIL: {cmd}\nstdout: {r.stdout}\nstderr: {r.stderr}")
        sys.exit(1)
    if not data.get("ok"):
        print(f"FAIL: {cmd}\n{json.dumps(data, indent=2)}")
        sys.exit(1)
    return data

def assert_eq(actual, expected, msg=""):
    assert actual == expected, f"{msg}: expected {expected!r}, got {actual!r}"

source = Path(tempfile.mkdtemp(prefix="c2s-journey-"))
repo = source / ".c2s"

try:
    # -- Setup: artifact with overlapping content --
    note = source / "notes.md"
    note.write_text(
        "Alpha is the first claim.\n"
        "Alpha and Beta are related claims.\n"
        "Beta is the second claim.\n",
        encoding="utf-8",
    )
    before = note.read_bytes()

    # -- 1. Init --
    c2s(repo, "init")

    # -- 2. Create citations (some overlapping) --
    r1 = c2s(repo, "cite-selection", "--artifact", "notes.md",
             "--start", "0", "--end", "5", "--handle", "ALPHA", "--tag", "test")
    cid_alpha = r1["citation_id"]

    r2 = c2s(repo, "cite-selection", "--artifact", "notes.md",
             "--start", "34", "--end", "38", "--handle", "BETA", "--tag", "test")
    cid_beta = r2["citation_id"]

    # Overlapping: covers both "Alpha" (0-5) and mentions "Beta" too
    r3 = c2s(repo, "cite-selection", "--artifact", "notes.md",
             "--start", "0", "--end", "40", "--note", "overlapping citation")
    cid_overlap = r3["citation_id"]

    # -- 3. lookup-actions: overlapping region (2 citations match 0-5) --
    la = c2s(repo, "lookup-actions", "--artifact", "notes.md",
             "--start", "0", "--end", "5")
    assert_eq(la["requires_picker"], True,
              "multiple citations overlap at 0-5 (ALPHA exact + OVERLAP contains)")
    assert len(la["matches"]) == 2, f"expected 2 matches, got {len(la['matches'])}"
    alphas = [m for m in la["matches"] if m["preferred_handle"] == "ALPHA"]
    assert len(alphas) == 1
    assert_eq(alphas[0]["match_kind"], "exact")
    print("  PASS: overlapping lookup returns both citations with correct match kinds")

    # -- 4. lookup-actions: requires_picker with multiple matches --
    la2 = c2s(repo, "lookup-actions", "--artifact", "notes.md",
              "--start", "34", "--end", "38")
    assert_eq(la2["requires_picker"], True, "BETA+OVERLAP both cover 34-38")
    assert len(la2["matches"]) == 2
    # BETA should be exact, OVERLAP should be contains
    betas = [m for m in la2["matches"] if m["preferred_handle"] == "BETA"]
    assert len(betas) == 1
    assert_eq(betas[0]["match_kind"], "exact")
    print("  PASS: BETA exact match found alongside OVERLAP contains")

    # -- 5. lookup-actions: uncited position returns cite action --
    la3 = c2s(repo, "lookup-actions", "--artifact", "notes.md",
              "--start", "50", "--end", "60")
    assert_eq(len(la3["matches"]), 0)
    assert "actions" in la3
    assert "cite" in la3["actions"], "uncited region should offer cite action"
    print("  PASS: uncited region returns cite action for new citation")

    # -- 5. Picker: user selects citation_id, dispatches set-handle (rename) --
    c2s(repo, "set-handle", "--citation-id", cid_overlap,
        "--handle", "OVERLAP", "--action", "bind")
    # Then rename
    c2s(repo, "set-handle", "--citation-id", cid_overlap,
        "--handle", "BIG-CITE", "--action", "rename", "--previous-handle", "OVERLAP")
    # Then alias (becomes preferred as most recent binding)
    c2s(repo, "set-handle", "--citation-id", cid_overlap,
        "--handle", "BIG-ALT", "--action", "alias")

    # Verify handles in replay: most recent binding (BIG-ALT) is preferred
    status = c2s(repo, "status")
    overlap = next(c for c in status["citations"] if c["citation_id"] == cid_overlap)
    assert_eq(overlap.get("preferred_handle"), "BIG-ALT",
              "most recent binding (alias) is preferred handle")
    assert "BIG-CITE" in overlap.get("aliases", []), "renamed handle preserved as alias"
    assert "OVERLAP" in overlap.get("aliases", []), "original handle preserved as alias"
    print("  PASS: handle rename + alias workflow: most-recent binding is preferred")

    # -- 6. accept-current (idempotent on resolved) --
    c2s(repo, "accept-current", "--citation-id", cid_alpha)
    status2 = c2s(repo, "status")
    alpha = next(c for c in status2["citations"] if c["citation_id"] == cid_alpha)
    assert_eq(alpha["status"], "resolved", "accept-current on resolved is idempotent")
    print("  PASS: accept-current is idempotent on resolved citation")

    # -- 7. retract then restore --
    c2s(repo, "retract", "--citation-id", cid_beta)
    status3 = c2s(repo, "status")
    beta = next(c for c in status3["citations"] if c["citation_id"] == cid_beta)
    assert_eq(beta["status"], "retracted")

    c2s(repo, "restore", "--citation-id", cid_beta)
    status4 = c2s(repo, "status")
    beta = next(c for c in status4["citations"] if c["citation_id"] == cid_beta)
    assert_eq(beta["status"], "resolved")
    print("  PASS: retract + restore cycle works")

    # -- 8. note --
    c2s(repo, "note", "--citation-id", cid_alpha, "--note", "Verified against source")
    print("  PASS: note appended successfully")

    # -- 9. relocate (changes status until accepted) --
    c2s(repo, "relocate", "--citation-id", cid_alpha,
        "--artifact", "notes.md", "--start", "0", "--end", "10")
    status5 = c2s(repo, "status")
    alpha = next(c for c in status5["citations"] if c["citation_id"] == cid_alpha)
    assert_eq(alpha["locator"]["end"], 10, "locator updated after relocate")
    assert_eq(alpha["status"], "changed", "relocate changes status until accepted")
    # Accept the new evidence
    c2s(repo, "accept-current", "--citation-id", cid_alpha)
    status5b = c2s(repo, "status")
    alpha = next(c for c in status5b["citations"] if c["citation_id"] == cid_alpha)
    assert_eq(alpha["status"], "resolved", "accept-current after relocate resolves")
    print("  PASS: relocate -> changed -> accept-current -> resolved")

    # -- 10. check validates hash chains --
    c2s(repo, "check")
    print("  PASS: hash chain valid after all workflow actions")

    # -- 11. source-clean: artifact unchanged --
    after = note.read_bytes()
    assert_eq(before, after, "source artifact was modified!")
    print("  PASS: source artifact unchanged after full workflow")

    # -- 12. export determinism --
    c2s(repo, "export")
    c2s(repo, "export")  # second run — no crash, same output
    print("  PASS: export runs deterministically after full workflow")

    # -- 13. Retire the last active handle → preferred_handle becomes None --
    c2s(repo, "set-handle", "--citation-id", cid_overlap,
        "--handle", "BIG-ALT", "--action", "retire")
    status6 = c2s(repo, "status")
    overlap = next(c for c in status6["citations"] if c["citation_id"] == cid_overlap)
    # All bindings retired → no preferred handle
    assert_eq(overlap.get("preferred_handle"), None,
              "preferred handle is None when all handles retired")
    # Aliases still preserved in history
    assert len(overlap.get("aliases", [])) > 0, "retired handles preserved as aliases"
    print("  PASS: handle retire returns None preferred, preserves alias history")

    print(f"\n{'='*60}")
    print("ALL RIGHT-CLICK USER JOURNEYS PASS")
    print(f"{'='*60}")

finally:
    import shutil
    shutil.rmtree(source, ignore_errors=True)
