# Replacement Schema Index

**Status:** active schema inventory.

The v0.3/v1 schema inventory is archived outside this repository under
`Cite2Site-Archival/`. The files listed here are the only active schema family.

## Required Replacement Schema Families

| Family | Schema | Example | Gate |
|---|---|---|---|
| Project identity | [schemas/replacement-project.schema.json](schemas/replacement-project.schema.json) | [examples/replacement-project.example.json](examples/replacement-project.example.json) | R1 |
| Operation envelope | [schemas/replacement-operation.schema.json](schemas/replacement-operation.schema.json) | [examples/replacement-operation.example.json](examples/replacement-operation.example.json) | R2 |
| Citation creation | [schemas/replacement-citation-created.schema.json](schemas/replacement-citation-created.schema.json) | [examples/replacement-citation-created.example.json](examples/replacement-citation-created.example.json) | R3 |
| Group authority | [schemas/replacement-group.schema.json](schemas/replacement-group.schema.json) | [examples/replacement-group.example.json](examples/replacement-group.example.json) | R4 |
| Handle authority | [schemas/replacement-handle.schema.json](schemas/replacement-handle.schema.json) | [examples/replacement-handle.example.json](examples/replacement-handle.example.json) | R5 |
| Scoped supersession | [schemas/replacement-supersession.schema.json](schemas/replacement-supersession.schema.json) | [examples/replacement-supersession.example.json](examples/replacement-supersession.example.json) | R6 |
| Reconciliation | [schemas/replacement-reconciliation.schema.json](schemas/replacement-reconciliation.schema.json) | [examples/replacement-reconciliation.example.json](examples/replacement-reconciliation.example.json) | R7 |
| Projections | [schemas/replacement-projection.schema.json](schemas/replacement-projection.schema.json) | [examples/replacement-projection.example.json](examples/replacement-projection.example.json) | R8 |
| Integration messages | [schemas/replacement-integration-message.schema.json](schemas/replacement-integration-message.schema.json) | [examples/replacement-integration-message.example.json](examples/replacement-integration-message.example.json) | R9 |

The active implementation must not reuse v0.3/v1 schema IDs for replacement
objects.
