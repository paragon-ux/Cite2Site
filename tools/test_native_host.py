"""Test the Cite2Site Chrome native messaging host."""
import json, struct, subprocess, sys, tempfile
from pathlib import Path

# Create a test repo with a file to cite
tmp = Path(tempfile.mkdtemp(prefix="c2s-chrome-test-"))
note = tmp / "notes.md"
note.write_text("Alpha claim\nBeta claim\n", encoding="utf-8")

# Init repo
subprocess.run(["c2s", "--repo", str(tmp / ".c2s"), "init"], capture_output=True, check=True)

# Build a native messaging message
msg = {
    "action": "cite-selection",
    "artifact": str(note),
    "start": 0,
    "end": 11,
    "selectedText": "Alpha claim",
    "contentHash": "sha256:abc123",
    "title": "test",
    "sourceUrl": "https://example.com",
}
raw = json.dumps(msg).encode("utf-8")
payload = struct.pack("@I", len(raw)) + raw

# Run the native host
r = subprocess.run(
    [sys.executable, "browser-extension/native_host.py"],
    input=payload, capture_output=True, timeout=10
)

# Parse response
resp_len = struct.unpack("@I", r.stdout[:4])[0]
resp = json.loads(r.stdout[4:4+resp_len])

print(json.dumps(resp, indent=2))
if resp.get("ok"):
    print("\nPASS: Native host returned OK")
else:
    print(f"\nFAIL: {resp.get('error', {}).get('message', resp)}")
    sys.exit(1)

import shutil; shutil.rmtree(tmp)
