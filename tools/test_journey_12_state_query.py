"""Journey #12: Read-Only State Query Contract

Tests the citation state API contract that every future adapter and integration
depends on. Verifies schema conformance, read-only guarantee, determinism,
and structured not-found responses.

This is the highest-leverage journey per the Claude review — journeys 1, 3,
4, and 6-10 all depend on this contract being stable.
"""
import json, subprocess, sys, tempfile
from pathlib import Path

def c2s(repo, *args, ok_required=True):
    cmd = ["c2s", "--repo", str(repo)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"FAIL: {cmd}\nstdout: {r.stdout}\nstderr: {r.stderr}")
        sys.exit(1)
    if ok_required and not data.get("ok"):
        print(f"FAIL: {cmd}\n{json.dumps(data, indent=2)}")
        sys.exit(1)
    return data

source = Path(tempfile.mkdtemp(prefix="c2s-j12-"))
repo = source / ".c2s"
note = source / "notes.md"

try:
    note.write_text("Line one\nLine two\nLine three\n", encoding="utf-8")
    c2s(repo, "init")
    c2s(repo, "cite-selection", "--artifact", "notes.md",
         "--start", "0", "--end", "8", "--handle", "L1", "--tag", "test")

    # ================================================================
    # 1. Schema conformance: every field present per status
    # ================================================================

    # status query
    status = c2s(repo, "status")
    required_top = ["ok", "schema_version", "repository_id", "privacy_mode",
                    "citations", "indexes", "summary"]
    for field in required_top:
        assert field in status, f"status missing top-level field: {field}"
    assert status["schema_version"] == "c2s.status.v0.3"
    assert status["privacy_mode"] == "metadata_only"
    assert status["ok"] is True

    # Per-citation fields
    cit = status["citations"][0]
    per_citation = ["citation_id", "artifact", "locator", "metadata",
                    "preferred_handle", "aliases", "status", "state"]
    for field in per_citation:
        assert field in cit, f"citation missing field: {field}"
    assert cit["status"] == "resolved"
    assert cit["state"] == "active"
    assert cit["metadata"]["tags"] == ["test"]
    print("  PASS: status response schema conformance")

    # citations query
    q = c2s(repo, "citations", "--format", "json")
    assert q["schema_version"] == "c2s.citations.v0.3"
    assert "filters" in q
    assert "citations" in q
    qc = q["citations"][0]
    assert qc["status"] == "resolved"
    assert qc["preferred_handle"] == "L1"
    print("  PASS: citations query response schema conformance")

    # lookup-actions
    la = c2s(repo, "lookup-actions", "--artifact", "notes.md",
             "--start", "0", "--end", "5")
    assert "matches" in la
    assert "ok" in la
    print("  PASS: lookup-actions response schema conformance")

    # ================================================================
    # 2. Read-only guarantee: query never appends to history
    # ================================================================
    history_before = (repo / "citation-history.jsonl").read_bytes()
    handle_before = (repo / "handle-bindings.jsonl").read_bytes()

    for _ in range(3):
        c2s(repo, "status")
        c2s(repo, "citations", "--format", "json")
        # JSONL output is a stream — don't parse as wrapped response
        subprocess.run(
            ["c2s", "--repo", str(repo), "citations", "--format", "jsonl"],
            capture_output=True, check=True
        )
        c2s(repo, "lookup-actions", "--artifact", "notes.md",
            "--start", "0", "--end", "5")
        c2s(repo, "export")
        c2s(repo, "check")

    history_after = (repo / "citation-history.jsonl").read_bytes()
    handle_after = (repo / "handle-bindings.jsonl").read_bytes()
    assert history_before == history_after, "citation history mutated by read-only queries"
    assert handle_before == handle_after, "handle history mutated by read-only queries"
    print("  PASS: read-only guarantee — no history mutation after 3x all queries")

    # ================================================================
    # 3. Determinism: same input → byte-identical output
    # ================================================================
    def export_snapshot():
        c2s(repo, "export")
        return (repo / "exports" / "index-by-artifact.json").read_bytes()

    snap1 = export_snapshot()
    snap2 = export_snapshot()
    assert snap1 == snap2, "export not deterministic across two runs"
    print("  PASS: export determinism across repeated runs")

    status1 = json.dumps(c2s(repo, "status"), sort_keys=True)
    status2 = json.dumps(c2s(repo, "status"), sort_keys=True)
    assert status1 == status2, "status not deterministic"
    print("  PASS: status report determinism")

    # ================================================================
    # 4. Structured not-found / error responses
    # ================================================================
    # Non-existent artifact in citations
    q = c2s(repo, "citations", "--artifact", "nonexistent.md", "--format", "json")
    assert q["citations"] == [], "non-existent artifact should return empty citations"
    assert q["ok"] is True
    print("  PASS: non-existent artifact returns empty list, not error")

    # Non-existent handle
    q = c2s(repo, "citations", "--handle", "NOBODY", "--format", "json")
    assert q["citations"] == []
    print("  PASS: non-existent handle returns empty list")

    # Lookup uncited region
    la = c2s(repo, "lookup-actions", "--artifact", "notes.md",
             "--start", "999", "--end", "1000")
    assert la["matches"] == []
    assert "actions" in la
    assert "cite" in la["actions"]
    print("  PASS: uncited lookup returns cite action")

    # Invalid filter gracefully rejected
    r = subprocess.run(
        ["c2s", "--repo", str(repo), "citations", "--status", "INVALID_STATUS"],
        capture_output=True, text=True
    )
    assert r.returncode != 0
    error = json.loads(r.stderr) if r.stderr.strip() else {}
    assert not error.get("ok", True), f"invalid status should fail: {error}"
    print("  PASS: invalid filter produces structured error")

    print(f"\n{'='*60}")
    print("JOURNEY #12: STATE QUERY CONTRACT — ALL CHECKS PASS")
    print(f"{'='*60}")

finally:
    import shutil
    shutil.rmtree(source, ignore_errors=True)
