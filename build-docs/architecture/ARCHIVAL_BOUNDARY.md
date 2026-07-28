# Archival Boundary

**Status:** active architecture boundary.

## Purpose

This document defines the clean break between the historical v0.3/v1
Cite2Site authority model and the replacement protocol.

The historical model is preserved for audit and design history in the sibling
folder `Cite2Site-Archival/` and in Git history. It is not an active runtime
contract, compatibility target, migration input, or conformance suite for the
replacement implementation.

## Historical Material

Historical v0.3/v1 material includes the old protocol and implementation
specifications, stable contract, schema inventory, schemas, examples,
compatibility corpus, phase prompts, guides, release docs, integration
examples, tests, and old user/agent workflow descriptions.

The stable historical reference for the interrupted baseline is
`../Cite2Site-Archival/from-integration-gate9-finalization-b4b741d/` plus
commit `9b761e2b05298313425e6d5b0c2033c08dfed114` on
`integration/gate9-finalization`.

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

Archived documents must not appear in the active repository reading order,
active schema index, active conformance tests, or release guidance. When
referenced, they must be named as **Historical**, **Superseded**, and
**Unsupported by the active runtime**, and the reference must point outside the
repo or to Git history.
