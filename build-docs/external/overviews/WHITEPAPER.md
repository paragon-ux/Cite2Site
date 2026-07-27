# Cite2Site Whitepaper

**Status:** external product and architecture narrative.

## Abstract

Cite2Site is a source-clean, universal citation system for humans, agents,
and automation. It lets a person or a process cite evidence drawn from an
ordinary file without leaving a single mark on that file. The current first
slice supports text and Markdown files; the architecture is designed to extend
to documents, exported conversations, PDFs, and other adapter-supported
artifacts without changing the authority model. The citation itself is
recorded elsewhere, in an append-only repository built to be replayed rather
than trusted at face value. From that history, Cite2Site projects JSON
records and MkDocs pages that can be published through ordinary static
hosting, and consulted, months or years later, by a person or an agent who
was not present when the citation was made.

## Problem

Work today is scattered across documents, code, exported conversations,
spreadsheets, PDFs, and web pages, and it increasingly involves collaborators
who are not human. A citation made in one of these surfaces needs to survive
the ordinary entropy of a long-lived project — files get renamed, moved,
rewritten, reformatted — and it needs to be legible to an agent that has no
memory of the conversation in which the citation was first made. Most
existing approaches ask the user to accept one of three compromises:

1. write a marker into the source artifact;
2. adopt a proprietary note or knowledge platform and re-home the material
   inside it;
3. carry the context by hand, copying it into whatever workflow comes next.

None of these compromises is free. A marker presumes the artifact is yours
to modify, which is often false — the artifact may be a shared PDF, a
colleague's code, an exported transcript, or a spreadsheet whose layout is
load-bearing. A proprietary platform solves durability by trading away
portability: the citation is only as durable as your subscription and only
as legible as that platform's export format allows. And manual context
transfer is simply brittle — it depends on a human remembering to do it,
doing it consistently, and doing it correctly, none of which scales, and
none of which an agent can verify after the fact.

## Thesis

A citation, to be worth relying on later, should be source-clean,
append-only, and replayable — three properties that, taken together, are
really one property: verifiability without trust.

Source-clean means the cited artifact is never asked to carry citation
state; it remains exactly what it always was, and can be inspected,
diffed, or handed to someone else without any hidden annotation attached.
Append-only means the citation's history is a ledger, not a document —
nothing is edited in place, so the full sequence of what was accepted, and
when, remains available for audit. Replayable means that the current,
observable state of a citation — resolved, changed, missing, retracted —
is a pure function of history plus present observation, computed fresh
each time rather than cached as an assumption. A system with these three
properties does not need to ask anyone to take its word for anything; it
can be checked.

## Core Model

```text
citation history + handle bindings + artifact observations + policy
= projected citation state
```

Citation history stores accepted evidence and its locator: what was cited,
and precisely where. Handle bindings store editable aliases layered over
citation IDs that never themselves change. Artifact observations are
readings of the current artifact, taken through an adapter appropriate to
its type. Policy governs what may be published and in what form. Projected
state — the only thing a status command, an export, or a published page
ever shows — is generated fresh from these four inputs, never stored as
authority in its own right.

## Why Not Markers

Markers work well in a controlled environment, where the tool that writes
them also owns the file. That assumption fails constantly in practice.
Consider the artifacts a citation system is most often asked to reference:

- third-party PDFs, which a reader has no license to alter;
- exported chatbot conversations, frozen at the moment of export;
- websites and their snapshots, which belong to someone else entirely;
- shared policy documents, where an inserted comment could itself become a
  liability;
- code owned by another project, where an unsolicited marker is a
  discourtesy at best;
- spreadsheets and other strictly formatted documents, where an extra cell
  or comment can silently break downstream formulas.

Cite2Site keeps all citation state outside the artifact for exactly this
reason: the same, unadorned model of citation should apply whether the
artifact is yours to edit or not. A citation system that only works on
files you own is not a universal citation system — it is a note-taking
feature with a narrower name.

