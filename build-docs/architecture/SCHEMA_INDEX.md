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
| `schemas/project.schema.json` | Implemented `.c2s/project.json`, including publication-policy fields. |
| `schemas/event-envelope.schema.json` | Common append-only event fields |
| `schemas/citation-created-event.schema.json` | `citation.created` event |
| `schemas/workflow-citation-event.schema.json` | Implemented G5 citation compensation events |
| `schemas/handle-bound-event.schema.json` | `handle.bound` event |
| `schemas/cite-batch-request.schema.json` | Agent batch citation request |
| `schemas/citations-response.schema.json` | Implemented `citations` JSON query response |
| `schemas/lookup-actions-response.schema.json` | Contextual menu lookup response |
| `schemas/status-report.schema.json` | Replay status projection |
| `schemas/export-indexes.schema.json` | Grouped index projection |

## Example Inventory

| Path | Purpose |
|---|---|
| `examples/project.example.json` | Initialized project metadata |
| `examples/citation-created-event.example.json` | Citation event |
| `examples/workflow-citation-event.example.json` | Citation compensation event |
| `examples/handle-bound-event.example.json` | Handle binding event |
| `examples/cite-batch-request.example.json` | Batch request |
| `examples/citations-response.example.json` | Implemented citations query response |
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
- `publication.private_link_base` is syntactically an HTTPS URI in the project
  schema; runtime policy validation additionally rejects credentials, queries,
  and fragments before generating a link.
- Examples use fabricated hashes and paths. They are explanatory fixtures, not
  cryptographically valid event histories.
