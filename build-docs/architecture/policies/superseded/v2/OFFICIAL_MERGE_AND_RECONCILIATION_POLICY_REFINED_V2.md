# RFC: Cite2Site Citation Grouping, Duplicate Tally, and Reconciliation Policy

**Status:** Required
**Category:** Protocol
**Applies to:** Citation creation, handles, groups, browser and editor integrations, agentic batches, replay, indexing, Git reconciliation, and publication

## 1. Conformance

The words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

An implementation conforms only when it satisfies every mandatory requirement in this RFC.

## 2. Core model

Cite2Site has four primary authority objects:

1. **Citation** — one intentional evidence record identified by `citation_id`.
2. **Group** — a stable folder-like container identified by `group_id`.
3. **Handle** — a stable user-owned name and tally inside one group, identified by `handle_id`.
4. **Operation** — one atomic mutation identified by `operation_id` and protected by an `idempotency_key`.

A citation MAY belong to multiple groups.

Within a group, a citation MAY be bound to one active preferred handle.

Every authority history MUST remain append-only. Existing citation, group, handle, membership, binding, mutation, supersession, retraction, restoration, and reconciliation records MUST NOT be rewritten or deleted.

Derived indexes, counts, summaries, and published pages MUST NOT be treated as authority.

Cite2Site MUST preserve every intentional citation. It MUST suppress only repeated execution of the same logical operation through idempotency.

## 3. Citation identity

A `citation_id` identifies one intentional citation record.

Two distinct intentional citation operations MUST receive distinct citation IDs, including when they cite identical evidence in the same group under the same handle.

A retry of the same logical operation MUST return the citation ID allocated to the original successful operation and MUST NOT create another citation or tally entry.

A citation ID MUST NOT be derived solely from evidence identity or `target_fingerprint`.

A citation ID MUST remain unchanged through import, reconciliation, grouping, handle binding, relocation, acceptance, retraction, restoration, supersession, and destination event rehashing.

Citation IDs MUST have one canonical string representation and one canonical total order. Unless a versioned citation-ID schema defines another order, canonical citation IDs MUST be compared by unsigned bytewise lexical order of their canonical UTF-8 strings.

`created_at` MAY be retained for audit and display. It MUST NOT affect duplicate precedence, tally order, reconciliation precedence, or conflict resolution.

## 4. Groups

A group is a stable folder-like authority object.

Every group MUST have an immutable `group_id`.

A group MAY have:

- a mutable display name;
- one parent group;
- aliases;
- a duplicate policy;
- publication or privacy metadata.

Group name and path MUST NOT be group identity.

Renaming or moving a group MUST NOT change its `group_id`, memberships, tally entries, or history.

A group hierarchy MUST be acyclic.

Two independently created groups MUST NOT be automatically collapsed merely because they have the same name or path.

Same-name sibling groups MAY be preserved after reconciliation, but the projection MUST report the path as ambiguous until an explicit rename or group merge resolves it.

Every repository MUST provide a default group for integrations that do not request a group. The default group SHOULD be presented as `Inbox`.

### 4.1 Explicit group merge

Group merge MUST be an explicit authority operation.

A group merge MUST:

1. identify source and destination group IDs;
2. preserve the source group and its complete history;
3. append destination memberships for source citations that are not already represented in the destination tally;
4. preserve membership provenance;
5. preserve every distinct citation;
6. preserve both group rolling tallies without compression;
7. reapply the destination group's duplicate policy;
8. retire, alias, or redirect the source only through explicit events.

A group merge MUST NOT rewrite citation records.

Same-name handles in the two groups MUST NOT be silently merged. The merge operation MUST provide an explicit handle mapping or preserve them as distinct handle IDs.

## 5. Handles

A handle is a stable user-owned name and rolling tally inside one group.

Every handle MUST have an immutable `handle_id` and MUST belong to exactly one `group_id`.

A handle MAY have a mutable display name and aliases.

The handle name MUST NOT be handle identity.

Renaming a handle MUST NOT change its `handle_id`, tally, bindings, duplicate buckets, or history.

Handles MUST be normalized before validation, indexing, lookup, and comparison:

1. Unicode NFC;
2. case-sensitive comparison;
3. leading and trailing whitespace are invalid;
4. aliases do not create independent duplicate buckets.

