# ADR 0002: Dedicated Citation Repository

## Status

Accepted

## Context

Not every cited artifact is part of a Git project. Citation history also needs
its own privacy and publication policy.

## Decision

Cite2Site stores authority in a dedicated `.c2s` citation repository. The cited
artifact may live inside that repository, beside it, or in a separate folder.

## Alternatives Considered

- Require the cited artifact's repository to own C2S state. This excludes
  non-Git artifacts and couples citation policy to an unrelated project.
- Operate a shared server as the authority. This adds availability, identity,
  and deployment dependencies to a local citation primitive.
- Store authority only in generated site output. This makes publication a hidden
  state store and weakens auditability.

## Consequences

- Cited artifacts do not require Git.
- Citation history can be published independently.
- Users can carry citation context across projects and conversations.
- Export and site generation operate from `.c2s`.

## Implementation Implications

- `init` creates project metadata, history files, and projection directories.
- Artifact URIs are resolved relative to the citation repository workspace.
- Publication policy belongs to project metadata, not to an editor integration.

## Validation Hooks

- `TR-101` through `TR-104`.
- Fresh-repository CLI smoke test.
- Replay and export tests using an artifact outside the `.c2s` directory.
