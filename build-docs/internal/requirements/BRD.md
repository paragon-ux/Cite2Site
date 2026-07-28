# Business Requirements

**Status:** active replacement requirements.

## Purpose

Cite2Site must let people and agents cite evidence without altering cited
artifacts, while preserving every intentional citation and making branch
reconciliation deterministic.

## Requirements

| ID | Requirement | Priority | Verification |
|---|---|---:|---|
| BR-001 | Cited artifacts remain byte-for-byte unchanged by every citation, lookup, projection, publication, and reconciliation command. | Must | Source-clean regression tests in R3, R8, and R9. |
| BR-002 | Every intentional citation receives a distinct record-instance `citation_id`. | Must | Duplicate-evidence creation tests in R3. |
| BR-003 | Repeated execution of the same logical mutation is suppressed only by `idempotency_key`. | Must | Same-key retry and conflict tests in R2. |
| BR-004 | Users organize citations through stable groups and group-owned handles. | Must | Group and handle identity tests in R4 and R5. |
| BR-005 | Duplicate handling is scoped and reversible without deleting history. | Must | Scoped supersession tests in R6. |
| BR-006 | Branches reconcile by semantic operation replay, not text-merging authority files. | Must | Deterministic reconciliation tests in R7. |
| BR-007 | Publication defaults to metadata-only. | Must | No-leak projection tests in R8. |
| BR-008 | Archived v0.3/v1 repositories fail closed before reads or writes. | Must | Archived-format rejection tests in R1. |
| BR-009 | Browser integration uses the replacement contract and does not own authority. | Must | Native-host fixture tests, package build, and manual Chrome validation in R9. |

## Out Of Scope

- Runtime migration from archived repositories.
- Transparent compatibility with v0.3/v1 command behavior.
- Source markers inside cited artifacts.
