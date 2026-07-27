# Phase 04: Adapter Hardening

**Status:** authorized after Phase 03 workflow completeness is accepted.

## Purpose

Make extension to new artifact types safe and testable. Adapters may observe
and canonicalize artifacts; they may not become semantic authorities or infer
citation acceptance from resemblance.

## Required Reading

Read `AGENTS.md`, `DOCUMENTATION_STANDARD.md`, the status matrix, TRD adapter
requirements, the implementation specification adapter contract, and Phase 03
results.

## Scope

Create an adapter conformance harness; harden filesystem-text and Markdown;
add explicit diagnostics and summaries; and add one bounded next adapter only
if its conformance fixtures, privacy behavior, and failure modes are complete.

## Non-Goals

- Do not infer evidence from AST identity, symbols, semantic similarity, or
  surrounding context.
- Do not claim support for PDFs, documents, spreadsheets, browsers, or chats
  merely because an adapter interface exists.
- Do not publish adapter-derived snippets without Phase 02 policy enforcement.

## Adapter Contract Evidence

Every supported adapter must prove, through fixtures:

1. `identify`: stable artifact identity and normalized URI;
2. `canonicalize`: explicit canonical evidence and hash;
3. `locate`: unambiguous locator coordinates and encoding;
4. `observe`: current artifact observation without mutation;
5. `compare`: deterministic resolved/changed/missing/unsupported result;
6. `summarize`: metadata-safe range summary;
7. `privacy`: compliance with every supported publication mode.

## Required Changes

- Define a concrete adapter protocol and conformance test harness.
- Add diagnostics for UTF-8 failure, unsupported content, missing files, and
  ambiguous observations.
- Keep Markdown text semantics explicit until block-aware behavior has a fully
  specified locator and test suite.
- If adding an adapter, add its public limitations to the status matrix and
  external engineering overview in the same gate.

## Required Tests

- Shared conformance fixtures run against every supported adapter.
- Negative tests prove unsupported, invalid, private, and ambiguous cases fail
  closed with stable codes/statuses.
- URI normalization and canonicalization are deterministic across platforms.
- Artifact observations do not mutate source bytes.
- New adapters receive privacy-leak tests in all supported export modes.

## Acceptance Criteria

The phase is accepted only when every claimed adapter passes the complete
conformance suite, unsupported surfaces fail closed, and public docs list the
actual supported adapters rather than architectural aspirations.

