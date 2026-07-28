# R1: Repository Identity

**Status:** planned.

## Objective

Create the replacement repository identity and fail closed on archived-format
repositories before replay or mutation.

## Deliverables

- Replacement `project.json` schema and example.
- `init` creates a replacement repository with a default Inbox group.
- Archived v0.3/v1 repository shape returns `E_ARCHIVED_PROTOCOL_UNSUPPORTED`
  before writes.
- Unsupported schemas return structured errors.

## Acceptance

- New replacement repo initializes and validates.
- Archived repo fixtures remain byte-for-byte unchanged after rejection.
- CLI smoke covers `init` and validation errors.