## Why A Dedicated Citation Repository

The citation repository gives Cite2Site a stable home that does not
require the cited artifact to be under version control, or even to sit in
the same directory. It may be a standalone folder, a Git repository in its
own right, or the publishing source behind a GitHub Pages site. That
separation is what makes several other properties possible at once:

- artifacts that are not themselves tracked by Git can still be cited;
- privacy policy can be set independently of whatever policy governs the
  artifact itself;
- citation history persists durably, outside the lifecycle of any single
  editing session;
- the same history can be published as a site;
- the same history can be picked back up by a future conversation or a
  different agent entirely, with no loss of context.

## Humans First, Agents First

Cite2Site is built for two very different users at once, and refuses to
choose between them.

A human wants an interaction simple enough to forget it is a tool at all:

The current first slice provides the same underlying capability through a CLI.
Native right-click integrations are Target clients of that contract, rather
than a feature already supplied by the runtime.

```text
right click uncited selection -> Cite with C2S
right click cited region -> Rename handle / Add alias / Open
```

An agent wants the opposite: something entirely deterministic, with no
ambiguity for a language model to resolve on its own:

```text
cite-selection
cite-batch
set-handle
lookup-actions
status
export
check
```

These are not two designs in competition for the same budget. They are one
design, viewed from two angles — the right-click integration a human uses
calls exactly the same core contracts an agent calls directly. Neither
surface is a special case of the other, and neither can drift out of sync
with the other, because there is only one contract underneath both.

## Handles As Editable Refs

Citation IDs are immutable by design: once evidence is accepted, its
identity is fixed. Handles sit above that identity as friendly, human-
legible aliases, and may be created, renamed, aliased, or retired, each
action recorded as its own handle-binding event rather than an edit to
existing history. Old handles remain valid aliases by default, precisely
so that a link or reference published somewhere else keeps resolving even
after the preferred name has changed.

The analogy worth drawing is to version-control refs: a branch name can
move without disturbing the commits it points to. Cite2Site borrows that
useful separation of naming from identity, without requiring the cited
artifact itself to live inside a Git repository.

## Replay Instead Of Lifecycle Mutation

A citation in Cite2Site does not go stale, and it does not refresh itself.
What exists in history is a fixed record of evidence that was, at some
point, explicitly accepted. What replay adds on top is an honest,
recomputed observation: the current artifact may still match that
evidence, may have visibly changed, may no longer be found, or may have
been retracted outright. That observation can change from one run to the
next as the world changes around it — but the accepted history it is
compared against never does.

This distinction is not a technicality; it is the whole point. The moment
a projection is allowed to quietly become authority — the moment a parser,
an overlay, a semantic guess, or a background service is trusted to decide
what a citation currently means — the system has traded verifiability for
convenience, and it cannot be trusted again without re-auditing everything
it ever touched.

## Publishing As A Projection

MkDocs is the first publication path, chosen because it is local,
easy to customize, and trivial to deploy through ordinary static hosting.
But the generated site is not, itself, an authority — it is a readable
projection of the underlying history, produced so that a person or an
agent has somewhere pleasant to look, not somewhere new to trust.

Publication policy defaults to metadata-only. The first slice records that
default; Phase 02 adds the distinct export transforms and no-leak tests needed
to enforce it across every generated output. The premise remains that a
citation system should never be the reason private or third-party content ends
up somewhere public.

## Grouping And Indexing

A flat list of citations is a ledger, not a memory. To be genuinely useful
across a long-lived project, Cite2Site needs to present its history
grouped along the axes people and agents actually think in:

- by artifact;
- by handle and alias;
- by tag;
- by status;
- by batch;
- by chronology.

These groupings are what turn a citation site from an audit trail into a
navigable body of durable memory — something a future collaborator, human
or agent, can actually orient inside, rather than scroll through.

## Security And Privacy