Two independently created handles MUST NOT be automatically collapsed merely because their normalized display names match.

If the same normalized handle name resolves to multiple active handle IDs in one group, name-based lookup MUST report ambiguity until an explicit handle merge or rename resolves it.

### 5.1 Explicit handle merge

Handle merge MUST be an explicit authority operation.

A handle merge MUST:

1. identify source and destination handle IDs in the same group;
2. preserve the source handle and its complete tally history;
3. add each distinct source citation to the destination handle tally if it is not already represented there;
4. preserve binding provenance;
5. preserve every distinct citation;
6. reapply the group's duplicate policy;
7. retire or alias the source only through explicit events.

A handle merge MUST NOT compress multiple citation IDs into one tally entry.

## 6. Rolling tallies

Rolling tally is a first-class semantic of both groups and handles.

### 6.1 Group rolling tally

Each group MUST expose a complete ordered tally of every distinct citation ever added to that group.

Each citation MUST occupy at most one canonical tally position in a given group.

Removing, archiving, superseding, retracting, restoring, renaming, relocating, or rebinding a citation MUST NOT remove its group tally entry.

Re-adding a citation that previously belonged to the group MUST restore or update its existing membership state and MUST NOT create another canonical tally position for the same `citation_id`.

### 6.2 Handle rolling tally

Each handle MUST expose a complete ordered tally of every distinct citation ever bound to that handle.

Each citation MUST occupy at most one canonical tally position in a given handle.

Removing, superseding, globally retracting, restoring, or rebinding a citation MUST NOT remove its handle tally entry.

Binding a different intentional citation to the same handle MUST create a new tally entry, even when its target matches an earlier citation.

### 6.3 Tally ordering and projection

Group and handle tally order MUST use canonical citation-ID order and MUST NOT use timestamps.

A tally MUST remain a complete ordered sequence. It MUST NOT be replaced by an aggregate count or compressed duplicate record.

Every tally entry MUST expose at least:

- `citation_id`;
- `target_fingerprint`;
- canonical tally position;
- global citation state;
- group membership state;
- handle binding state when applicable;
- scoped `superseded_by` relationships;
- provenance for imported or merged membership.

Derived totals such as total, active, superseded, archived, removed, and globally retracted counts MAY be provided, but they MUST supplement the complete tally and MUST NOT replace it.

## 7. Target fingerprint

Every citation MUST have a deterministic `target_fingerprint` derived from:

1. artifact identity;
2. locator;
3. accepted evidence content hash;
4. canonicalization identifier.

The target fingerprint MUST be used to form duplicate buckets.

It MUST NOT be used as a citation ID or uniqueness constraint.

Equal fingerprints MUST NOT suppress intentional citation creation or remove tally entries.

## 8. Group duplicate policy

Every group MUST declare one duplicate policy:

- `handle` — duplicate buckets are scoped by `handle_id` and `target_fingerprint`;
- `group` — duplicate buckets are scoped by `group_id` and `target_fingerprint`;
- `none` — no automatic supersession is applied; the rolling tallies remain informational.

The default policy MUST be `handle` unless a repository explicitly configures another policy.

### 8.1 Handle-scoped policy

Under `handle`, citations belong to the same duplicate bucket only when both values match:

1. `handle_id`;
2. `target_fingerprint`.

Citations under different handle IDs MUST remain independently active even when their handle names or target fingerprints match.

### 8.2 Group-scoped policy

Under `group`, citations belong to the same duplicate bucket when both values match:

1. `group_id`;
2. `target_fingerprint`.

Different handle bindings inside the group MUST NOT prevent group-level duplicate matching.

### 8.3 No-supersession policy

Under `none`, matching handles or fingerprints MUST NOT produce automatic supersession.

Every citation and tally entry MUST remain independently projected according to its explicit global, membership, and binding events.

Changing a group's duplicate policy MUST be an explicit atomic operation and MUST re-evaluate all affected duplicate buckets.

## 9. Scoped supersession

Duplicate supersession MUST be scoped. It MUST NOT globally retract a citation.

Under the `handle` policy, supersession changes the state of a handle binding.

Under the `group` policy, supersession changes the state of a group membership.

Within each duplicate bucket, the citation with the greatest canonical citation ID MUST be the dominant representative.

