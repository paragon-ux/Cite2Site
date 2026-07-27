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

## Architecture Source Package

- [architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md](architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md)
- [architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md](architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md)
- [architecture/SCHEMA_INDEX.md](architecture/SCHEMA_INDEX.md)
- [architecture/schemas/](architecture/schemas/)
- [architecture/examples/](architecture/examples/)

Architecture files are implementation contracts. When command behavior,
event shape, replay output, export shape, or adapter semantics change, update
the architecture package first or in the same patch.

## Availability Notice

This checkout currently omits the external product-narrative files and ADRs
named by the historical documentation map. They are not recreated or edited by
this pass because they are owner-controlled deletions in the worktree. Their
absence is a documentation-completeness blocker: `AGENTS.md` still directs
agents to consult relevant ADRs. Restore them deliberately in a dedicated gate,
then apply this standard before treating the documentation set as release-
complete. The local link check only verifies documents that are present.

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
