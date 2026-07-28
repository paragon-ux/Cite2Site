"""Integration test for the Cite2Site Chrome native-messaging host."""
from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


def decode_response(raw: bytes) -> dict:
    if len(raw) < 4:
        raise AssertionError(f"host returned no framed response; stderr may contain the cause")
    length = struct.unpack("@I", raw[:4])[0]
    payload = raw[4 : 4 + length]
    if len(payload) != length:
        raise AssertionError("host returned a truncated response")
    return json.loads(payload.decode("utf-8"))


with tempfile.TemporaryDirectory(prefix="c2s-chrome-test-") as tmp_value:
    tmp = Path(tmp_value)
    repo = tmp / ".c2s"
    config = tmp / "config.json"

    subprocess.run(
        [sys.executable, "-m", "c2s.cli", "--repo", str(repo), "init"],
        capture_output=True,
        check=True,
        text=True,
    )
    config.write_text(json.dumps({"repo": str(repo)}), encoding="utf-8")

    selected = "Alpha claim"
    message = {
        "action": "cite-selection",
        "artifact": "https://example.com/article",
        "sourceUrl": "https://example.com/article",
        "title": "Example article",
        "start": 0,
        "end": len(selected),
        "selectedText": selected,
        "contentHash": "sha256:" + hashlib.sha256(selected.encode("utf-8")).hexdigest(),
    }
    raw = json.dumps(message).encode("utf-8")
    payload = struct.pack("@I", len(raw)) + raw

    env = os.environ.copy()
    env["CITE2SITE_NATIVE_CONFIG"] = str(config)

    # Run from an unrelated directory to prove the host does not depend on CWD.
    completed = subprocess.run(
        [sys.executable, "-m", "c2s.native_host"],
        cwd=Path.home(),
        env=env,
        input=payload,
        capture_output=True,
        timeout=30,
    )

    response = decode_response(completed.stdout)
    assert response.get("ok"), response
    assert Path(response["capture_path"]).is_file()
    assert (repo / "citation-history.jsonl").stat().st_size > 0
    citations_md = repo / "site" / "docs" / "citations.md"
    assert citations_md.is_file()
    assert "citation_id" in citations_md.read_text(encoding="utf-8")

    print(json.dumps(response, indent=2))
    print("\nPASS: native host cited, persisted the capture, and refreshed citations.md")
