# ADR 0001: Source-Clean Citations

## Status

Accepted

## Context

Cite2Site must work with arbitrary artifacts, including files the user cannot
or should not modify. Markers, comments, bookmarks, and embedded IDs are useful
in controlled systems but are not universal.

## Decision

Cite2Site will not write citation markers into cited artifacts. Citation
authority lives outside the source artifact in the citation repository.

## Alternatives Considered

- Embed handles or IDs directly in source files. This works for controlled text
  formats but excludes third-party, binary, and formatting-sensitive artifacts.
- Maintain editor-specific metadata or overlays. This creates a separate,
  platform-bound authority surface.
- Require a requirement registry. This narrows the product to managed
  requirements rather than universal citation evidence.

## Consequences

- Cited artifacts remain ordinary files.
- C2S must maintain locators and accepted evidence externally.
- Some integrations may display overlays, but overlays are projections only.
- Adapter quality matters because source markers are not available as anchors.

## Implementation Implications

- Citation creation must capture accepted evidence and an explicit locator.
- Tests must compare artifact bytes before and after every mutating command.
- Adapters must fail closed when a selection cannot be represented safely.

## Validation Hooks

- Source-clean test coverage in replacement citation, projection,
  reconciliation, and integration gates.
- Replacement mutation smoke flows with required idempotency keys.
- Privacy and export tests that confirm projections, not artifacts, carry C2S
  metadata.
