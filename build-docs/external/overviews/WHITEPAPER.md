# Cite2Site Whitepaper

**Status:** external product and architecture narrative.

## Abstract

Cite2Site is a source-clean universal citation system for humans, agents, and
automation. It lets users cite evidence from ordinary files without inserting
markers, comments, bookmarks, or platform-specific references into the source.
Citation history is stored externally in an append-only repository, replayed
against current artifacts, and projected into JSON and MkDocs pages that can be
published through ordinary static hosting.

## Problem

People increasingly work across documents, code, exported conversations,
spreadsheets, PDFs, and web pages. They need durable citations that can survive
future work and be understood by agents. Existing approaches often require one
of three compromises:

1. write markers into the source artifact;
2. rely on a proprietary note or knowledge platform;
3. copy context manually into each future workflow.

Each compromise is costly. Markers are not universal. Proprietary platforms
limit portability. Manual context transfer is brittle and hard for agents to
verify.

## Thesis

Universal citations should be source-clean, append-only, and replayable.

Source-clean means the cited artifact remains ordinary. Append-only means
history is auditable. Replayable means current projected state can be computed
from citation history plus current artifact observations without trusting hidden
UI state or semantic inference.

## Core Model

```text
citation history + handle bindings + artifact observations + policy
= projected citation state
```

Citation history stores accepted evidence and locators. Handle bindings store
editable aliases over immutable citation IDs. Artifact observations are read
through adapters. Policy controls privacy and publication. Projected state is
generated from those inputs.

## Why Not Markers

Markers are useful in controlled environments, but they are not universal.
Many cited artifacts cannot or should not be modified:

- third-party PDFs;
- exported chatbot conversations;
- websites and snapshots;
- shared policy documents;
- code owned by another project;
- spreadsheets and documents with strict formatting.

Cite2Site keeps citation state outside the artifact so the same citation model
can apply across these surfaces.

## Why A Dedicated Citation Repository

The citation repository gives C2S a stable home without requiring the cited
artifact to use Git. It can be a standalone folder, a Git repo, or a publishing
source for GitHub Pages. This separation supports:

- non-Git artifacts;
- independent privacy policy;
- durable citation history;
- site publishing;
- reuse across future conversations and agents.

## Humans First, Agents First

Cite2Site is designed for both humans and agents.

Humans need simple interactions:

```text
right click uncited selection -> Cite with C2S
right click cited region -> Rename handle / Add alias / Undo / Redo / Open
```

Agents need deterministic commands:

```text
cite-selection
cite-batch
set-handle
lookup-actions
status
export
check
```

These are not competing models. Right-click integrations call the same core
contracts that agents use.

## Handles As Editable Refs

Citation IDs are immutable. Handles are friendly aliases. A handle can be
created, renamed, aliased, or retired by appending a handle-binding event. Old
handles should remain aliases by default so published references continue to
resolve.

This mirrors a useful property of version-control refs without making Git a
requirement for cited artifacts.

## Replay Instead Of Lifecycle Mutation

Citations do not become stale or refresh themselves. A citation has accepted
evidence in history. Replay may observe that the current artifact differs,
cannot be found, or matches the accepted evidence. That projection can change,
but the accepted history remains intact.

This prevents accidental authority from creeping into parsers, overlays,
semantic guesses, or background services.

## Publishing As A Projection

MkDocs is the first publication path because it is local, customizable, and easy
to deploy through static hosts. The generated site is not authority. It is a
readable projection that helps people and agents navigate citation history.

Default publication is metadata-only. Evidence text is not published unless
repository policy explicitly allows it.

## Grouping And Indexing

Flat citation lists are not enough. Cite2Site needs indexes by:

- artifact;
- handle and alias;
- tag;
- status;
- batch;
- chronology.

These indexes make citation sites useful as durable memory across future work,
including future chatbot sessions.

## Security And Privacy

Cite2Site must assume cited artifacts can contain private or third-party
content. The default publication mode is therefore metadata-only. Hash-only,
snippet, and private-link modes require explicit policy.

No adapter should infer evidence from semantic similarity or surrounding
context. Unsupported or ambiguous evidence must fail closed.

## Conclusion

Cite2Site turns citation into a portable local primitive: right-click evidence,
append source-clean citation history, replay deterministic state, and publish a
site that people and agents can inspect. The project succeeds by staying small
at the authority layer and letting editors, browsers, document tools, Git, and
MkDocs do what they already do well.