Every other active binding or membership in that bucket MUST receive an explicit scoped supersession event identifying the dominant citation in `superseded_by`.

A scoped supersession event MUST:

- identify its `group_id`;
- identify `handle_id` when handle-scoped;
- identify the superseded `citation_id`;
- identify the dominant `citation_id`;
- identify the `target_fingerprint`;
- use `reason: "superseded"`;
- belong to the same atomic operation that applied the duplicate rule.

The dominant citation MUST NOT be rewritten or mutated solely because it is dominant in a bucket.

Notes, labels, tags, aliases, evidence, and tally entries MUST NOT be merged into the dominant citation.

A citation MAY simultaneously be:

- dominant in one handle;
- superseded in another handle;
- dominant in one group;
- superseded in another group;
- globally active or globally retracted.

Scoped supersession MUST preserve all of those independent states.

## 10. Global citation state

Global citation retraction is separate from group membership and handle binding state.

A global `citation.retracted` event MUST make the citation globally unavailable while preserving every group and handle tally entry.

A global retraction MUST NOT delete memberships, bindings, notes, metadata, or scoped supersession history.

A global `citation.restored` event MUST restore global availability but MUST NOT implicitly restore a removed membership, removed binding, or superseded scoped state.

Retracting a dominant citation MUST NOT implicitly activate citations it previously superseded.

Moving, renaming, removing, or globally retracting a dominant citation MUST NOT implicitly restore older scoped entries.

Scoped restoration MUST occur only through explicit membership or binding restoration events followed by duplicate-policy reevaluation.

Historical `superseded_by` relationships MUST remain inspectable even if the dominant citation later changes state.

## 11. Idempotent and atomic operations

Every mutating command MUST accept an `idempotency_key` and MUST have a stable `operation_id`.

An idempotency key identifies one logical operation within one repository.

The command name and canonical semantic payload MUST participate in idempotency comparison.

Generated timestamps, event IDs, event hashes, projections, publication results, hook results, and transport metadata MUST NOT participate in semantic payload equality.

The same idempotency key with the same semantic payload MUST return the original operation result and MUST NOT append another authority operation, citation, membership, binding, or tally entry.

The same idempotency key with a different command or semantic payload MUST fail with `E_IDEMPOTENCY_CONFLICT`.

Concurrent identical requests MUST produce exactly one authority operation.

All authority events belonging to one mutation MUST form one atomic operation.

A command MUST NOT report authority success unless every required citation, group, handle, membership, binding, and scoped supersession event has been durably committed.

Replay and reconciliation MUST NOT treat a partially written operation as complete.

A retry of an interrupted operation MUST recover or complete the original operation and MUST NOT allocate replacement citation, group, handle, or operation IDs.

For batch mutation:

- the batch MUST have a batch idempotency key;
- every item MUST have a distinct item idempotency key;
- every intentional item MUST have a distinct `client_item_id`;
- every accepted citation item MUST receive a distinct citation ID.

In `all_or_nothing` mode, all authority events MUST commit or none may be reported as completed.

In `partial` mode, every accepted item MUST be independently atomic and idempotent.

## 12. Reevaluation requirements

Duplicate buckets MUST be reevaluated after every successful operation that can affect bucket membership or dominance, including:

- citation creation;
- adding or restoring group membership;
- adding or restoring handle binding;
- moving a citation between handles;
- changing a group's duplicate policy;
- relocating a citation;
- accepting changed evidence;
- group merge;
- handle merge;
- reconciliation;
- migration that derives or changes target fingerprints.

Required scoped supersession events MUST be part of the same atomic operation.

A mutation that moves a citation out of a bucket MUST NOT implicitly restore earlier superseded entries. Restoration requires an explicit event.

## 13. Replay and projections

Replay MUST process only completed authority operations.

Replay MUST preserve every citation, group, handle, membership, binding, and tally entry.

Replay MUST apply explicit global state events and explicit scoped membership and binding events.

Replay MUST NOT infer unrecorded supersession solely from matching names, IDs, or fingerprints.

For every group, projections MUST include:

- immutable `group_id`;
- current name and path;
- duplicate policy;
- complete group rolling tally;
- complete group membership history;
- target-fingerprint buckets;
- dominant and superseded memberships;
- total, active, superseded, archived, removed, and globally retracted counts.

