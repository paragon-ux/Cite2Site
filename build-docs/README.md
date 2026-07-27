# Cite2Site Build Docs

**Status:** active build documentation navigation.

Cite2Site separates external product-facing documents from internal execution
authority and architecture-source contracts. Public narrative is readable,
while internal docs are precise enough for an agent to implement from without
reopening core decisions.

Fresh agents must start with `AGENTS.md`. This file is the build-doc map after
that orientation step, not a replacement for the session gate and reading-order
rules in `AGENTS.md`.

The documentation standard is part of the authority chain. It explains how to
separate implemented behavior from approved target design without diluting
either the technical argument or the reader's experience.

## Current Execution Authority

- [internal/BUILD_WORKFLOW_CURRENT.md](internal/BUILD_WORKFLOW_CURRENT.md)
- [internal/CI_VALIDATION.md](internal/CI_VALIDATION.md)
- [internal/CURRENT_STATUS_MATRIX.md](internal/CURRENT_STATUS_MATRIX.md)
- [internal/PROJECT_PLAN.md](internal/PROJECT_PLAN.md)
- [internal/DOCUMENTATION_STANDARD.md](internal/DOCUMENTATION_STANDARD.md)
- [internal/requirements/BRD.md](internal/requirements/BRD.md)
- [internal/requirements/DRD.md](internal/requirements/DRD.md)
- [internal/requirements/TRD.md](internal/requirements/TRD.md)
- [internal/orientation/README.md](internal/orientation/README.md)

## Phase Prompts

Each prompt is a session-gate implementation contract. Start only the prompt
authorized by the status matrix and its stated prerequisites.

- [Phase 01: Grouping And Indexing](internal/phase_prompts/PHASE_01_GROUPING_INDEXING.md)
- [Phase 02: Privacy And Publication](internal/phase_prompts/PHASE_02_PRIVACY_AND_PUBLICATION.md)
- [Phase 03: Workflow Completeness](internal/phase_prompts/PHASE_03_WORKFLOW_COMPLETENESS.md)
- [Phase 04: Adapter Hardening](internal/phase_prompts/PHASE_04_ADAPTER_HARDENING.md)
- [Phase 05: Integration Examples](internal/phase_prompts/PHASE_05_INTEGRATION_EXAMPLES.md)
- [Phase 06: CI, Release, And Migration](internal/phase_prompts/PHASE_06_CI_RELEASE_AND_MIGRATION.md)
- [Phase 07: v1 Stabilization](internal/phase_prompts/PHASE_07_V1_STABILIZATION.md)

## Architecture Source Package

- [architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md](architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md)
- [architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md](architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md)
- [architecture/SCHEMA_INDEX.md](architecture/SCHEMA_INDEX.md)
- [architecture/schemas/](architecture/schemas/)
- [architecture/examples/](architecture/examples/)

Architecture files are implementation contracts. When command behavior,
event shape, replay output, export shape, or adapter semantics change, update
the architecture package first or in the same patch.

## External Product Narrative

- [external/overviews/PRODUCT_OVERVIEW.md](external/overviews/PRODUCT_OVERVIEW.md)
- [external/overviews/ENGINEERING_OVERVIEW.md](external/overviews/ENGINEERING_OVERVIEW.md)
- [external/overviews/WHITEPAPER.md](external/overviews/WHITEPAPER.md)
- [external/narratives/END_TO_END_NARRATIVE.md](external/narratives/END_TO_END_NARRATIVE.md)
- [external/narratives/PUBLISHING_AND_ADOPTION_PLAN.md](external/narratives/PUBLISHING_AND_ADOPTION_PLAN.md)

External documents explain the product in ordinary language while distinguishing
the current CLI/core substrate from Target integrations and publication work.

## ADRs

- [internal/adrs/0001-source-clean-citations.md](internal/adrs/0001-source-clean-citations.md)
- [internal/adrs/0002-dedicated-citation-repository.md](internal/adrs/0002-dedicated-citation-repository.md)
- [internal/adrs/0003-append-only-replay.md](internal/adrs/0003-append-only-replay.md)
- [internal/adrs/0004-handles-as-editable-refs.md](internal/adrs/0004-handles-as-editable-refs.md)
- [internal/adrs/0005-contextual-actions-not-overlays.md](internal/adrs/0005-contextual-actions-not-overlays.md)
- [internal/adrs/0006-mkdocs-as-publication-projection.md](internal/adrs/0006-mkdocs-as-publication-projection.md)
- [internal/adrs/0007-metadata-only-default.md](internal/adrs/0007-metadata-only-default.md)
- [internal/adrs/0008-session-gates-define-rigor-not-a-hard-stop.md](internal/adrs/0008-session-gates-define-rigor-not-a-hard-stop.md)
- [internal/adrs/0009-artifact-index-is-a-derived-cache.md](internal/adrs/0009-artifact-index-is-a-derived-cache.md)

## Change Control Rule

Every implementation change must map to:

1. a capability row in the current status matrix;
2. a workflow section;
3. a requirement in BRD, DRD, or TRD;
4. a contract in the architecture specs or JSON schemas;
5. a milestone in the project plan.

If a proposed change does not map to those sources, revise the docs first or
treat the change as out of scope. A concise document is not sufficient evidence
that the change is ready; the authority chain and validation evidence must also
be complete.
