# RFC: Cite2Site Duplicate Citation and Merge Reconciliation Policy

**Status:** Required
**Category:** Protocol
**Applies to:** Citation creation, browser and editor integrations, agentic batch commands, Git reconciliation, replay, indexing, and publication

## 1. Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

An implementation is conforming only when it satisfies every **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, and **SHALL NOT** requirement in this document.

## 2. Data model

Cite2Site MUST treat citation history as append-only filesystem records.

Each intentional citation operation MUST create a distinct citation record with a distinct immutable `citation_id`.

Cite2Site MUST preserve independently created citations even when they reference identical artifacts, locators, or evidence.

Cite2Site MUST NOT globally collapse citations by evidence identity.

Cite2Site MUST NOT rewrite or delete an existing citation creation record.

## 3. Citation identity

`citation_id` MUST identify one citation record.

`citation_id` MUST NOT identify cited evidence globally.

`citation_id` MUST NOT replace the citation handle.

Two intentional citation operations MUST receive different citation IDs, including when both operations cite identical evidence.

A retried execution of the same logical citation operation MUST retain the citation ID created by the original successful execution and MUST NOT append a second citation record.

## 4. Handle semantics

A handle MUST be treated as a user-owned citation name.

A handle MUST NOT be treated as citation identity.

Multiple citation records MAY share the same handle.

A handle index MUST map each handle to an ordered collection of citation IDs.

A handle collision MUST NOT invalidate an otherwise valid citation record.

A shared handle MUST produce a running citation tally.

## 5. Target fingerprint

Each citation MUST have a deterministic `target_fingerprint`.

The target fingerprint MUST be derived from:

1. artifact identity;
2. locator;
3. accepted evidence content hash;
4. canonicalization identifier.

The target fingerprint MUST be used for duplicate matching.

The target fingerprint MUST NOT be used as a citation ID.

The target fingerprint MUST NOT be used as a uniqueness constraint.

## 6. Idempotency

Every mutating command MUST support an `idempotency_key`.

An idempotency key MUST identify one logical operation.

When an operation is retried with the same idempotency key and the same semantic payload, Cite2Site MUST return the result of the original operation and MUST NOT append another record.

When an idempotency key is reused with a different semantic payload, Cite2Site MUST reject the operation with `E_IDEMPOTENCY_CONFLICT`.

Evidence similarity MUST NOT be used to identify a command retry.

## 7. Duplicate matching rule

Two citation records MUST be treated as duplicates for supersession when both of the following values are equal:

1. preferred handle;
2. target fingerprint.

No other duplicate rule is conforming.

Matching evidence without a matching handle MUST NOT trigger supersession.

A matching handle without a matching target fingerprint MUST NOT trigger supersession.

Matching notes, labels, tags, artifacts, locators, or evidence hashes MUST NOT independently trigger supersession.

## 8. Citation supersession

When a newly created citation matches one or more active citations under Section 7:

1. the new citation MUST remain active;
2. the new citation MUST remain unchanged;
3. every older active matching citation MUST be retracted;
4. each retraction MUST identify the new citation as `superseded_by`;
5. no matching creation record MAY be removed or rewritten.

The retraction event MUST have the following semantic form:

```json
{
  "event_type": "citation.retracted",
  "citation_id": "<superseded-citation-id>",
  "reason": "superseded",
  "superseded_by": "<overriding-citation-id>",
  "idempotency_key": "<operation-idempotency-key>"
}
```

The retraction event MUST be appended to citation history.

The overriding citation MUST NOT receive a mutation solely because it superseded another citation.

Cite2Site MUST NOT merge notes, labels, tags, aliases, or other metadata from the superseded citation into the overriding citation.

## 9. Supersession ordering

When multiple active citations share the same handle and target fingerprint, Cite2Site MUST select one overriding citation using the following total order:

1. ascending citation creation `created_at`;
2. ascending `citation_id` as the tie-breaker.

The citation with the greatest ordering value MUST remain active.

Every other active citation in the matching set MUST be retracted and MUST identify the overriding citation in `superseded_by`.

This ordering MUST be deterministic.

This ordering MUST produce the same result regardless of Git merge direction.

No actor, branch name, local append order, Git checkout order, or client type MAY alter the ordering result.

## 10. Restoration

A retracted citation MUST remain restorable.

Restoration MUST append a `citation.restored` event.

Restoration MUST NOT remove or rewrite the earlier retraction event.