For every handle, projections MUST include:

- immutable `handle_id`;
- owning `group_id`;
- current name and aliases;
- complete handle rolling tally;
- complete binding history;
- target-fingerprint buckets;
- dominant and superseded bindings;
- total, active, superseded, removed, and globally retracted counts.

Filters MAY hide entries for a particular view, but they MUST NOT alter or replace the underlying complete tallies.

## 14. Authority reconciliation

Git MUST NOT text-merge Cite2Site authority ledgers.

Semantic reconciliation MUST:

1. identify and validate the merge base;
2. validate repository identity and schema;
3. validate every authority history and completed operation;
4. confirm that shared authority history has not been rewritten;
5. preserve every valid independent citation, group, handle, membership, and binding operation;
6. skip only operations already applied through idempotency or stable import identity;
7. preserve branch-local causal order;
8. order genuinely concurrent operations by canonical `operation_id` order;
9. preserve citation, group, and handle IDs;
10. assign fresh destination event hashes and event IDs;
11. rebuild complete group and handle rolling tallies without compression;
12. preserve distinct same-name group and handle IDs;
13. apply explicit group and handle merges;
14. reapply every affected group's duplicate policy;
15. append required scoped supersession events;
16. validate the final authority state;
17. regenerate every derived projection.

Concurrent duplicate candidates MUST use canonical citation-ID order to select their scoped dominant representative.

Reconciliation MUST produce the same authority and projection regardless of Git merge direction, branch name, client type, timestamps, or checkout order.

An imported operation with an idempotency key MUST preserve it.

An imported operation without an idempotency key MUST receive a stable identity:

```text
c2s-import:<source-repository-id>:<source-operation-id>
```

The same imported operation MUST NOT be appended more than once.

## 15. Structural conflicts

Reconciliation MUST stop before writes when any of the following exists:

- invalid JSONL;
- invalid event or previous-event hash;
- rewritten shared authority history;
- repository identity mismatch;
- unsupported schema or event type;
- incomplete atomic operation;
- identical idempotency keys with different semantic payloads;
- identical operation IDs with different operations;
- identical citation IDs with different creation records;
- identical group IDs with different group creation records;
- identical handle IDs with different handle creation records;
- group hierarchy cycle;
- invalid group or handle reference;
- invalid scoped supersession self-reference;
- missing supersession target;
- Git conflict markers in authority files.

A shared display name, shared path, shared target fingerprint, matching evidence, or duplicate tally entry MUST NOT be treated as a structural conflict.

Such semantic ambiguities MUST be preserved and surfaced for explicit rename or merge.

A structural conflict MUST return a structured error and MUST NOT produce a partial reconciliation result.

## 16. Single-writer, derived data, and publication

Mutation, batch mutation, migration, and reconciliation MUST be mutually exclusive authority-writing operations within one repository.

Authority validation MUST occur under exclusive write ownership.

The implementation MUST detect and safely recover or reject incomplete operations after interruption.

The following are derived and MUST NOT participate as authority:

- group and handle indexes;
- rolling-tally counts and summaries;
- duplicate-bucket summaries;
- artifact indexes;
- citation exports;
- grouped indexes;
- MkDocs pages and navigation;
- deployed site files.

Derived data MUST be regenerated after successful mutation, migration, or reconciliation.

Publication MUST follow the configured privacy policy. The default MUST remain `metadata_only`.

Publication or hook failure MUST NOT invalidate committed authority records.

Retrying an already committed operation MUST NOT append authority events, but MAY retry failed projection or publication work.

## 17. Schema and required errors

Adopting this RFC MUST use an authority schema capable of representing:

- citation IDs independent of target identity;
- group IDs and hierarchy;
- handle IDs owned by groups;
- complete group and handle rolling tallies;
- group memberships and handle bindings;
- group duplicate policy;
- target fingerprints;
- scoped supersession;
- global citation state;
- idempotency and atomic operation identity;
- stable import provenance.

Migration MUST preserve all existing citation IDs and intentional citation records.

Legacy handle strings MUST be migrated into stable handle IDs in a documented group, normally the default group.

Legacy handle tallies MUST remain complete and MUST NOT be compressed during migration.

