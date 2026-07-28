# Glossary

**Status:** current internal terminology control.

| Term | Definition |
|---|---|
| Accepted evidence | Canonical evidence content the user, agent, or machine explicitly cited. |
| Adapter | Code that identifies, canonicalizes, locates, observes, summarizes, and privacy-filters one artifact type. |
| Alias | Secondary display name for a group or handle. Alias state does not create another authority object. |
| Artifact | A cited source item such as a text file, Markdown file, exported chat, PDF text layer, or future adapter-supported object. |
| Artifact index | Derived projection of artifacts that have citations. It is not authority. |
| Batch | A set of mutation items governed by batch and item idempotency keys. |
| Citation history | Historical v0.3/v1 term for archived event files. Replacement authority is completed operations. |
| Citation ID | Immutable record-instance identity for one intentional citation. It is not derived solely from evidence identity. |
| Citation repository | Dedicated `.c2s` repository storing C2S authority and generated projections. |
| Completed operation | Atomic replacement authority record with `operation_id`, `idempotency_key`, command, semantic payload hash, status, and events. |
| Contextual action | Action returned by `lookup-actions` for a cursor, selection, or range. |
| Current observation | Evidence read from an artifact during replay. It may differ from accepted evidence without changing the citation history. |
| Documentation authority | The role a document plays: explanation, decision, requirement, current-state report, or architecture contract. |
| Evidence hash | SHA-256 hash of canonical accepted evidence. |
| Group | Stable folder-like citation container identified by immutable `group_id`. |
| Handle | Stable group-owned name object identified by immutable `handle_id`. |
| Handle binding history | Historical v0.3/v1 term for archived handle event files. Replacement bindings are completed operation events. |
| Locator | Adapter-specific coordinates for evidence in an artifact. |
| Metadata-only | Publication mode that excludes evidence text. |
| Projection | Generated status, JSON index, or MkDocs page derived from history and observations. Not authority. |
| Replay | Deterministic reduction of completed operations, artifact observations, and policy into projected citation state. |
| Rolling tally | Complete ordered record of distinct citations that have belonged to a group or handle. |
| Scoped supersession | Duplicate-policy result that changes group membership or handle binding state without globally retracting a citation. |
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
