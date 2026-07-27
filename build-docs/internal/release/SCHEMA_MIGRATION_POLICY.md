# Schema Migration Policy And Procedure

**Status:** internal release procedure.

## Authority And Current Versions

The current implementation uses these schema versions:

| Surface | Current Version | Authority |
|---|---|---|
| Project metadata | `c2s.project.v0.3` | `.c2s/project.json` |
| Citation and handle events | `c2s.event.v0.3` | `.c2s/citation-history.jsonl`, `.c2s/handle-bindings.jsonl` |
| Status projection | `c2s.status.v0.3` | generated export/status output |
| Citations query projection | `c2s.citations.v0.3` | CLI query output |
| Artifact index projection | `c2s.artifact-index.v0.3` | derived cache |

Generated projections, grouped indexes, MkDocs files, and the artifact index are
not migration authority. They are regenerated after authority files are checked
or migrated.

## Compatibility Policy

1. A release must document every authority schema version it can read.
2. A release must refuse unknown authority schema versions with a stable
   structured diagnostic.
3. A release must not silently coerce unknown event payloads into the current
   schema.
4. A release may read older schemas only when migration fixtures prove the
   conversion.
5. A release may drop support for an older schema only in a documented breaking
   release with an explicit upgrade path.
6. Runtime JSON Schema validation may be added only without violating the
   stdlib-only runtime constraint or after a dependency ADR approves a change.

## Current Migration State

**Implemented:** Cite2Site v0.3 initializes and checks current v0.3 authority
files.

**Partial:** No migration command exists because no prior released authority
schema is currently supported. The runtime refuses unknown or unsupported
project and event schema versions before replay or mutation. The release
procedure below is the required path for introducing the first migration.

**Target:** When `c2s.project.v0.4` or `c2s.event.v0.4` is introduced, the
release must include migration fixtures and a command or documented manual
procedure before the release is accepted.

## Required Migration Design

Every migration must specify:

| Field | Requirement |
|---|---|
| From version | Exact authority schema version accepted as input. |
| To version | Exact authority schema version written as output. |
| Authority files | Which `.c2s` files are read and written. |
| Backup path | Where original authority files are copied before writes. |
| Rebuild path | Which generated projections are deleted or regenerated. |
| Refusal codes | Stable errors for unsupported, corrupt, or unsafe inputs. |
| Rollback | Whether restore-from-backup is sufficient or a forward repair is required. |
| Tests | Fixture names for success, corruption, unknown version, and source-clean checks. |

## Migration Procedure

1. Stop all commands that may append to the citation repository.
2. Run `c2s check` and keep its JSON output with the release evidence.
3. Copy `.c2s/project.json`, `.c2s/citation-history.jsonl`, and
   `.c2s/handle-bindings.jsonl` into a timestamped backup directory outside
   generated projection folders.
4. Parse all authority files before writing any migrated file.
5. Validate every input record has a supported `schema_version`.
6. Write migrated files to temporary paths in the same directory as the target
   authority files.
7. Validate migrated hash chains and schema versions before replacement.
8. Atomically replace authority files only after all migrated files validate.
9. Delete or regenerate `.c2s/artifact-index.jsonl`, `.c2s/exports/`, and
   `.c2s/site/` from replay.
10. Run `c2s check`, `c2s status`, and `c2s export`.
11. Compare source artifact hashes captured before and after migration when
    fixtures include cited artifacts.
12. Record the migration version, backup path, command output, and validation
    result in release evidence.

## Refusal Procedure

If a repository contains an unknown or corrupt authority schema:

1. Return a structured JSON error with a stable code.
2. Do not write authority files.
3. Do not regenerate projections as a side effect of the refused migration.
4. Tell the maintainer which authority file and record failed.
5. Preserve enough detail for repair without printing accepted evidence text.

Recommended stable error codes for a future migration command:

| Code | Meaning |
|---|---|
| `E_SCHEMA_UNSUPPORTED` | Authority schema version is recognized as unsupported by this release. |
| `E_SCHEMA_UNKNOWN` | Authority schema version is not recognized. |
| `E_MIGRATION_UNSAFE` | Migration preconditions failed before any write. |
| `E_MIGRATION_BACKUP` | Backup could not be created. |
| `E_MIGRATION_VALIDATE` | Migrated output failed validation before replacement. |

## Fixture Requirements

When a prior schema becomes supported, add fixtures for:

1. one minimal valid repository;
2. one repository with citation and handle histories;
3. one repository with generated projections that must be ignored and rebuilt;
4. one unknown project schema version;
5. one unknown event schema version;
6. one corrupt JSON file;
7. one corrupt JSONL record;
8. one hash-chain mismatch;
9. one source-clean artifact hash check.

Each fixture must assert that refused migrations leave authority files
byte-for-byte unchanged.
