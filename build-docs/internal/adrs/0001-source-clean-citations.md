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

## Consequences

- Cited artifacts remain ordinary files.
- C2S must maintain locators and accepted evidence externally.
- Some integrations may display overlays, but overlays are projections only.
- Adapter quality matters because source markers are not available as anchors.
