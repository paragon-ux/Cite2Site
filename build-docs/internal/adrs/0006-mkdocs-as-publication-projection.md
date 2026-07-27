# ADR 0006: MkDocs As Publication Projection

## Status

Accepted

## Context

Users need citation context that can be shared with people and future agents.
Static sites are portable and easy to host.

## Decision

MkDocs is the first publication projection. C2S generates Markdown and JSON
outputs that MkDocs can serve or publish through static hosting.

## Consequences

- Publication does not require a C2S server.
- Users can deploy through GitHub Pages or similar hosts.
- Generated pages are projections, not authority.
- Site generation must respect privacy modes.
