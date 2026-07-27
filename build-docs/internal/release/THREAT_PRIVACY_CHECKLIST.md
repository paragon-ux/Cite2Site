# Threat And Privacy Checklist

**Status:** internal release review procedure.

## Purpose

Cite2Site's primary release risk is trust erosion: the tool must not mutate
cited artifacts, leak accepted evidence through public projections, or imply
that generated files are authoritative. This checklist is completed before a
release candidate is tagged and whenever publication, export, adapter, schema,
or packaging behavior changes.

## Assets

| Asset | Protection Goal |
|---|---|
| Cited artifacts | Must remain byte-for-byte outside C2S mutation. |
| `.c2s/citation-history.jsonl` | Append-only citation authority; hash chain must remain valid. |
| `.c2s/handle-bindings.jsonl` | Append-only handle authority; aliases must remain auditable. |
| `.c2s/project.json` | Repository metadata and publication policy must be explicit. |
| `.c2s/exports/` | Generated projection; must not be treated as authority. |
| `.c2s/site/` | Generated static site; must default to metadata-safe output. |
| Package artifact | Must not contain local private artifacts, temporary repositories, or secrets. |

## Source-Clean Review

1. Identify every command changed since the prior release.
2. For each mutating command, verify it appends to authority history only.
3. Confirm cited artifact hashes are checked before and after smoke flows.
4. Confirm adapters do not persist markers, comments, hidden metadata, or
   bookmarks into the source artifact.
5. Confirm generated projections can be deleted and recreated from authority
   histories.

Release blocker: any C2S command mutates a cited artifact without an explicit
ADR changing the source-clean invariant.

## Publication Privacy Review

1. Confirm `metadata_only` is the default export mode.
2. Confirm grouped JSON indexes and MkDocs group pages remain metadata-safe.
3. Confirm `hash_only` omits accepted evidence text.
4. Confirm `snippet` fails unless `publication.allow_snippet` is true.
5. Confirm `private_link` fails unless an authorized HTTPS base URL is present.
6. Confirm private-link bases reject credentials, queries, and fragments.
7. Confirm notes, accepted evidence, observed evidence, snippets, and private
   links are absent from metadata-safe query output.

Release blocker: public default output contains accepted evidence text,
observed evidence text, notes intended to remain private, or private-link URLs.

## Schema And Migration Risk

1. Confirm schema-version checks reject unknown authority schema versions.
2. Confirm corrupt JSON and JSONL inputs fail with stable structured errors.
3. Confirm migration procedures back up authority files before writing.
4. Confirm migrations never rewrite history in place without a recoverable
   backup and explicit release notes.
5. Confirm generated projections are rebuilt after migration.

Release blocker: a migration can silently drop events, rewrite cited artifacts,
or make rollback impossible without being recorded in the release notes.

## Packaging And Dependency Risk

1. Build the package artifact locally.
2. Inspect the artifact file list if packaging configuration changes.
3. Confirm runtime dependencies remain empty unless an ADR approves a change.
4. Install from the built artifact with `--no-deps`.
5. Run the installed CLI smoke flow.
6. Confirm no `.c2s` repositories, generated exports, editor files, virtual
   environments, credentials, or local temp paths are packaged.

Release blocker: the artifact cannot be installed cleanly, includes private
local state, or requires an undeclared runtime dependency.

## Error And Diagnostic Review

1. Confirm user-facing failures return the common structured JSON error
   envelope.
2. Confirm stable error codes exist for newly introduced failure paths.
3. Confirm messages do not expose local secrets, full private evidence, or
   unrelated filesystem contents.
4. Confirm ambiguous mutating actions still require a concrete `citation_id`.

Release blocker: a recoverable user error exits with only prose or an
ambiguous mutation can modify citation history.

## Sign-Off

| Reviewer | Area | Result | Notes |
|---|---|---|---|
| | Source-clean | PASS | 98 tests; artifact hash unchanged after smoke |
| | Privacy | PASS | metadata_only default; snippet/link policy-gated; grouped indexes metadata-safe |
| | Migration | PASS | 9 migration fixture tests; schema version validation; tamper/hash-chain rejection |
| | Packaging | PASS | check_package_artifact.py: wheel builds, installs, smoke flows, export deterministic |
| | Errors | PASS | 38 C2SError codes cataloged; structured JSON envelope; no path leaks in messages/details |
