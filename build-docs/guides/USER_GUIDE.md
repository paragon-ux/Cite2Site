# Cite2Site User Guide — v1.0

**Status:** v1.0 stable. Grounded in implemented workflows per Phase 7.

---

## What Cite2Site Does

Cite2Site lets you cite evidence from your files without modifying them.
Every citation is recorded in a `.c2s/` directory beside your work. You can
check citation status, search citations, fix mistakes, and publish a citation
site — all through the command line.

The core guarantee: **your source files never change.** Cite2Site only writes
to `.c2s/`.

---

## Getting Started

### Install

```bash
pip install cite2site
```

### Initialize a Citation Repository

Run `c2s init` in any directory you want to cite files from:

```bash
cd ~/my-project
c2s init
```

This creates `.c2s/` with the files Cite2Site uses to track citations.

### Create Your First Citation

Select text in a file and note the start and end character positions
(0-based). For example, in `notes.md`, lines 0-10 contain "Alpha claim".

```bash
c2s cite-selection --artifact notes.md --start 0 --end 11 --handle ALPHA
```

Output:
```json
{"ok": true, "citation_id": "sha256:...", "event_id": "sha256:..."}
```

The file `notes.md` is unchanged.

---

## Everyday Commands

### Check Citation Status

```bash
c2s status
```

Shows every citation, its current status (resolved, changed, missing, etc.),
and grouped indexes.

### Find Citations

```bash
# By artifact
c2s citations --artifact notes.md

# By handle
c2s citations --handle ALPHA

# By tag
c2s citations --tag important

# By status
c2s citations --status changed

# By batch
c2s citations --batch sha256:abc123...

# Machine-readable output
c2s citations --handle ALPHA --format jsonl
```

### See What's Available at a Position

```bash
c2s lookup-actions --artifact notes.md --start 5 --end 8
```

Returns matching citations and the actions you can take.

---

## Fixing Mistakes

### Accept Changed Evidence

If a cited artifact changed and you agree the new text is correct:

```bash
c2s accept-current --citation-id sha256:abc123...
```

### Retract a Wrong Citation

```bash
c2s retract --citation-id sha256:abc123...
```

The citation is marked `retracted`. It stays in history but won't appear in
active search results.

### Restore a Retracted Citation

```bash
c2s restore --citation-id sha256:abc123...
```

### Relocate a Citation

If the evidence moved to a different position or file:

```bash
c2s relocate --citation-id sha256:abc123 --artifact notes-v2.md --start 50 --end 70
```

### Add a Note

```bash
c2s note --citation-id sha256:abc123 --note "Verified against source document"
```

---

## Managing Handles

Handles are human-readable names for citations. The citation ID never changes,
but handles can be renamed.

### Create a Handle During Citation

```bash
c2s cite-selection --artifact notes.md --start 0 --end 11 --handle MY-NAME
```

### Auto-Handle from First Line

If the selected text's first line is a valid handle:

```bash
c2s cite-selection --artifact notes.md --start 0 --end 50 --handle-from-first-line
```

### Rename a Handle

```bash
c2s set-handle --citation-id sha256:abc123 --handle NEW-NAME --action rename --previous-handle OLD-NAME
```

The old handle becomes an alias.

### Add an Alias

```bash
c2s set-handle --citation-id sha256:abc123 --handle ALT-NAME --action alias
```

### Retire a Handle

```bash
c2s set-handle --citation-id sha256:abc123 --handle OLD-NAME --action retire
```

---

## Publishing

### Export the Citation Site

```bash
c2s export
```

Writes to `.c2s/exports/` and `.c2s/site/`. By default, only metadata is
published — no evidence text.

### Preview the Site Locally

```bash
pip install mkdocs
python -m mkdocs serve -f .c2s/site/mkdocs.yml
```

The site shows citations organized by artifact, handle, tag, status, and batch.

### Privacy Modes

Control what the export includes:

```bash
# Default: no evidence text
c2s export --privacy metadata_only

# Strip even content hashes
c2s export --privacy hash_only

# Include evidence text (requires repository policy)
c2s export --privacy snippet

# Include private links (requires repository policy)
c2s export --privacy private_link
```

Snippet and private_link modes are disabled by default. To enable them, edit
`.c2s/project.json`:

```json
{
  "publication": {
    "privacy_mode": "metadata_only",
    "allow_snippet": true,
    "snippet_max_chars": 500,
    "allow_private_link": true,
    "private_link_base": "https://my-site.example.com"
  }
}
```

---

## Batch Citations

Create multiple citations at once with a JSON request file:

```json
{
  "mode": "all_or_nothing",
  "items": [
    {
      "client_item_id": "item-1",
      "artifact": {"adapter": "filesystem-text", "uri": "notes.md"},
      "locator": {"start": 0, "end": 11},
      "handle": "ALPHA"
    },
    {
      "client_item_id": "item-2",
      "artifact": {"adapter": "filesystem-text", "uri": "notes.md"},
      "locator": {"start": 12, "end": 22},
      "handle": "BETA"
    }
  ]
}
```

```bash
c2s cite-batch --request batch.json
```

With `"mode": "partial"`, valid items are created even if some fail.

---

## Dry-Run Selection

Test a citation before creating it:

```bash
c2s preflight-selection --artifact notes.md --start 0 --end 11
```

Returns the evidence contract without appending to history.

---

## Validate the Repository

```bash
c2s check
```

Verifies both the citation-history and handle-bindings hash chains.

---

## Error Codes

Every error returns structured JSON. Common codes:

| Code | Meaning |
|---|---|
| `E_ARTIFACT_MISSING` | The cited file was deleted |
| `E_CONTENT_HASH_MISMATCH` | The evidence text changed since accepted |
| `E_HANDLE_COLLISION` | That handle is already in use |
| `E_CITATION_NOT_FOUND` | No such citation ID |
| `E_PRIVACY_POLICY` | Snippet/private_link requires policy override |
| `E_REPO_NOT_INITIALIZED` | Run `c2s init` first |

See the v1.0 Stable Contract for the full catalog of 38 C2SError codes.

---

## Where Citation Data Lives

```
.c2s/
  project.json                  — repository config
  citation-history.jsonl        — append-only citation events
  handle-bindings.jsonl         — append-only handle events
  artifact-index.jsonl          — derived artifact cache
  exports/                      — generated JSON exports
  site/                         — generated MkDocs site
```

Treat `.c2s/exports/` and `.c2s/site/` as generated output. The authority
files are `citation-history.jsonl`, `handle-bindings.jsonl`, and `project.json`.

---

## Limitations (v1.0)

- Only text and Markdown files are supported. PDF and DOCX support is planned.
- Right-click integration requires an external tool to call Cite2Site commands.
  An integration contract and editor mock are provided for tool builders.
- Overlap ordering uses handle presence, not most-recent binding order.
  This will improve in a future release.
