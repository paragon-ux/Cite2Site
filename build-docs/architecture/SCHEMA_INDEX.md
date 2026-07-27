# Schema Index

**Status:** architecture-source schema inventory.

Schemas are implementation contracts for command payloads, event records, and
projection output. They intentionally cover the stable shape without requiring a
runtime JSON Schema dependency in the Python core.

## Scope And Limits

The schemas describe the target v0.3 contract, including shapes for grouped
indexes and commands not yet delivered in the first slice. A valid JSON file is
not proof that an implementation is semantically valid: schema alone cannot
establish hash-chain continuity, citation existence, source cleanliness,
deterministic ordering, privacy behavior, or whether a named command is
implemented.

Treat a schema/example pair as a reviewable contract fixture. When runtime
validation is introduced, it must preserve the stdlib-only core unless a
dependency decision is explicitly approved.

## Schema Inventory

| Path | Purpose |
|---|---|
| `schemas/project.schema.json` | `.c2s/project.json` |
| `schemas/event-envelope.schema.json` | Common append-only event fields |
| `schemas/citation-created-event.schema.json` | `citation.created` event |
| `schemas/handle-bound-event.schema.json` | `handle.bound` event |
| `schemas/cite-batch-request.schema.json` | Agent batch citation request |
| `schemas/lookup-actions-response.schema.json` | Contextual menu lookup response |
| `schemas/status-report.schema.json` | Replay status projection |
| `schemas/export-indexes.schema.json` | Grouped index projection |

## Example Inventory

| Path | Purpose |
|---|---|
| `examples/project.example.json` | Initialized project metadata |
| `examples/citation-created-event.example.json` | Citation event |
| `examples/handle-bound-event.example.json` | Handle binding event |
| `examples/cite-batch-request.example.json` | Batch request |
| `examples/lookup-actions-response.example.json` | Overlap action response |
| `examples/status-report.example.json` | Replay status |
| `examples/export-indexes.example.json` | Grouped indexes |

## Rules

- Schema files use JSON Schema draft 2020-12.
- Example files must validate against their paired schema when schema tooling is
  available; CI currently guarantees JSON parsing and manual contract review,
  not full JSON Schema evaluation.
- Schema changes require updates to implementation spec, protocol spec, tests,
  and current status matrix.
- A schema addition must state its maturity: Implemented, Partial, Target, or
  Open. Do not represent a target-only schema as an available CLI response.
- Examples use fabricated hashes and paths. They are explanatory fixtures, not
  cryptographically valid event histories.
