# ADR 0006: MkDocs As Publication Projection

## Status

Accepted

## Context

Users need citation context that can be shared with people and future agents.
Static sites are portable and easy to host.

## Decision

MkDocs is the first publication projection. C2S generates Markdown and JSON
outputs that MkDocs can serve or publish through static hosting.

## Alternatives Considered

- Run a C2S web service. This adds operational state and a publishing dependency
  that static output does not require.
- Build a bespoke site generator. This duplicates navigation and theme concerns
  that MkDocs already addresses.
- Treat an external knowledge platform as the publication authority. This
  weakens portability and local ownership.

## Consequences

- Publication does not require a C2S server.
- Users can deploy through GitHub Pages or similar hosts.
- Generated pages are projections, not authority.
- Site generation must respect privacy modes.

## Implementation Implications

- Export writes deterministic Markdown and JSON projections under `.c2s/site`
  and `.c2s/exports`.
- MkDocs configuration remains a build input; generated pages are not a source
  of truth.
- Grouped pages and static-host guidance are Target work until export tests
  prove them.

## Validation Hooks

- TR export requirements and DR-007.
- Repeated-export determinism checks, generated-link checks, and MkDocs build
  checks when MkDocs enters the supported toolchain.
