# Immediate Stop: Clean Protocol Replacement and Archival Boundary

This directive changes the execution order and architecture boundary of the remainder of the task.

Stop the current Gate 9 / Phase 7 Part 2 work immediately.

Do not continue implementing against the v0.3/v1 authority model.

Do not begin an in-place migration, compatibility bridge, dual-protocol implementation, schema-version negotiation layer, or old-to-new authority conversion.

The revised policy is a **clean protocol replacement**. The earlier Cite2Site model is historical material to be archived, not an active protocol that the replacement implementation must migrate, emulate, reconcile with, or continue supporting.

## Preserve current work without continuing it

Before changing anything, record:

```powershell
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --cached --stat
```

The verified repository root must be the intended `first-build-slice` Cite2Site checkout.

Preserve all existing branches and commits.

Do not:

* reset destructively;
* clean untracked files;
* delete branches;
* rewrite published history;
* force-push;
* silently discard current Gate 9 work;
* commit incomplete work as though it were valid under the replacement protocol.

Record any interrupted work and affected files in:

`.git/codex-gate9-state.md`

Classify interrupted work as one of:

* reusable under the replacement protocol;
* documentation-only and still accurate;
* dependent on the archived model;
* unrelated;
* unsafe to integrate without redesign.

Do not attempt to adapt old-model-dependent work until the replacement authority package is complete.

## Governing policy documents

Read these two supplied policy documents in full:

1. `OFFICIAL_MERGE_AND_RECONCILIATION_POLICY_REFINED_V2(2).md`
2. `OFFICIAL_PROTOCOL_MIGRATION.md`

Use the refined grouping, tally, idempotency, atomic-operation, scoped-supersession, and reconciliation model as the basis of the replacement protocol.

The old model must not remain active merely because historical documents, tests, commands, schemas, or implementations exist.

## Clean-break interpretation

The repository will have one active authority model.

The replacement protocol must not:

* read legacy authority ledgers as valid current authority;
* convert legacy handle strings into new handle objects;
* preserve compatibility with evidence-derived citation IDs;
* retain old command behavior behind a version switch;
* execute both old and new replay reducers;
* maintain dual schema families as active alternatives;
* reconcile old-model and new-model branches semantically;
* provide transparent fallback to v0.3/v1 behavior;
* claim that old repositories can be upgraded automatically;
* retain obsolete behavior solely to satisfy old compatibility fixtures.

The replacement protocol begins from a newly initialized repository using the new authority model.

Existing repositories created under the archived model are outside the active protocol boundary.

When encountered, they must fail closed with a clear structured error explaining that the repository uses an archived, unsupported authority format. Do not partially read, mutate, convert, or reinterpret such a repository.

The exact error name must be defined with the replacement error catalog. A name such as `E_ARCHIVED_PROTOCOL_UNSUPPORTED` may be considered, but do not adopt it until the governing specification and schema define it.

## Correct the policy package first

The supplied RFC currently contains language that can be read as requiring executable legacy migration.

Before implementing the replacement protocol, reconcile that language with this clean-break decision.

Remove or replace active requirements that mandate:

* conversion from v0.3/v1 authority histories;
* migration of legacy handle strings into stable handle IDs;
* migrated legacy tally construction;
* preservation of legacy citation IDs inside the replacement repository;
* an executable legacy-migration acceptance fixture;
* dual-protocol compatibility behavior.

Where historical preservation is required, rewrite it as an **archival requirement**, not a runtime migration requirement.

The archival requirement should state that:

* the earlier protocol remains available as historical documentation;
* its original Git history remains preserved;
* its design and behavior must not be falsely rewritten;
* it is not active authority for the replacement implementation;
* it is not accepted as input by the replacement runtime;
* no automatic conversion is promised;
* no compatibility guarantee crosses the archival boundary.

Do not leave contradictory mandatory language in the active RFC.

## Archive rather than version alongside

Move the old authority package out of the active documentation and implementation chain according to the repository’s documentation standard.

The archive should include or point to the historical forms of:

