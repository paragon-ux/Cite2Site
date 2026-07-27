# Glossary

**Status:** current internal terminology control.

| Term | Definition |
|---|---|
| Accepted evidence | Canonical evidence content the user, agent, or machine explicitly cited. |
| Adapter | Code that identifies, canonicalizes, locates, observes, summarizes, and privacy-filters one artifact type. |
| Alias | Historical or secondary handle that resolves to a citation ID. |
| Artifact | A cited source item such as a text file, Markdown file, exported chat, PDF text layer, or future adapter-supported object. |
| Artifact index | Projection/index of artifacts that have citations. It is generated or appended from citation history, not source authority. |
| Batch | A group of citation events created in one request with a shared `batch_id`. |
| Citation history | Append-only JSONL event file containing citation events. Authority file: `.c2s/citation-history.jsonl`. |
| Citation ID | Immutable content-addressed identity for a citation. Handles do not replace it. |
| Citation repository | Dedicated `.c2s` repository storing C2S authority and generated projections. |
| Contextual action | Action returned by `lookup-actions` for a cursor, selection, or range. |
| Current observation | Evidence read from an artifact during replay. It may differ from accepted evidence without changing the citation history. |
| Documentation authority | The role a document plays: explanation, decision, requirement, current-state report, or architecture contract. |
| Evidence hash | SHA-256 hash of canonical accepted evidence. |
| Handle | Editable human/agent alias over a citation ID. |
| Handle binding history | Append-only JSONL event file containing handle bind, rename, alias, and retire events. |
| Locator | Adapter-specific coordinates for evidence in an artifact. |
| Metadata-only | Publication mode that excludes evidence text. |
| Projection | Generated status, JSON index, or MkDocs page derived from history and observations. Not authority. |
| Replay | Deterministic reduction of citation history, handle bindings, artifact observations, and policy into projected citation state. |
| Source-clean | C2S does not modify cited artifacts to store citation state. |
| Target contract | Approved behavior that is specified and testable in principle but is not necessarily present in the current runtime. |
| Truth label | A maturity label: Implemented, Partial, Target, or Open. See `DOCUMENTATION_STANDARD.md`. |

## Forbidden Terminology

- Do not call citations stale.
- Do not describe citation refresh.
- Do not call overlays authority.
- Do not describe handles as citation identity.
- Do not describe generated pages as source of truth.
- Do not describe an intended editor integration as currently available without
  identifying it as a target contract.
