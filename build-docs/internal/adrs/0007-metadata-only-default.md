# ADR 0007: Metadata-Only Publication Default

## Status

Accepted

## Context

Cited artifacts can include private, sensitive, copyrighted, or third-party
content. A citation site should be safe to publish by default.

## Decision

Public export defaults to `metadata_only`. Evidence text is excluded unless a
repository policy explicitly enables a richer mode.

## Alternatives Considered

- Publish complete evidence by default. This risks exposing private,
  copyrighted, or third-party content.
- Make every project choose a mode during initialization. This creates an easy
  path to unsafe defaults and harms quick local adoption.
- Treat hashes as a replacement for policy. Hashes are useful identifiers but
  do not decide whether snippets or links are safe to publish.

## Consequences

- Default publication is safer.
- Snippet and private-link modes require explicit policy and tests.
- Agents can still use IDs, handles, hashes, status, tags, and artifact
  metadata.

## Implementation Implications

- Project metadata declares publication policy and the CLI defaults to
  `metadata_only`.
- Every export path must apply the policy before serialization.
- Richer modes require an explicit transform contract, not merely an accepted
  option name.

## Validation Hooks

- BR-007, DR-008, and TR privacy requirements.
- Negative-content tests proving accepted and observed evidence text is absent
  from metadata-only JSON and Markdown output.
- Policy-refusal tests for disallowed snippets and private links.