Cite2Site has to assume, as a baseline, that any cited artifact may
contain private or third-party content it has no right to publish. That
assumption is why the default publication mode is metadata-only, and why
every mode that exposes more — hash-only, snippet, or private-link —
requires an explicit, affirmative policy choice rather than an opt-out.

The same caution applies to how evidence is recognized in the first
place: no adapter is permitted to infer that a passage was cited from
semantic similarity or surrounding context. Where evidence is ambiguous or
an adapter cannot support the artifact type, the correct behavior is to
fail closed and say so, not to guess plausibly and move on.

## Related Work

Cite2Site sits at a crossing point between several existing traditions,
and is worth placing precisely among them, because each solves part of the
same problem and none solves all of it at once.

**In-line annotation tools** — web highlighters such as Hypothes.is,
document annotation layers in PDF readers, and platforms like Genius that
attach commentary to a passage — get closest to Cite2Site's everyday
interaction model, right-click evidence, attach meaning to it. But nearly
all of them store the annotation as a layer bound to a specific rendering
of the artifact, often on a server the user does not control, and none of
them treat the artifact itself as something that must remain provably
unmodified and equally citable regardless of who owns it.

**Graph-based note-taking tools** — Roam Research, Obsidian, and similar
systems built around backlinks — offer a genuinely powerful model for
connecting ideas, and their bidirectional-link primitive is a distant
cousin of Cite2Site's handle. But the citation, in these tools, usually
lives inside material the user has already copied into the tool's own
format; the original artifact is not the thing being referenced, a
transcription of it is. Cite2Site's citation always points back at the
artifact as it exists in the world, not a copy of it.

**Version control itself** — `git blame`, permalinks to a specific commit
and line, and Git notes — is arguably the closest philosophical relative
Cite2Site has. Both are append-only, both are content-addressed, and both
treat history as the thing worth trusting over any single snapshot. Where
they part ways is scope: Git's model only extends to artifacts already
under Git's management, in text Git can diff meaningfully. It has nothing
to offer a PDF, a spreadsheet, or an exported conversation, and it was
never designed to be operated by a language model issuing structured
commands.

**Web archiving and permalinking services** — Perma.cc, the Internet
Archive's Wayback Machine, and the Memento protocol — solve a real and
adjacent problem, link rot, by preserving a copy of a page at the moment
it was cited. That is valuable, but it is a different guarantee: it
preserves the target, not the relationship between a specific accepted
passage and a specific piece of writing that depends on it, and it offers
no notion of a handle, a batch, or a replayable status distinct from "the
archived copy still exists."

**Provenance and citation metadata standards** — the W3C PROV vocabulary,
Dublin Core, and schema.org's citation types — describe, precisely and
usefully, what a citation relationship should mean when exchanged between
systems. They are a grammar, not an implementation; none of them specify
an operational, local-first architecture, an append-only event log, or a
concrete guarantee that the cited artifact remains untouched. Cite2Site
can reasonably be read as one opinionated implementation of the
relationships these standards describe, built for a world where the other
party in the conversation might just as easily be an agent as a person.

Taken together, these traditions establish that every individual piece of
Cite2Site's design has precedent somewhere. What does not yet have
precedent, as far as this document is aware, is their combination: a
citation model that is simultaneously source-clean across arbitrary
artifact types, append-only at the level of raw history rather than
rendered annotation, replayable into a projection rather than cached as a
fact, and built from the outset to be operated by deterministic commands a
language model can issue without guessing.

## Conclusion

Cite2Site turns citation into a small, portable, local primitive: select
evidence through the current CLI or a future native integration, append a
source-clean citation event, replay deterministic state from history and
present observation, and publish a site that a person or an agent can inspect
and trust without having been present for any of it. The project earns that
trust by staying
deliberately small at the layer that matters — the authority layer — and
by leaving everything else to tools that already do their jobs well:
editors, browsers, document readers, Git, and MkDocs. Quality here is not
a separate feature bolted on afterward; it is the entire reason the
architecture is shaped the way it is. A system this easy to audit is, not
coincidentally, a system this easy to trust.
