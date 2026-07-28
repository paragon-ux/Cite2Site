# Product Overview - Cite2Site v1.0

**Status:** historical v0.3/v1 narrative pending replacement rewrite.

The active replacement protocol is defined by the refined reconciliation RFC
and archival boundary. This overview is preserved for history only.

Cite2Site is a source-clean citation tool that records evidence outside your
files so the files themselves never change. Create a citation from selected
text, and Cite2Site stores it in an append-only, hash-chained history.
Replay that history at any time to check whether the evidence still holds —
still there, changed, or gone.

## What Works Today

Cite2Site v1.0 ships as a CLI with 15 commands covering the full citation
lifecycle:

- **Create citations** from text and Markdown files — `cite-selection`,
  `cite-batch`, `preflight-selection`.
- **Manage handles** — bind, rename, alias, retire — `set-handle`.
- **Query state** — find citations by artifact, handle, tag, status, or
  batch — `citations`, `status`, `lookup-actions`.
- **Recover from change** — accept updated evidence, retract, restore,
  relocate, annotate — `accept-current`, `retract`, `restore`, `relocate`,
  `note`.
- **Publish** — export grouped JSON indexes and a MkDocs site with
  metadata-only privacy by default — `export`.
- **Verify integrity** — validate hash chains across the entire citation
  history — `check`.

Everything is deterministic: same histories + same artifacts = same output,
every time. 98 tests cover the engine.

## Architecture

Cite2Site separates *how you get text out of an artifact* from *how citation
history, verification, and replay work.* The first part is a thin adapter
layer: text and Markdown are built-in; DOCX, PDF, and XLSX use a
**ConverterAdapter** that shells out to standard tools (pandoc, pdftotext)
rather than requiring bespoke parsers. New formats extend the adapter layer
without touching the replay engine.

For browser pages, a Readability-based re-extraction path is specified for
static/server-rendered content. When a format genuinely can't be verified
(JS-rendered pages, authenticated content), Cite2Site reports the limitation
rather than guessing.

## Honest by Design

Most citation tools solve half the problem: they help you mark a passage,
then stop paying attention. Cite2Site is built around the other half — what
happens to a citation months later, after the file has been edited,
reformatted, or replaced. The answer is always one of a small set of real
states: resolved, changed, missing, or retracted. When it can't determine the
answer, it says so — it won't return a false "valid" against content it never
saw.
