# Cite2Site Project Plan

**Status:** active replacement project plan.

## Objective

Build Cite2Site around a clean replacement protocol that preserves every
intentional citation, organizes citations through stable groups and
group-owned handles, applies scoped duplicate policy without deleting history,
and reconciles branches deterministically through semantic authority operations.

The v0.3/v1 implementation is historical. It is not an active compatibility
target and must not drive new feature work.

## Success Definition

Cite2Site succeeds under the replacement protocol when:

1. cited artifacts remain source-clean;
2. every mutating command writes one completed atomic operation;
3. every mutation requires an `idempotency_key`;
4. distinct intentional citations receive distinct record-instance
   `citation_id` values;
5. every citation has a deterministic `target_fingerprint`;
6. every repository has a default group;
7. groups have immutable `group_id` values and complete rolling tallies;
8. handles have immutable group-owned `handle_id` values and complete rolling
   tallies;
9. duplicate policy is scoped to group membership or handle binding;
10. scoped supersession never globally retracts or erases a citation;
11. semantic reconciliation preserves independent branch operations and is
    merge-direction independent;
12. archived-format repositories fail closed before reads or writes;
13. metadata-only publication remains the default;
14. tests and docs distinguish replacement behavior from historical v0.3/v1
    behavior.

## Gate Plan

| Gate | Status | Goal |
|---|---:|---|
| R0: Archival separation | Done | Move archived files outside the repo and replace active docs with replacement authority. |
| R1: Repository identity | Done | Define and implement replacement repository schema, initialization, and archived-format rejection. |
| R2: Atomic operations | Done | Implement operation envelope, completed records, idempotency, and completed-operation replay. |
| R3: Citations and fingerprints | Done | Implement record-instance citation IDs and deterministic target fingerprints. |
| R4: Groups and memberships | Partial | Implement default Inbox, group hierarchy, memberships, and group rolling tallies. |
| R5: Handles and bindings | Partial | Implement stable handle IDs, handle names/aliases, ambiguity, and handle rolling tallies. |
| R6: Duplicate policy | Partial | Implement handle/group/none policies and scoped supersession. |
| R7: Reconciliation | Partial | Implement semantic branch reconciliation for replacement repositories only. |
| R8: Projections and publication | Partial | Implement replacement status/export/site projections with metadata-only default. |
| R9: Integrations and Chrome extension | Actionable | Replacement-aware native-host and extension contract are installed for manual validation. |

## Out Of Scope

- Runtime migration from v0.3/v1 repositories.
- Dual reducers, version switches, or transparent fallback.
- Automatic import of archived histories.
- Compatibility with archived Chrome-extension command/message shapes.

## Definition Of Done

A replacement capability is Done only when behavior, tests, docs, schemas,
status rows, and security/privacy expectations agree. Historical v0.3/v1 tests
do not prove replacement conformance.