* the v0.3 protocol specification;
* the v0.3 implementation specification;
* the old stable contract;
* old schemas and examples;
* old compatibility-corpus definitions;
* superseded ADRs;
* old user and agent workflow descriptions where historically useful.

Use a clear archive location determined after reading:

* `AGENTS.md`;
* `build-docs/README.md`;
* `build-docs/internal/DOCUMENTATION_STANDARD.md`.

The archive must be clearly labelled:

* Historical;
* Superseded;
* Unsupported by the active runtime;
* Not current implementation authority.

Do not keep archived documents in the active reading order.

Do not require ordinary implementation agents or reviewers to read the archive unless they are investigating historical behavior.

Git history remains the ultimate preservation mechanism. Do not duplicate large quantities of obsolete material unnecessarily when a compact archive index and stable historical commit references are sufficient.

## Replace the active authority chain

After establishing the archive boundary, build one coherent active authority package for the replacement protocol.

Update in this order:

1. refined RFC;
2. architectural decisions;
3. active protocol specification;
4. active implementation specification;
5. active schemas and examples;
6. BRD, DRD, and TRD;
7. project plan and build workflow;
8. current status matrix;
9. `AGENTS.md` and build-document map;
10. active phase and gate prompts;
11. user, agent, integration, extension, security, support, and release documentation;
12. README and external narratives last.

Do not create parallel “old active” and “new active” documentation trees.

At every active documentation entry point, there must be one clear answer to:

* which protocol is current;
* which authority files are current;
* which commands are current;
* which schemas are current;
* which implementation is current;
* which capabilities are implemented;
* which capabilities remain planned.

## Required replacement model

The active protocol must be based on:

* record-instance citation IDs;
* stable `group_id` objects;
* stable group-owned `handle_id` objects;
* group memberships;
* handle bindings;
* complete group rolling tallies;
* complete handle rolling tallies;
* deterministic target fingerprints;
* group-scoped duplicate policies;
* scoped supersession;
* separate global citation state;
* stable `operation_id`;
* required `idempotency_key`;
* atomic completed operations;
* completed-operation-only replay;
* explicit group and handle merges;
* deterministic semantic reconciliation between branches using the replacement protocol;
* canonical ID ordering without timestamp precedence;
* metadata-only publication by default.

Semantic reconciliation applies only when both inputs conform to the replacement protocol and share a valid replacement-protocol ancestry.

It must not attempt to reconcile archived-model authority with replacement-model authority.

## Code separation

Inspect the current implementation and classify each surface:

* reusable invariant;
* old-model-specific;
* replacement-ready;
* transitional;
* obsolete.

Reusable invariants may include:

* cited artifacts remain source-clean;
* authority remains append-only;
* projections remain derived;
* publication defaults to metadata-only;
* filesystem safety;
* structured errors;
* deterministic serialization where still applicable.

Old-model-specific behavior must not remain active, including:

* evidence-derived citation identity;
* raw string handles as identity;
* handle collision as duplicate control;
* global duplicate retraction;
* replay based on only the old citation and handle-binding ledgers;
* old lifecycle commands whose semantics contradict scoped state;
* old projection shapes presented as replacement-protocol output.

Do not preserve contradictory code behind an undocumented compatibility path.

If old code must remain temporarily while replacement implementation is incomplete, it must be:

* isolated;
* unreachable from the replacement entry point;
* labelled as archived or transitional;
* excluded from claims of replacement-protocol conformance;
* scheduled for deletion before the replacement protocol is accepted.

Prefer removal from the active branch when Git history already preserves it and no active requirement needs it.

## Test separation

The active test suite must test the replacement protocol.

Old tests may be:

* moved to a historical archive;
* retained only as documentation of previous behavior;
* removed from the active suite when Git history already preserves them.

Do not force the replacement implementation to pass tests whose assertions encode:

* deterministic evidence-derived citation IDs;
* direct string-handle identity;
* global duplicate retraction;
* timestamp precedence;
* old authority-file assumptions;
* transparent old-repository loading;
* automatic legacy migration.

Add an explicit test proving that an archived-format repository is rejected before replay or mutation.

Do not add a conversion test unless a future separately authorized import project defines one.

## No implied import promise