Restoration MUST NOT mutate the citation identified by `superseded_by`.

After restoration, more than one citation MAY temporarily be active under the same handle and target fingerprint.

The next successful citation creation or reconciliation affecting that duplicate set MUST reapply the supersession rule in Sections 7 through 9.

## 11. Single-citation mutation

A citation command that includes a handle MUST execute the following logical operation:

1. validate the input;
2. validate or reserve the idempotency key;
3. create the citation record;
4. bind the handle;
5. identify older active citations with the same handle and target fingerprint;
6. append the required supersession retractions;
7. validate the resulting authority histories;
8. regenerate derived projections;
9. invoke configured synchronization and publication hooks.

The complete operation MUST be exposed as one core command.

A browser, editor, chat, file-manager, or right-click integration MUST NOT be required to:

* query duplicate candidates;
* request duplicate confirmation;
* invoke a separate retraction command;
* edit an authority file;
* interpret Git conflicts.

The core MUST perform duplicate supersession.

## 12. Agentic batch mutation

Each intentional batch item MUST have:

* a distinct `client_item_id`;
* a distinct item idempotency key;
* a distinct citation ID;
* its own citation metadata.

A batch item MAY cite the same evidence as another batch item.

A batch item with a distinct idempotency key MUST NOT be suppressed because its target fingerprint matches another item.

For every accepted batch item, Cite2Site MUST:

1. create the citation;
2. bind its handle;
3. apply the duplicate matching rule;
4. append required supersession retractions.

A retried batch item MUST NOT create a second citation or duplicate retraction.

In `all_or_nothing` mode, all citation creations, handle bindings, and supersession retractions in the batch MUST succeed or the command MUST report failure without claiming batch completion.

In `partial` mode, the duplicate and supersession rules MUST be applied independently to every accepted item.

## 13. Authority-ledger reconciliation

Git MUST NOT text-merge Cite2Site authority ledgers.

The following files MUST be reconciled through Cite2Site semantic reconciliation:

* `.c2s/citation-history.jsonl`;
* `.c2s/handle-bindings.jsonl`.

Reconciliation MUST:

1. identify the Git merge base;
2. validate the base authority histories;
3. validate both branch authority histories;
4. confirm that the base history is an exact prefix of each branch history;
5. identify operations appended after the merge base;
6. skip previously applied operations by idempotency key or stable import identity;
7. append every other valid operation to the destination history;
8. assign fresh `previous_event_hash` and `event_id` values;
9. compute the resulting citation projection;
10. apply the supersession rule;
11. append required retraction events;
12. validate the final authority histories;
13. regenerate every derived projection.

Reconciliation MUST preserve every independently created citation.

Reconciliation MUST NOT discard a citation because it matches another citation’s target fingerprint.

Reconciliation MUST NOT discard a citation because it shares a handle with another citation.

## 14. Imported operation identity

An imported event that contains an `idempotency_key` MUST preserve that key.

An imported event that lacks an `idempotency_key` MUST receive the following stable import key:

```text
c2s-import:<source-repository-id>:<source-event-id>
```

A later reconciliation MUST preserve the assigned import key.

The same imported operation MUST NOT be appended more than once.

An imported event MUST receive a fresh destination-chain `event_id`.

The source `event_id` MUST NOT be used as the destination-chain `event_id`.

## 15. Derived records

The following records MUST be treated as derived projections:

* artifact index;
* citation status export;
* citation JSONL export;
* handle index;
* target fingerprint index;
* duplicate tally;
* grouped indexes;
* MkDocs pages;
* MkDocs navigation;
* deployed static-site files.

Derived records MUST NOT participate as authority in reconciliation.

Derived records MUST be regenerated after every successful reconciliation.

A conflict in a derived file MUST NOT block reconciliation when the authority histories are valid.

## 16. Replay

Replay MUST read authority records in their recorded order.

Replay MUST apply explicit citation retractions.

Replay MUST apply explicit citation restorations.

Replay MUST preserve all citation creation records.

Replay MUST preserve all citation notes and metadata.

Replay MUST report whether each citation is active or retracted.

Replay MUST expose `superseded_by` for a superseded citation.

Replay MUST NOT infer supersession solely from matching handles or fingerprints.

A citation MUST be considered superseded only when an applicable retraction event exists.

Duplicate matching and required retractions MUST occur during citation mutation or reconciliation, not as an unrecorded replay-only state.

## 17. Handle and duplicate projection

