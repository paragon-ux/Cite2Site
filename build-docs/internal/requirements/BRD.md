# Business Requirements Document

**Status:** internal product requirements authority.

## How To Read This Document

This BRD defines the product obligations for Cite2Site, not a feature inventory.
The current status matrix distinguishes delivered behavior from approved target
work. Requirements retain their force even when their delivery is scheduled for
a later gate; their acceptance criteria must remain falsifiable.

## Product Name

Cite2Site (C2S)

## Product Summary

Cite2Site is a local-first citation system that lets users and agents create
source-clean universal citations from ordinary artifacts, maintain append-only
citation history, and publish navigable citation sites through MkDocs and static
hosting.

## Business Problem

Users need durable evidence references that carry across files, tools, projects,
and future conversations. Existing approaches usually require source markers,
manual context copying, or platform-specific knowledge systems. Those approaches
fail when the cited artifact cannot be modified, when agents need deterministic
context, or when users want a persistent public or private citation site.

## Target Users

| User | Need |
|---|---|
| Everyday user | Cite passages from documents, web pages, notes, PDFs, spreadsheets, or conversations without learning Git or CLI workflows. |
| Agent user | Give future agents durable, inspectable citation context without pasting long logs. |
| Power user | Manage handles, tags, batches, indexes, and static-site publication. |
| Maintainer | Validate citation integrity, preserve append-only history, and ship predictable releases. |
| Publisher | Publish metadata-safe citation sites through GitHub Pages or another static host. |

## Business Goals

1. Make citation creation simple enough for non-developers.
2. Make citation state portable enough for agents and future conversations.
3. Avoid source artifact pollution from markers, comments, or hidden metadata.
4. Enable local ownership of citation history.
5. Support static publication without a hosted service requirement.
6. Preserve trust through append-only audit history.
7. Keep the core small enough to integrate with many tools.

## Non-Goals

- Replace document editors, note apps, Git, MkDocs, browsers, or IDEs.
- Provide semantic truth judgments.
- Modify cited artifacts to store citation markers.
- Require a server for local citation workflows.
- Require Git for cited artifacts.
- Build every UI integration before the core contracts stabilize.

## Product Requirements

| ID | Requirement | Priority | Acceptance |
|---|---|---:|---|
| BR-001 | Users can create a citation from selected evidence. | Must | `cite-selection` works; source-byte test proves the artifact is unchanged. |
| BR-002 | Agents can create multiple citations at once. | Must | `cite-batch` preserves all-or-nothing default and explicit partial semantics. |
| BR-003 | Users can add or rename handles after citation creation. | Must | A handle-binding event preserves the immutable citation ID and replay resolves aliases. |
| BR-004 | Human tools can offer cited-region actions without becoming authority. | Must | `lookup-actions` supplies an integration contract; any right-click UI is a separate, explicitly tested transport. |
| BR-005 | Overlapping citations are manageable. | Must | Multiple matches have deterministic, documented ordering and a mutation requires a chosen citation ID. |
| BR-006 | Citation history is publishable as a site. | Must | `export` generates deterministic MkDocs-compatible projections. |
| BR-007 | Default publication does not expose evidence text. | Must | A no-leak fixture proves `metadata_only` suppresses accepted and observed evidence. |
| BR-008 | Citation collections can be grouped and indexed. | Must | Deterministic indexes exist by artifact, handle, tag, status, and batch. |
| BR-009 | Users can inspect current implementation status. | Should | The status matrix cites tests, command checks, or explicit gaps for every capability. |
| BR-010 | The project has release-quality orientation docs. | Should | Orientation, decision records, and external narratives are present, linked, and distinguish target from current behavior. |

## Success Metrics

- A new user can initialize a citation repo and create a citation in under five
  minutes using documented commands.
- An agent can cite at least five selections in one batch and receive
  deterministic JSON output.
- A published metadata-only site can be generated without evidence text, proven
  by a negative-content test rather than a policy declaration.
- Every citation appears in grouped indexes after export, proven by an index
  membership fixture.
- All mutating commands append events and pass source-clean tests.
- Every command failure path returns structured JSON.

## Release Acceptance

v0.3.0 is acceptable when:

1. first-slice commands are implemented and tested;
2. grouping/indexing is implemented and tested;
3. BRD, DRD, TRD, specifications, whitepaper, workflows, and ADRs are present
   and their links validate;
4. README has working quickstart;
5. validation commands pass from a clean checkout;
6. no public default export leaks evidence text.

## Constraints

- Python stdlib core unless a dependency is explicitly justified.
- Local-first operation.
- Append-only authority.
- Metadata-only publication by default.
- Git optional for cited artifacts.
- Integrations cannot become authority.

## Risks

| Risk | Business Impact | Mitigation |
|---|---|---|
| UX becomes CLI-first for humans | Low adoption by non-developers. | Preserve right-click contract as primary human workflow. |
| Publication leaks content | Trust failure. | Default metadata-only export and privacy tests. |
| Grouping is weak | Citation sites feel like raw logs. | Prioritize grouping/indexing before broader adapters. |
| Core over-expands into integrations | Maintenance burden. | Keep integrations as thin clients over JSON contracts. |
| Handles become identity | Broken links and audit ambiguity. | Keep immutable citation IDs and audited handle refs. |
| Documentation promises a target feature | Users or agents rely on unavailable behavior. | Use current/target labels and make the status matrix release-gating evidence. |
