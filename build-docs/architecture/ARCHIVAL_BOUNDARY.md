# Archival Boundary

**Status:** active architecture boundary.

## Purpose

This document defines the clean break between the historical v0.3/v1
Cite2Site authority model and the replacement protocol.

The historical model is preserved for audit and design history. It is not an
active runtime contract, compatibility target, migration input, or conformance
suite for the replacement implementation.

## Historical Material

Historical v0.3/v1 material includes:

- `build-docs/architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md`;
- `build-docs/architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md`;
- `build-docs/architecture/V1_STABLE_CONTRACT.md`;
- `build-docs/architecture/SCHEMA_INDEX.md`;
- `build-docs/architecture/schemas/`;
- `build-docs/architecture/examples/`;
- `build-docs/internal/COMPATIBILITY_CORPUS.md`;
- old v0.3/v1 user, agent, workflow, and integration guidance where it
  describes string handles, evidence-derived citation IDs, or the two-ledger
  authority model.

The stable historical reference for the interrupted baseline is commit
`9b761e2b05298313425e6d5b0c2033c08dfed114` on
`integration/gate9-finalization`. Git history remains the primary archive.

## Active Replacement Authority

The active authority chain is:

1. `build-docs/architecture/policies/OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V3.md`;
2. `build-docs/architecture/policies/OFFICIAL_PROTOCOL_MIGRATION_V2.md`;
3. `build-docs/architecture/ARCHIVAL_BOUNDARY.md`;
4. `build-docs/architecture/CITE2SITE_REPLACEMENT_IMPLEMENTATION_SPEC.md`;
5. `build-docs/architecture/REPLACEMENT_SCHEMA_INDEX.md`;
6. active requirements, workflow, status, gate prompts, and ADRs that
   explicitly reference the replacement protocol.

## Runtime Rule

Archived-format repositories must fail closed before replay, mutation,
reconciliation, projection, or publication.

The replacement runtime must not:

- load v0.3/v1 ledgers as current authority;
- convert legacy string handles into replacement handle objects;
- preserve evidence-derived citation IDs as active identity;
- run old and new reducers side by side;
- provide transparent fallback to archived behavior;
- claim automatic upgrade or compatibility with archived repositories.

Any future import utility requires a separate authorization, contract, and
security review. This boundary does not authorize one.

## Documentation Rule

Archived documents must not appear in the active reading order or active
schema index. When referenced, they must be named as **Historical**,
**Superseded**, and **Unsupported by the active runtime**.
