# Cite2Site Orientation

**Status:** internal orientation for humans and agents.

## What This Document Can Tell You

This is a map of the current technical direction, not proof that every target
workflow is implemented. Read the status matrix before relying on a command or
integration, and use the documentation standard when deciding how a claim
should be written or verified.

## Read This First

Cite2Site is a source-clean citation system. It records citations outside the
cited artifact, stores append-only history in `.c2s`, replays that history
against current files, and exports metadata-safe citation pages.

## Current Mental Model

```text
citation history + handle bindings + artifact observations + policy
= projected citation state
```

Authority:

- `.c2s/citation-history.jsonl`;
- `.c2s/handle-bindings.jsonl`;
- `.c2s/project.json`.

Not authority:

- MkDocs pages;
- JSON exports;
- editor overlays;
- browser context menus;
- generated indexes.

## Current Repository State

**Implemented first slice:**

- Python package under `src/c2s`;
- CLI entrypoint `python -m c2s`;
- first-slice tests under `tests`;
- source-clean text and Markdown citation creation;
- batch creation, handle binding, contextual lookup, status, export, and
  integrity checks;
- deterministic grouped indexes, index-backed query filters, grouped MkDocs
  navigation, and policy-enforced privacy transforms.

**Target, not current user interface:** editor, browser, and document-tool
right-click integrations; lifecycle-adjacent recovery commands; richer adapter
coverage; and remote CI/release automation. The status matrix names the exact
limitations and next gates.

## Build Order

1. Preserve append-only event authority.
2. Complete workflow commands.
3. Add adapter conformance tests.
4. Add integrations over `lookup-actions`.
5. Add CI and release automation.

## Agent Rules

- Read `AGENTS.md` before editing.
- Use `build-docs/internal/CURRENT_STATUS_MATRIX.md` to choose next work.
- Use `build-docs/architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md` for behavior.
- Use `build-docs/internal/requirements/TRD.md` for implementation requirements.
- Use `build-docs/internal/DOCUMENTATION_STANDARD.md` when changing any
  documentation or contract language.
- Use `build-docs/internal/phase_prompts/` for authorized phase-level build
  instructions.
- Do not modify cited artifacts in tests except when deliberately simulating
  user edits.
- Run `python -m unittest discover -s tests` before reporting changes.

## Important Commands

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
python -m c2s init
python -m c2s status
python -m c2s export
```

## ADR Index

| ADR | Decision |
|---|---|
| [0001-source-clean-citations.md](../adrs/0001-source-clean-citations.md) | C2S does not write markers into cited artifacts. |
| [0002-dedicated-citation-repository.md](../adrs/0002-dedicated-citation-repository.md) | Citation history lives in a dedicated `.c2s` repository. |
| [0003-append-only-replay.md](../adrs/0003-append-only-replay.md) | Projected state is replay output, not mutable authority. |
| [0004-handles-as-editable-refs.md](../adrs/0004-handles-as-editable-refs.md) | Handles are editable aliases over immutable citation IDs. |
| [0005-contextual-actions-not-overlays.md](../adrs/0005-contextual-actions-not-overlays.md) | UI integrations call `lookup-actions`; overlays are not authority. |
| [0006-mkdocs-as-publication-projection.md](../adrs/0006-mkdocs-as-publication-projection.md) | MkDocs is the first publication projection. |
| [0007-metadata-only-default.md](../adrs/0007-metadata-only-default.md) | Public export defaults to metadata-only. |
