# Cite2Site Build Docs

**Status:** active build documentation map.

Cite2Site is in the replacement-protocol rebuild. The historical v0.3/v1
package has been moved to the sibling archival folder `Cite2Site-Archival/`
and remains preserved by Git history. It is not current implementation
authority.

Fresh agents must start with `AGENTS.md`. This file is the map after that
orientation step.

## Current Execution Authority

- [internal/CURRENT_STATUS_MATRIX.md](internal/CURRENT_STATUS_MATRIX.md)
- [internal/BUILD_WORKFLOW_CURRENT.md](internal/BUILD_WORKFLOW_CURRENT.md)
- [internal/CI_VALIDATION.md](internal/CI_VALIDATION.md)
- [internal/PROJECT_PLAN.md](internal/PROJECT_PLAN.md)
- [internal/DOCUMENTATION_STANDARD.md](internal/DOCUMENTATION_STANDARD.md)
- [internal/phase_prompts/REPLACEMENT_GATE_00_ARCHIVAL_SEPARATION.md](internal/phase_prompts/REPLACEMENT_GATE_00_ARCHIVAL_SEPARATION.md)
- [internal/phase_prompts/REPLACEMENT_GATE_01_REPOSITORY_IDENTITY.md](internal/phase_prompts/REPLACEMENT_GATE_01_REPOSITORY_IDENTITY.md)
- [internal/phase_prompts/REPLACEMENT_GATE_02_ATOMIC_OPERATIONS.md](internal/phase_prompts/REPLACEMENT_GATE_02_ATOMIC_OPERATIONS.md)
- [internal/phase_prompts/REPLACEMENT_GATE_03_CITATIONS.md](internal/phase_prompts/REPLACEMENT_GATE_03_CITATIONS.md)
- [internal/phase_prompts/REPLACEMENT_GATE_04_GROUPS.md](internal/phase_prompts/REPLACEMENT_GATE_04_GROUPS.md)
- [internal/phase_prompts/REPLACEMENT_GATE_05_HANDLES.md](internal/phase_prompts/REPLACEMENT_GATE_05_HANDLES.md)
- [internal/phase_prompts/REPLACEMENT_GATE_06_DUPLICATE_POLICY.md](internal/phase_prompts/REPLACEMENT_GATE_06_DUPLICATE_POLICY.md)
- [internal/phase_prompts/REPLACEMENT_GATE_07_RECONCILIATION.md](internal/phase_prompts/REPLACEMENT_GATE_07_RECONCILIATION.md)
- [internal/phase_prompts/REPLACEMENT_GATE_08_PROJECTIONS_PUBLICATION.md](internal/phase_prompts/REPLACEMENT_GATE_08_PROJECTIONS_PUBLICATION.md)
- [internal/phase_prompts/REPLACEMENT_GATE_09_INTEGRATION.md](internal/phase_prompts/REPLACEMENT_GATE_09_INTEGRATION.md)

## Active Replacement Architecture

- [architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md](architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md)
- [architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md](architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md)
- [architecture/ARCHIVAL_BOUNDARY.md](architecture/ARCHIVAL_BOUNDARY.md)
- [architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md](architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md)
- [architecture/REPLACEMENT_SCHEMA_INDEX.md](architecture/REPLACEMENT_SCHEMA_INDEX.md)
- [architecture/INTEGRATION_CONTRACT.md](architecture/INTEGRATION_CONTRACT.md)
- [internal/adrs/0011-clean-protocol-replacement-and-archival-boundary.md](internal/adrs/0011-clean-protocol-replacement-and-archival-boundary.md)

## Active Requirements

These files must be reconciled to the replacement protocol before replacement
implementation is accepted:

- [internal/requirements/BRD.md](internal/requirements/BRD.md)
- [internal/requirements/DRD.md](internal/requirements/DRD.md)
- [internal/requirements/TRD.md](internal/requirements/TRD.md)
- [internal/requirements/MIGRATION_DIRECTIVE.md](internal/requirements/MIGRATION_DIRECTIVE.md)

## Historical V0.3/V1 Package

Historical material is outside this repository under
`../Cite2Site-Archival/`. Use that folder or Git history, especially
`9b761e2b05298313425e6d5b0c2033c08dfed114`, when investigating prior
behavior. Do not add archived v0.3/v1 files back to the active reading order.

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
