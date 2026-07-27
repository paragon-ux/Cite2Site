# ADR 0010: Generated Projections Are Safe And Replaceable

## Status

Accepted

## Context

G3 turns replay indexes into JSON and MkDocs projections. Artifact URIs, tags,
and handles can be user-controlled, while a later replay can remove a group or
change its status. Direct rendering risks Markdown/HTML injection; weak slug
collision handling can overwrite pages; and retaining pages from an earlier
replay makes a generated site disagree with the current authority history.

## Decision

Treat all generated projection files as replaceable output. Render every
user-controlled display value with Markdown-safe escaping, generate slugs with
deterministic collision resolution that is rechecked for uniqueness, and remove
the known group directories before rebuilding them. Individual generated files
are atomically replaced where practical. Projection-write failures become
structured errors; successful authority mutations remain independent of any
later projection refresh.

## Alternatives Considered

- Render metadata verbatim. This is simpler but lets a citation label alter
  published Markdown or HTML.
- Preserve old group pages for incremental speed. This leaves stale pages that
  no longer describe replayed state.
- Make generated pages authority so they can be repaired manually. This breaks
  the source-of-truth boundary and duplicates event history.

## Consequences

- A successful export contains only the group pages represented by that replay.
- Generated names and content are deterministic and safe to publish once the
  applicable privacy policy permits publication.
- An interrupted export may require rerunning export, but it cannot alter
  citation or handle authority.

## Implementation Implications

- Export code must escape display content, use collision-safe slugs, prune
  only known generated directories, and surface `E_PROJECTION_WRITE` on I/O
  failure.
- Tests must cover adversarial group keys, collision chains, stale-group
  removal, deterministic regeneration, and source cleanliness.

## Validation Hooks

- G3 grouped-export, link-integrity, deterministic-output, and source-clean
  tests.
- Security review of generated Markdown and projection-write failure paths.
