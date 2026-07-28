# Cite2Site

**Status:** replacement protocol rebuild.

Cite2Site is a source-clean citation system. It records citation authority in a
dedicated Cite2Site repository and never writes markers into the artifacts that
people cite.

The active protocol is the replacement model: record-instance citations,
stable groups, group-owned handle IDs, completed atomic operations,
idempotency, complete rolling tallies, scoped duplicate policy, deterministic
semantic reconciliation, and metadata-only publication by default.

The previous v0.3/v1 package is historical. It has been moved outside this
repository to `../Cite2Site-Archival/` and remains available through Git
history. It is not an active compatibility target.

## Current CLI Shape

Replacement commands are being delivered gate by gate. Mutating commands must
include an `idempotency_key`, append one completed operation, and produce
replacement authority objects.

```bash
python -m c2s init --repo .c2s --idempotency-key init-demo
python -m c2s cite-selection --repo .c2s --artifact notes.md --start 0 --end 11 --handle ALPHA --idempotency-key demo-1
python -m c2s lookup-actions --repo .c2s --artifact notes.md --start 0 --end 11
python -m c2s status --repo .c2s
```

During the rebuild, a command exists only when its replacement gate has tests
and status evidence. Old command behavior is not preserved as compatibility.

## Authority

Start with [AGENTS.md](AGENTS.md) and [build-docs/README.md](build-docs/README.md).
The protocol authority is:

- [refined reconciliation RFC](build-docs/architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md)
- [clean archival migration policy](build-docs/architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md)
- [archival boundary](build-docs/architecture/ARCHIVAL_BOUNDARY.md)
- [replacement implementation specification](build-docs/architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md)
- [replacement schema index](build-docs/architecture/REPLACEMENT_SCHEMA_INDEX.md)
- [replacement integration contract](build-docs/architecture/INTEGRATION_CONTRACT.md)

## Validation

Local replacement validation starts with:

```bash
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
```

Gate-specific validation expands from
[CI_VALIDATION.md](build-docs/internal/CI_VALIDATION.md) and the active gate
prompt.
