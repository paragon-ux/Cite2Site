"""Validate GitHub Actions workflow YAML files."""
import sys, yaml
from pathlib import Path

for wf in Path(".github/workflows").glob("*.yml"):
    try:
        with open(wf) as f:
            yaml.safe_load(f)
        print(f"  {wf.name}: OK")
    except Exception as e:
        print(f"  {wf.name}: FAIL — {e}")
        sys.exit(1)

print("PASS: All workflows valid")
