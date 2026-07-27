# Phase 02: Privacy And Publication

**Status:** authorized after Phase 01 grouping and indexing is accepted.

## Purpose

Turn the configured `metadata_only` default into enforced publication behavior,
then add explicit, policy-controlled alternatives. The phase makes projection
safe to publish; it does not add a hosted service or make generated pages
authority.

## Required Reading

Read `AGENTS.md`, `DOCUMENTATION_STANDARD.md`, the current status matrix, the
workflow, BRD/DRD/TRD, and the v0.3 protocol and implementation specifications.
Confirm Phase 01 is marked Done before starting.

## Scope

Implement deterministic privacy transforms for `metadata_only`, `hash_only`,
`snippet`, and `private_link`; apply them consistently to status and export;
complete grouped MkDocs navigation; and provide a reproducible local/static
publication path.

## Non-Goals

- Do not expose evidence merely because a caller names a richer mode.
- Do not add cloud synchronization, a C2S web server, or a custom site engine.
- Do not infer a snippet or public link from surrounding content.
- Do not make MkDocs output an authority file.

## Required Design Decisions

Before coding, record the following in the protocol/specification if absent:

1. The exact fields retained and removed by each privacy mode.
2. The repository-policy field that authorizes `snippet` and `private_link`.
3. Whether a forbidden request returns a structured error or a redacted
   projection, and the stable error code if it errors.
4. The deterministic site navigation and slug rules for grouped pages.

## Required Changes

### Core and CLI

- Make `apply_privacy()` a real, pure transform rather than a mode check.
- Ensure `status`, `export`, `lookup-actions`, and `citations` (if present)
  cannot bypass the project policy.
- Keep accepted evidence available only inside authority history unless policy
  explicitly permits a projection field.
- Return generated paths and effective privacy mode in export responses.

### Publication

- Generate deterministic navigation for flat and grouped pages.
- Add a documented local MkDocs preview path without making MkDocs a runtime
  dependency of the stdlib core.
- Document static-host publication as a projection deployment, not a state
  migration.

### Documentation and Contracts

- Update privacy and export sections in BRD, DRD, TRD, protocol, implementation
  specification, schema index, status matrix, workflow, and external adoption
  material in the same gate.
- Add or revise JSON fixtures when public response shape changes.
- Replace every Target privacy claim with Implemented or Partial only when its
  no-leak evidence passes.

## Required Tests

- One fixture with unmistakable evidence text proves that `metadata_only` and
  `hash_only` output omit the text from JSON and Markdown.
- Policy-refusal tests cover disallowed snippets and private links.
- Allowed snippet/private-link tests cover only explicitly authorized fields.
- Repeated export of unchanged input produces byte-identical JSON and Markdown.
- Generated MkDocs links resolve to existing pages.
- Source-byte checks prove export and preview preparation never alter artifacts.
- CLI tests cover success and structured error envelopes for every mode.

## Acceptance Criteria

The phase is accepted only when:

1. default exports contain no accepted or observed evidence text;
2. every richer mode has an explicit policy rule and negative test;
3. grouped publication is deterministic and link-complete;
4. local preview and static-host instructions are reproducible;
5. all required validation from the workflow passes;
6. status, requirements, specs, schemas, examples, and external docs agree.

