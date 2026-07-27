# Product Overview — Cite2Site v1.0

Most citation tools solve half the problem: they help you mark a passage, and
then they stop paying attention. Cite2Site is built around the other half —
what happens to that citation six months later, after the file has been
edited, reformatted, or replaced.

Every citation is recorded outside the file it points to, in an append-only,
hash-chained history. The source is never modified. That history can be
replayed at any time to ask: does the evidence still say what it said when it
was cited? The answer is always one of a small number of honest states —
still valid, changed, missing, ambiguous, or, when the tool genuinely can't
verify (a page it can't safely re-fetch, a format it doesn't yet support), it
says that plainly instead of returning a false positive.

That last part is the design choice that matters most. A citation tool that
confidently reports "valid" when it actually has no way to know is worse than
one that admits uncertainty — especially once agents, not just people, are
the ones creating and relying on citations without a human checking every
one. Cite2Site is built to fail honestly.

## Architecture Over Breadth

Rather than a bespoke parser per file type, Cite2Site separates *how you get
canonical text out of an artifact* from *how citation history, verification,
and replay work.* The first part is a thin, swappable adapter — often just an
existing converter (pandoc for DOCX, pdftotext for PDF). The second part is
one model, built once, reused everywhere. New formats extend the first part
without touching the second.

For browser pages, a Readability-based re-observation path can re-extract
canonical text from static/server-rendered pages without a live browser
session. JS-rendered or authenticated pages get an honest
`adapter_unavailable` rather than a false comparison against content the user
never saw.

## What Ships Today

- **Filesystem text and Markdown adapters** — create citations without
  touching the source file.
- **ConverterAdapter** — DOCX via pandoc, PDF via pdftotext, XLSX via
  a specified converter. Same architecture, same verification logic.
- **15 CLI commands** — init, cite-selection, cite-batch, set-handle,
  accept-current, retract, restore, relocate, note, lookup-actions,
  status, citations, export, check, preflight-selection.
- **Append-only event model** — hash-chained JSONL histories, validated
  by `c2s check`.
- **4 privacy modes** — metadata_only (default), hash_only, policy-gated
  snippet and private_link.
- **Grouped exports and MkDocs site** — organized by artifact, handle,
  tag, status, and batch.
- **Deterministic replay** — same histories + same artifacts → same output,
  every time.
- **Structured errors** — 38 stable C2SError codes, machine-readable.

## Honest Failure

Inline comments and footnotes rot the moment the file changes underneath
them. Screenshots and copy-pasted quotes have no way to tell you when
they've gone stale. Cite2Site's citations live outside the file and check
themselves against it — so staleness is something you're told about, not
something you discover later.
