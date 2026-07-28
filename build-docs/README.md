# Cite2Site Build Docs

**Status:** active build documentation map.

Cite2Site is in the Replacement Protocol and Archival Separation Gate. The
historical v0.3/v1 package remains preserved, but it is not current
implementation authority and must not be used to resume Gate 9 work.

Fresh agents must start with `AGENTS.md`. This file is the map after that
orientation step.

## Current Execution Authority

- [internal/CURRENT_STATUS_MATRIX.md](internal/CURRENT_STATUS_MATRIX.md)
- [internal/BUILD_WORKFLOW_CURRENT.md](internal/BUILD_WORKFLOW_CURRENT.md)
- [internal/CI_VALIDATION.md](internal/CI_VALIDATION.md)
- [internal/PROJECT_PLAN.md](internal/PROJECT_PLAN.md)
- [internal/DOCUMENTATION_STANDARD.md](internal/DOCUMENTATION_STANDARD.md)
- [internal/phase_prompts/REPLACEMENT_PROTOCOL_ARCHIVAL_SEPARATION_GATE.md](internal/phase_prompts/REPLACEMENT_PROTOCOL_ARCHIVAL_SEPARATION_GATE.md)

## Active Replacement Architecture

- [architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md](architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md)
- [architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md](architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md)
- [architecture/ARCHIVAL_BOUNDARY.md](architecture/ARCHIVAL_BOUNDARY.md)
- [architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md](architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md)
- [architecture/REPLACEMENT_SCHEMA_INDEX.md](architecture/REPLACEMENT_SCHEMA_INDEX.md)
- [internal/adrs/0011-clean-protocol-replacement-and-archival-boundary.md](internal/adrs/0011-clean-protocol-replacement-and-archival-boundary.md)

## Active Requirements

These files must be reconciled to the replacement protocol before replacement
implementation is accepted:

- [internal/requirements/BRD.md](internal/requirements/BRD.md)
- [internal/requirements/DRD.md](internal/requirements/DRD.md)
- [internal/requirements/TRD.md](internal/requirements/TRD.md)
- [internal/requirements/MIGRATION_DIRECTIVE.md](internal/requirements/MIGRATION_DIRECTIVE.md)

## Historical V0.3/V1 Package

The following material is **Historical**, **Superseded**, and **Unsupported by
the active runtime**. It is preserved for audit and design history only:

- `architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md`
- `architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md`
- `architecture/V1_STABLE_CONTRACT.md`
- `architecture/SCHEMA_INDEX.md`
- `architecture/schemas/`
- `architecture/examples/`
- `internal/COMPATIBILITY_CORPUS.md`
- old phase prompts, guides, examples, and tests that encode evidence-derived
  citation IDs, string-handle identity, or the two-ledger v0.3/v1 authority
  model.

Do not add these files back to the active reading order. Use Git history,
especially `9b761e2b05298313425e6d5b0c2033c08dfed114`, as the stable archive
reference when investigating historical behavior.

## Change Control Rule

Every replacement implementation change must map to:

1. the refined reconciliation RFC;
2. the archival boundary;
3. the replacement implementation specification;
4. the replacement schema index and schemas when public shapes change;
5. the current status matrix and project plan;
6. tests that prove replacement semantics.

If a proposed change depends on v0.3/v1 behavior, archive or redesign it before
implementation. Do not create a compatibility bridge unless a future task
explicitly authorizes one.
