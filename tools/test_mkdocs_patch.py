"""Smoke test the mkdocs.yml Material theme patching logic used in the
deploy-mkdocs.yml GitHub Actions workflow."""
import re
import sys
from pathlib import Path

# Simulate the generated mkdocs.yml from c2s export
generated = """site_name: Cite2Site
nav:
  - Home: index.md
  - Citations: citations.md
""".strip()

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
        name: Switch to light mode"""

patched = re.sub(
    r"(site_name:.*\n)",
    r"\1\n" + theme_block + "\n",
    generated + "\n",
    count=1,
)

# Verify theme block was inserted
assert "name: material" in patched, "Material theme not inserted"
assert "site_name: Cite2Site" in patched, "site_name lost"
assert "navigation.tabs" in patched, "navigation.tabs missing"
assert "palette:" in patched, "palette missing"

# Verify the yaml is valid enough to parse roughly
lines = [l for l in patched.strip().split("\n") if l.strip()]
assert lines[0] == "site_name: Cite2Site", f"First line wrong: {lines[0]}"
assert "name: material" in patched, "Material theme not inserted"
print("PASS: Material theme patching logic is correct")
sys.exit(0)
