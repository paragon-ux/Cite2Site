# ADR 0007: Metadata-Only Publication Default

## Status

Accepted

## Context

Cited artifacts can include private, sensitive, copyrighted, or third-party
content. A citation site should be safe to publish by default.

## Decision

Public export defaults to `metadata_only`. Evidence text is excluded unless a
repository policy explicitly enables a richer mode.

## Consequences

- Default publication is safer.
- Snippet and private-link modes require explicit policy and tests.
- Agents can still use IDs, handles, hashes, status, tags, and artifact
  metadata.
