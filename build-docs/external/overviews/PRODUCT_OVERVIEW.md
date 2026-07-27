# Product Overview

Cite2Site lets people and agents create durable citations from ordinary files
without adding markers to those files. A user can cite a passage, publish a
metadata-safe citation site, and share that site with future collaborators or
chatbot sessions.

## What Exists Today

The current local first slice is a JSON CLI and replay engine for text and
Markdown files. It can create source-clean citations, accept batches, assign
handles, look up contextual actions, replay status, export a flat local site,
and verify event histories. It is useful now for people comfortable with a
command line and for agents that use structured commands.

The intended right-click experience, grouped navigation, and richer artifact
adapters are not yet shipped. They are the next layers over the same citation
contracts, rather than a second state system.

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
- Defaults public output to metadata-only.

## Who It Serves

- Everyday users who do not want CLI-heavy citation workflows.
- Agents that need deterministic citation context.
- Researchers and writers building durable evidence indexes.
- Maintainers publishing citation sites for projects.
- Power users managing handles, tags, batches, and status review.

## Near-Term Direction

Cite2Site has a working local first slice. The next product step is grouped
indexing so citation sites are navigable by artifact, handle, tag, status, and
batch instead of only showing a flat list.

The project does not judge whether a source is true. It records evidence that a
person, agent, or machine explicitly accepted, and later reports how that
evidence compares with the current artifact observation.