A conforming implementation MUST provide at least:

- `E_IDEMPOTENCY_CONFLICT`;
- `E_CITATION_ID_CONFLICT`;
- `E_GROUP_ID_CONFLICT`;
- `E_HANDLE_ID_CONFLICT`;
- `E_GROUP_HIERARCHY_CYCLE`;
- `E_GROUP_NAME_AMBIGUOUS`;
- `E_HANDLE_NAME_AMBIGUOUS`;
- `E_OPERATION_ID_CONFLICT`;
- `E_OPERATION_INCOMPLETE`;
- `E_RECONCILE_HISTORY_DIVERGED`;
- `E_RECONCILE_REPOSITORY_MISMATCH`;
- `E_RECONCILE_UNSUPPORTED_EVENT`;
- `E_RECONCILE_CONFLICT`;
- `E_DUPLICATE_SELF_REFERENCE`;
- `E_SUPERSESSION_TARGET_MISSING`;
- a structured write-ownership error.

## 18. Required acceptance tests

The milestone MUST NOT close until automated tests prove:

1. Distinct intentional citations to identical evidence receive distinct citation IDs.
2. An idempotent retry creates no citation, membership, binding, or tally duplicate.
3. Every distinct citation added to a group receives one persistent group tally position.
4. Every distinct citation bound to a handle receives one persistent handle tally position.
5. Group and handle tallies are never replaced by aggregate counts.
6. Re-adding the same citation restores its existing group tally entry rather than creating another position.
7. Rebinding the same citation restores its existing handle tally entry rather than creating another position.
8. A citation can belong to multiple groups with independent membership state.
9. A citation can have different handle bindings in different groups.
10. Group and handle rename preserve IDs and tallies.
11. Same-name groups and handles are preserved as distinct IDs after reconciliation.
12. Explicit group merge preserves both source and destination tally histories.
13. Explicit handle merge preserves both source and destination tally histories.
14. Under `handle`, only matching handle ID plus fingerprint triggers scoped supersession.
15. Under `group`, matching group ID plus fingerprint triggers scoped supersession across handles.
16. Under `none`, matching targets remain independently active.
17. Canonical greatest citation ID is the scoped dominant representative.
18. Timestamps and clock changes do not affect dominance or tally order.
19. Scoped supersession does not globally retract a citation.
20. A citation can be dominant in one scope and superseded in another.
21. Global retraction preserves every group and handle tally entry.
22. Global restoration does not implicitly restore scoped membership or binding state.
23. Moving or retracting a dominant citation does not implicitly activate older superseded entries.
24. Duplicate-policy change atomically reevaluates affected buckets.
25. Relocation and accepted-evidence changes atomically reevaluate affected buckets.
26. Concurrent identical idempotency requests append exactly once.
27. Different payloads under one idempotency key fail.
28. An all-or-nothing batch exposes no partial completed operation.
29. Branch-local causal order is preserved.
30. Concurrent operations use deterministic operation-ID order.
31. Reconciliation is independent of merge direction.
32. Invalid, rewritten, or incomplete authority history fails before writes.
33. Group hierarchy cycles fail before writes.
34. Derived records are regenerated instead of authority-merged.
35. Publication retry does not duplicate authority operations.
36. Legacy migration preserves citation IDs and complete handle tallies.
37. Reconciliation never modifies cited artifacts.
38. Metadata-only publication exposes no accepted evidence text.
39. Successful reconciliation leaves every authority hash chain valid.

## 19. Final normative statement

Cite2Site MUST preserve every intentional citation.

Every distinct citation added to a group MUST remain in that group's complete rolling tally.

Every distinct citation bound to a handle MUST remain in that handle's complete rolling tally.

Tallies MUST NOT be compressed into counts, merged evidence records, or one representative citation.

Groups MUST provide explicit, user-friendly scopes for organization and duplicate policy.

Handles MUST provide stable named tallies inside groups.

Duplicate supersession MUST be scoped to a group membership or handle binding and MUST NOT globally erase or retract the citation.

Within each duplicate bucket, the citation with the greatest canonical citation ID MUST be the dominant representative.

Idempotency MUST suppress only retries of the same logical operation.

No timestamp or clock value may influence duplicate precedence, tally order, or reconciliation.
