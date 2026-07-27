# ADR 0002: Dedicated Citation Repository

## Status

Accepted

## Context

Not every cited artifact is part of a Git project. Citation history also needs
its own privacy and publication policy.

## Decision

Cite2Site stores authority in a dedicated `.c2s` citation repository. The cited
artifact may live inside that repository, beside it, or in a separate folder.

## Consequences

- Cited artifacts do not require Git.
- Citation history can be published independently.
- Users can carry citation context across projects and conversations.
- Export and site generation operate from `.c2s`.
