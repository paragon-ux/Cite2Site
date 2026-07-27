# Cite2Site Agent Guide — v1.0

**Status:** v1.0 stable. Grounded in implemented agent workflows per Phase 7.

---

## Purpose

This guide is for agents, automation, and tool builders that integrate with
Cite2Site through the deterministic JSON CLI. Every command returns structured
JSON. Every error is machine-readable. No command modifies cited source files.

---

## Design Principles for Agents

1. **Always parse JSON.** Every command outputs JSON to stdout. Errors go to
   stderr as structured JSON.
2. **Check `ok` first.** `{"ok": true, ...}` means success.
   `{"ok": false, "error": {"code": "...", "message": "...", "details": {...}}}`
   means failure.
3. **Citation IDs are immutable.** Use them as stable references. Handles are
   editable aliases.
4. **Batch is atomic by default.** `cite-batch` in `all_or_nothing` mode
   appends all or nothing.
5. **Preflight before cite.** Use `preflight-selection` to validate a citation
   before committing it.
6. **Idempotent workflows.** `accept-current` on an already-resolved citation
   is a no-op. Same for `restore` on a non-retracted citation.

---

## Agent Command Reference

### Repository Commands

| Command | Input | Output |
|---|---|---|
| `c2s init` | --force (optional) | `{"ok": true, "repo": ".c2s", "repository_id": "sha256:..."}` |
| `c2s check` | (none) | `{"ok": true}` or structured error |

### Citation Commands

| Command | Required Flags | Optional Flags |
|---|---|---|
| `c2s cite-selection` | --artifact, --start, --end | --adapter, --expected-content-hash, --handle, --label, --tag, --note, --handle-from-first-line |
| `c2s preflight-selection` | --artifact, --start, --end | Same as cite-selection (read-only) |
| `c2s cite-batch` | --request (JSON file path) | (none) |

### Workflow Commands

| Command | Required Flags | Optional Flags |
|---|---|---|
| `c2s accept-current` | --citation-id | --expected-content-hash |
| `c2s retract` | --citation-id | |
| `c2s restore` | --citation-id | |
| `c2s relocate` | --citation-id, --artifact, --start, --end | --adapter, --expected-content-hash |
| `c2s note` | --citation-id, --note | |

### Handle Commands

| Command | Required Flags | Optional Flags |
|---|---|---|
| `c2s set-handle` | --citation-id, --handle | --action (bind/rename/alias/retire), --previous-handle |

### Query Commands

| Command | Required Flags | Optional Flags |
|---|---|---|
| `c2s lookup-actions` | --artifact, --start, --end | --privacy |
| `c2s status` | (none) | --privacy |
| `c2s citations` | (none, all filters optional) | --artifact, --handle, --tag, --status, --batch, --privacy, --format (json/jsonl) |
| `c2s export` | (none) | --privacy |

### Global Flags

All commands accept `--repo REPO` to specify the citation repository path
(default: `.c2s`).

---

## Agent Workflows

### Cite Evidence

```bash
# 1. Validate the citation without creating it
result=$(c2s preflight-selection --artifact notes.md --start 0 --end 11 --handle ALPHA)
# Parse result.ok, result.evidence, result.citation_id_preview

# 2. If valid, create the citation
result=$(c2s cite-selection --artifact notes.md --start 0 --end 11 --handle ALPHA \
  --expected-content-hash "sha256:abc...")
# Parse result.citation_id
```

### Batch Cite Multiple Selections

```bash
# Write request to temp file
cat > /tmp/batch.json << 'EOF'
{
  "mode": "all_or_nothing",
  "items": [
    {"client_item_id": "i1", "artifact": {"adapter": "filesystem-text", "uri": "file.md"},
     "locator": {"start": 0, "end": 11}, "handle": "A"},
    {"client_item_id": "i2", "artifact": {"adapter": "filesystem-text", "uri": "file.md"},
     "locator": {"start": 12, "end": 22}, "handle": "B"}
  ]
}
EOF

result=$(c2s cite-batch --request /tmp/batch.json)
# Parse result.batch_id, result.created[], result.rejected[]
```

### Query With Filters

```bash
# All citations for an artifact
c2s citations --artifact notes.md --format json

# Changed citations that need attention
c2s citations --status changed --format json

# Citations by batch
c2s citations --batch sha256:abc... --format json

# Cross-filter
c2s citations --artifact notes.md --status resolved --tag important --format json
```

### Overlap Resolution

When multiple citations overlap at a position, `lookup-actions` returns
`requires_picker: true`:

