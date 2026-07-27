# Product Overview

Cite2Site lets people and agents create durable citations from ordinary files
without adding markers to those files. A user can cite a passage, generate a
local citation site, and share a metadata-safe publication projection without
turning the cited file into a C2S document.

## What Exists Today

The current local first slice is a JSON CLI and replay engine for text and
Markdown files. It can create source-clean citations, accept batches, assign
handles, look up contextual actions, replay status, export grouped local
projections, and verify event histories. It is useful now for people
comfortable with a command line and for agents that use structured commands.

Status, the CLI, and generated MkDocs pages already group/query citations by
artifact, handle, tag, status, and batch. The intended right-click experience
and richer artifact adapters are not yet shipped. They are the next layers over
the same citation contracts, rather than a second state system.

## Primary Promise

```text
select evidence -> source-clean citation history -> inspectable projection
```

A native right-click integration is the target human transport for the first
step. Cite2Site itself remains responsible for the source-clean history and
replay, regardless of whether the selection originated in an editor, browser,
or command line.

## What It Does

- Records accepted evidence externally in a dedicated citation repository.
- Keeps source artifacts unchanged.
- Lets handles be added or renamed later.
- Lets agents create citations one at a time or in batches.
- Replays citation history against current files.
- Generates JSON and MkDocs projections.
- Enforces `metadata_only` by default and requires explicit repository policy
  for snippet or private-link projections.

## Who It Serves

- Everyday users who do not want CLI-heavy citation workflows.
- Agents that need deterministic citation context.
- Researchers and writers building durable evidence indexes.
- Maintainers publishing citation sites for projects.
- Power users managing handles, tags, batches, and status review.

## Near-Term Direction

Cite2Site has a working local first slice with deterministic replay indexes,
query filters, grouped site navigation, and enforced privacy modes. The next
product step is completing append-only recovery workflows.

The project does not judge whether a source is true. It records evidence that a
person, agent, or machine explicitly accepted, and later reports how that
evidence compares with the current artifact observation.
