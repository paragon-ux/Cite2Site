# Design Requirements Document

**Status:** internal design requirements authority.

## Scope And Maturity

The design describes the intended human and agent experience. The current
runtime supplies the CLI/core contracts for citation, handle binding, contextual
lookup, status, export, and checks. Native right-click integrations, recovery
commands, grouped site navigation, and full privacy behavior are Target work.
This distinction matters: a menu design is not a claim that the menu is already
available.

## Design Objective

Cite2Site should make citation management feel native in the user's current
tool while keeping authority in append-only citation history. The design must be
simple for everyday users, explicit for agents, and safe for publication.

## Design Principles

1. **Source-clean by default**: never require markers in the cited artifact.
2. **One gesture for humans**: a supported integration should let a user cite
   or manage a citation through one deliberate context action.
3. **Deterministic for agents**: every agent-facing surface returns JSON.
4. **Projection, not authority**: UI, sites, and exports are generated views.
5. **Fail closed**: ambiguity requires user or agent selection.
6. **Readable without training**: citation sites should be navigable by artifact,
   handle, tag, status, and batch.
7. **Privacy first**: default public output is metadata-only.

## Primary UX Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| DR-001 | A supported integration presents `Cite with C2S` for an uncited selection. | `lookup-actions` returns a create action and an integration fixture maps it to one user gesture. |
| DR-002 | A supported integration presents cited-region actions. | `lookup-actions` returns actions for matches; the integration names a concrete target for mutations. |
| DR-003 | Multiple overlapping citations show a picker first. | Response includes multiple ordered matches and `requires_picker`. |
| DR-004 | Mutating cited-region actions target a concrete citation. | Commands reject ambiguous mutations. |
| DR-005 | Handles can be edited without opening raw JSON. | UI contract and `set-handle` support bind, rename, alias, retire. |
| DR-006 | Users can recover mistakes. | Append-only recovery commands and their inverse relationships have success and error tests. |
| DR-007 | Site navigation supports browsing and scanning. | Grouped MkDocs pages have stable links and deterministic order. |
| DR-008 | Users can publish safely. | Metadata-only default is backed by a no-evidence-leak export test. |

## Contextual Menu Model

**Target integration model:** the following menus are integration behavior. The
current implementation exposes `lookup-actions` as the substrate; it does not
ship a right-click plugin.

Uncited selection:

```text
right click selection -> Cite with C2S
```

Cited region:

```text
right click cited region -> Open / Rename handle / Add alias / Undo / Redo
```

Changed or missing citation:

```text
right click region -> Open / Accept current / Relocate / Retire
```

Overlapping citations:

```text
right click region -> picker -> action menu
```

Picker ordering:

1. exact selection match;
2. smallest containing range;
3. most recent preferred-handle binding;
4. citation ID lexical order.

## Site Design Requirements

**Target publication model:** the current site is intentionally flat. Grouped
pages become an implementation claim only after the grouping/export gates and
link/privacy tests pass.

The MkDocs site must provide:

- home summary;
- all citations page;
- artifact pages;
- handle and alias pages;
- tag pages;
- status pages;
- batch pages;
- needs-attention page for changed, missing, ambiguous, unsupported, or adapter
  unavailable citations.

Page rules:

- show citation ID;
- show preferred handle and aliases;
- show artifact URI or public label;
- show status;
- show range summary;
- show tags and batch ID;
- hide evidence text in `metadata_only`;
- indicate when evidence details are private.

## Agent Experience Requirements

Agents need:

- deterministic JSON success and error shapes;
- stable error codes;
- batch creation;
- idempotency keys;
- query filters;
- grouped indexes;
- no prose scraping requirement;
- clear refusal on ambiguous evidence.

Agent surfaces must expose their current maturity in machine-readable fields or
command availability; agents must never be asked to scrape prose to distinguish
implemented capability from design intent.

## Accessibility Requirements

Generated MkDocs pages should:

- use semantic headings;
- avoid information conveyed only by color;
- keep citation IDs copyable;
- keep handles visible as text;
- provide stable anchors;
- keep metadata tables readable on narrow screens through MkDocs defaults.

## Content Requirements

Terminology:

- Use **citation history** for append-only authority.
- Use **projected citation state** for replay output.
- Use **handle** for editable alias.
- Do not call citations stale.
- Do not describe citation refresh.
- Do not describe overlays as C2S authority.

## Design Acceptance

A design change is acceptable only if:

1. it preserves source cleanliness;
2. it maps to a command or integration contract;
3. it has a JSON behavior for agents where applicable;
4. it has privacy behavior;
5. it does not create hidden authority outside `.c2s`.
6. it names the current implementation state and the test or gate that proves
   the claim.
