# R0: Archival Separation

**Status:** active.

## Objective

Move historical v0.3/v1 files outside the active repository and replace the
documentation spine with replacement-protocol authority.

## Deliverables

- `../Cite2Site-Archival/` contains the archived package.
- Active repo no longer contains old v0.3/v1 protocol specs, schemas,
  examples, compatibility corpus, old phase prompts, old guides, old release
  docs, old integration examples, or old active tests.
- Active docs point to replacement gates R0-R9.
- Active schema index lists replacement schemas and examples.
- Status matrix distinguishes active replacement status from archive history.

## Acceptance

- Docs link and JSON parse checks pass.
- Search confirms archived v0.3/v1 files are absent from tracked repo content.
- Replacement gate prompts R0-R9 exist.
- No old-model test is part of active conformance.