For every handle, the projection MUST report:

* total citation count;
* active citation count;
* retracted citation count;
* active citation IDs;
* complete citation history;
* target-fingerprint duplicate sets;
* `superseded_by` relationships.

The projection MUST preserve deterministic ordering.

Active citations MUST appear before retracted citations.

Within each state, citations MUST be ordered by creation `created_at` and then citation ID.

## 18. Structural conflicts

Reconciliation MUST stop before appending new records when any of the following conditions exists:

* invalid JSONL;
* invalid event hash;
* invalid previous-event hash;
* rewritten shared history;
* merge-base history is not an exact prefix;
* unsupported event schema;
* unsupported event type;
* repository identity mismatch;
* identical idempotency keys with different semantic payloads;
* identical citation IDs with different creation records.

A shared handle MUST NOT be treated as a structural conflict.

A shared target fingerprint MUST NOT be treated as a structural conflict.

Matching evidence MUST NOT be treated as a structural conflict.

A structural conflict MUST produce a structured error and MUST NOT produce a partial reconciliation result.

## 19. Same-citation mutation ordering

When both branches append operations to the same citation ID, reconciliation MUST preserve all valid operations.

When the final projection depends on the relative order of those operations, Cite2Site MUST order the imported operations using:

1. event `created_at`;
2. source `event_id` as the tie-breaker.

The resulting order MUST be deterministic and MUST be independent of merge direction.

Reconciliation MUST NOT delete one branch’s operation to resolve ordering.

A later user operation MAY append a retraction, restoration, relocation, acceptance, or note that changes the projected result.

## 20. Publication

After successful mutation or reconciliation, Cite2Site MUST regenerate the configured static citation site.

Publication MUST use the repository’s configured privacy policy.

The default publication mode MUST remain `metadata_only`.

Automatic publication MUST NOT expose accepted evidence text under `metadata_only`.

The same hooks used to persist and synchronize citation mutations MAY trigger indexing, MkDocs generation, hot reload, and deployment.

Publication failure MUST NOT invalidate successfully appended authority records.

## 21. Required error codes

A conforming implementation MUST provide:

* `E_IDEMPOTENCY_CONFLICT`;
* `E_CITATION_ID_CONFLICT`;
* `E_RECONCILE_HISTORY_DIVERGED`;
* `E_RECONCILE_REPOSITORY_MISMATCH`;
* `E_RECONCILE_UNSUPPORTED_EVENT`;
* `E_RECONCILE_CONFLICT`;
* `E_DUPLICATE_SELF_REFERENCE`;
* `E_SUPERSESSION_TARGET_MISSING`.

All errors MUST use the standard structured C2S error response.

## 22. Acceptance requirements

The milestone MUST NOT close until automated tests prove all of the following:

1. Two intentional citations to identical evidence receive distinct citation IDs.
2. Citations with different handles remain active.
3. Citations with the same handle and target fingerprint trigger supersession.
4. The deterministic newest citation remains active.
5. Every older active matching citation is retracted.
6. Every superseded citation identifies the overriding citation.
7. The overriding citation remains unchanged.
8. Superseded citations retain their notes and metadata.
9. A superseded citation remains queryable.
10. Restoration reactivates a superseded citation.
11. A later matching citation re-applies supersession.
12. Same-command retries append once.
13. Different payloads under one idempotency key fail.
14. Agentic batch retries do not duplicate citations.
15. Agentic batch retries do not duplicate retractions.
16. Independent citations created on separate branches are preserved.
17. Reconciliation produces the same active citation regardless of merge direction.
18. Shared handles do not create structural conflicts.
19. Shared target fingerprints do not create structural conflicts.
20. Invalid authority chains fail before writes.
21. Rewritten shared history fails before writes.
22. Same citation ID with different creation records fails.
23. Derived records are regenerated rather than authority-merged.
24. Reconciliation never modifies cited artifacts.
25. Metadata-only publication contains no accepted evidence text.
26. Successful reconciliation leaves every authority hash chain valid.

## 23. Final normative statement

Cite2Site MUST preserve every intentional citation record.

Cite2Site MUST suppress only repeated executions of the same logical operation.

Citations with the same handle and target fingerprint MUST form a supersession sequence.

The deterministically newest citation MUST remain active.

Older active citations in the sequence MUST be retracted and MUST identify the active citation through `superseded_by`.

Retraction MUST preserve history and MUST remain reversible through restoration.