This clean break does not prohibit a future optional import utility.

However:

* no import utility is authorized by this task;
* no import behavior belongs in the active protocol;
* no compatibility commitment should be made;
* no archived repository should be modified in place;
* any future importer must be a separately scoped, explicitly lossy-or-lossless contract with its own security review.

Do not call such future work “migration” in current product documentation unless it has been designed and authorized.

## New prerequisite gate

Treat this work as a distinct prerequisite gate:

**Replacement Protocol and Archival Separation Gate**

Gate 9 could not resume until the replacement prerequisite gate established:

* a clean archive boundary;
* one active replacement RFC;
* one active protocol specification;
* one active implementation specification;
* one active schema family;
* replacement-oriented requirements and workflow;
* truthful status labels;
* replacement-aware gate definitions;
* rejection behavior for archived repositories;
* no active documentation contradiction about legacy compatibility.

## Implementation order

After the replacement authority package is internally consistent, implement the replacement model in dependency order:

1. new repository identity and initialization contract;
2. atomic operation envelope and completed-operation replay;
3. record-instance citation identity and target fingerprints;
4. groups and memberships;
5. stable handles and bindings;
6. complete group and handle rolling tallies;
7. duplicate policies and scoped supersession;
8. explicit group and handle merges;
9. replacement-protocol semantic reconciliation;
10. projections and privacy enforcement;
11. integration surfaces;
12. Gate 9 / Phase 7 Part 2 behavior.

Do not adapt an extension or integration milestone to an incomplete temporary model.

## Gate 9 resumption

Gate 9 may resume only when:

* its governing prompt references only the replacement protocol;
* its command and message shapes use replacement objects;
* its mutation paths require atomic operations and idempotency;
* its group and handle behavior uses stable IDs;
* its duplicate behavior is scoped;
* it does not assume old handle-collision semantics;
* it does not assume evidence-derived citation IDs;
* it does not read or mutate archived authority repositories;
* required replacement foundations are implemented and tested.

Rewrite the Gate 9 objective before resuming it.

Do not continue from the interrupted old-model objective.

**Current execution note:** the active repository now uses the replacement
`R0` through `R9` gate sequence. Once the status matrix marks R1-R8
replacement foundations present, R9 is actionable under
`REPLACEMENT_GATE_09_INTEGRATION.md`; it still cannot be marked Done until
package evidence and manual Chrome validation pass.

## Validation

During authority cleanup, run targeted documentation and schema checks.

After replacement implementation is complete, run the repository-required final validation once.

Validation must include:

* active documentation-link checks;
* active schema and example parsing;
* no stale active references to the old model;
* archived documents excluded from current authority reading order;
* archived repositories rejected before writes;
* source-clean regression tests;
* atomic-operation integrity tests;
* incomplete-operation rejection tests;
* idempotency tests;
* rolling-tally completeness tests;
* scoped-supersession tests;
* same-name group and handle ambiguity tests;
* deterministic replacement-protocol reconciliation tests;
* metadata-only no-leak tests;
* authority hash-chain validation.

Do not repeatedly rerun the full suite after documentation-only edits.

## Commit structure

Keep the replacement reviewable through cohesive commits:

1. archive boundary and active policy correction;
2. replacement architecture decisions and specifications;
3. replacement schemas and examples;
4. requirements, workflow, status, and gate resequencing;
5. replacement core implementation;
6. projections and integrations;
7. Gate 9 completion;
8. final documentation and security remediation.

Do not combine archived-model cleanup and unfinished Gate 9 work into a commit claiming feature completion.

## Required handoff

The handoff must report:

* verified `first-build-slice` repository root;
* interrupted work preserved;
* historical material archived;
* active old-model references removed;
* clean-break decision recorded;
* active RFC corrected;
* active authority files;
* active schema family;
* archived-repository refusal behavior;
* replacement implementation status;
* Gate 9 status: Blocked or Resumed;
* exact reason Gate 9 may or may not proceed;
* commits created;
* focused and full validation results;
* unresolved replacement-protocol risks.

Do not describe the work as an old-to-new migration.

Do not claim compatibility with archived repositories.