```json
{
  "ok": true,
  "requires_picker": true,
  "matches": [
    {
      "citation_id": "sha256:abc...",
      "preferred_handle": "ALPHA",
      "match_kind": "exact",
      "range_summary": "lines 1-1: Alpha claim",
      "status": "resolved",
      "actions": ["open", "set_handle", "note", "accept_current", "relocate", "retract", "restore"]
    },
    {
      "citation_id": "sha256:def...",
      "preferred_handle": "BETA",
      "match_kind": "contains",
      "range_summary": "lines 1-3: Alpha claim Beta...",
      "status": "changed",
      "actions": ["open", "set_handle", "note", "accept_current", "relocate", "retract", "restore"]
    }
  ]
}
```

The agent must present these to the user (or use its own policy) to select a
concrete `citation_id` before any mutating action.

### Accept Changed Evidence

```bash
# Check current evidence
c2s citations --status changed --format json

# Accept the change for a specific citation
c2s accept-current --citation-id sha256:abc...
```

### Retract and Replace

```bash
# Retract the wrong citation
c2s retract --citation-id sha256:abc...

# Create a corrected one
c2s cite-selection --artifact notes.md --start 50 --end 70 --handle CORRECTED
```

### Relocate Moved Evidence

```bash
c2s relocate --citation-id sha256:abc... \
  --artifact notes-v2.md --start 100 --end 120
```

### Export and Publish

```bash
# Default metadata-only export
c2s export

# Read the generated status report
cat .c2s/exports/c2s-status.json | jq .

# Read grouped indexes
cat .c2s/exports/index-by-artifact.json | jq .
cat .c2s/exports/index-by-status.json | jq .
```

---

## JSON Response Contract

### Success

```json
{
  "ok": true,
  "...command-specific fields..."
}
```

### Error

```json
{
  "ok": false,
  "error": {
    "code": "E_SOME_CODE",
    "message": "Human-readable description",
    "details": {...}
  }
}
```

Parse `error.code` to determine the failure category. The `details` object
provides structured context (e.g., `{"path": "citation-history.jsonl", "line": 1}`).

---

## Error Code Reference

39 stable error codes. See `build-docs/architecture/V1_STABLE_CONTRACT.md` §5
for the complete catalog. Key codes for agent workflows:

| Code | Recovery |
|---|---|
| `E_CITATION_NOT_FOUND` | Verify citation_id; it may have been from a different repo |
| `E_CONTENT_HASH_MISMATCH` | Re-read the artifact and update start/end positions |
| `E_HANDLE_COLLISION` | Choose a different handle or retire the existing one |
| `E_CITATION_RETRACTED` | Use `restore` if the retraction was unintended |
| `E_PRIVACY_POLICY` | Update `.c2s/project.json` publication policy |
| `E_BATCH_ITEM_INVALID` | Inspect `details` for the rejected item's `client_item_id` |
| `E_EVENT_CHAIN` | Repository is corrupted; restore from backup or git history |

---

## Batch Request Schema

```json
{
  "mode": "all_or_nothing",       // or "partial"
  "items": [
    {
      "client_item_id": "string", // Required, maps to rejection report
      "artifact": {
        "adapter": "filesystem-text",  // or "markdown"
        "uri": "path/to/file"
      },
      "locator": {
        "start": 0,      // 0-based character offset
        "end": 11        // 0-based character offset (exclusive)
      },
      "expected_content_hash": "sha256:...",  // Optional
      "handle": "HANDLE",                     // Optional
      "label": "Human label",                 // Optional
      "tags": ["tag1", "tag2"],              // Optional
      "note": "annotation"                    // Optional
    }
  ]
}
```

---

## Privacy Mode Policy

Privacy modes `snippet` and `private_link` require repository policy
in `.c2s/project.json`:

```json
{
  "publication": {
    "privacy_mode": "metadata_only",
    "allow_snippet": false,
    "snippet_max_chars": 500,
    "allow_private_link": false,
    "private_link_base": ""
  }
}
```

Set `allow_snippet: true` to permit evidence text in exports.
Set `allow_private_link: true` and `private_link_base` to an HTTPS URL to
permit private links.

---

## Determinism Guarantees

- Replay is deterministic for the same histories, artifacts, adapters, and policy.
- Export is deterministic for the same input — two runs produce identical output.
- Citation IDs are deterministic — same evidence, artifact, and locator
  produce the same ID.
- Error codes are stable — same error condition produces the same code.

---

## Integration Contract

For editor, browser, and document-tool builders, see
`build-docs/architecture/INTEGRATION_CONTRACT.md` for the lookup-actions
contract and the editor plugin mock in `examples/integration/`.

---

## Limitations (v1.0)

- Only text and Markdown adapters. PDF/DOCX are deferred.
- Overlap ordering uses handle presence, not binding recency (documented as Partial).
- No runtime schema validator. Migration fixture tests cover schema version
  validation.
- Batch operations require a temp file (no stdin).
