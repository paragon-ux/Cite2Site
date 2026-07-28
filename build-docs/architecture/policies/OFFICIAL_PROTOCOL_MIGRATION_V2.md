# Official Protocol Migration v2: Mandatory Archival Replacement

**Status:** Required
**Transition model:** Clean replacement with mandatory archival; no runtime conversion

## Approval

**Yes, I approve the refined policy.**

It simplifies the user experience without weakening the authority model:

* users organize citations through stable groups and handles;
* every intentional citation remains in the rolling tally;
* duplicate handling is deterministic and scoped;
* supersession does not globally retract the citation;
* retries are suppressed through operation idempotency rather than evidence identity;
* reconciliation preserves independent branch operations and produces a merge-direction-independent result;
* timestamps are removed from precedence decisions.

That is a coherent protocol and a better fit for Cite2Site than the earlier global-retraction model.

This is **not compatible with the frozen v0.3 protocol as currently documented**. The existing stable contract freezes citation IDs as deterministic hashes of artifact, locator, and evidence; handles as strings bound directly to citations; seven event types; six schema identifiers; 15 commands; and 38 error codes. The new RFC introduces record-instance citation IDs, `group_id`, `handle_id`, `operation_id`, group memberships, scoped bindings and supersession, explicit merges, new commands, and new errors. It therefore requires a clean replacement of the active protocol authority and mandatory archival of the frozen v0.3/v1 materials. It does not require, authorize, or imply a runtime migration path, dual-protocol implementation, or compatibility bridge.

# Mandatory archival boundary

The previous v0.3/v1 protocol package MUST be preserved as historical material and removed from the active authority chain.

Archival means:

* preserve the original documents, implementation record, tests, and Git history without rewriting them to describe the replacement model;
* label archived material **Historical**, **Superseded**, and **Unsupported by the active runtime**;
* exclude archived material from active agent reading order, active runtime paths, active schemas, active tests, current conformance claims, and release guidance;
* reject archived-format repositories before replay, mutation, reconciliation, projection, or publication;
* do not convert legacy citation IDs, handle strings, ledgers, fixtures, or repository state into the replacement model;
* do not maintain a dual-protocol reducer, version switch, compatibility shim, or transparent fallback;
* preserve removed old-model implementation through Git history or an explicitly labelled archive snapshot rather than keeping it reachable from the active runtime;
* limit semantic reconciliation to repositories that already conform to the replacement authority model.

A future import utility would require separate authorization and its own contract. This policy does not authorize one.

# Confirmed stale documents

These files contain direct contradictions with the RFC, not merely missing elaboration.

| Document                                                  | What is stale                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`README.md`**                                           | Says handles are aliases over citation IDs and points readers to a frozen v1 contract. It does not introduce groups, stable handle IDs, rolling tallies, scoped supersession, or reconciliation.                                                                                                                                                         |
| **`AGENTS.md`**                                           | Declares only citation and handle-binding JSONL files authoritative and defines handles as editable aliases. Its reading order also lacks the new RFC.                                                                                                                                                                                                   |
| **`build-docs/README.md`**                                | The architecture map has no reconciliation RFC, group/handle authority package, or associated ADRs. Its change-control chain must include the new protocol source.                                                                                                                                                                                       |
| **`build-docs/architecture/V1_STABLE_CONTRACT.md`**       | The most substantially stale document. It freezes the old schema IDs, event envelope, string handle binding, workflow events, commands, error catalog, citation-ID canonicalization, and global status transitions. This MUST remain as the historical v1 contract, be moved outside the active authority chain, and be labelled Historical, Superseded, and Unsupported by the active runtime. |
| **`CITE2SITE_PROTOCOL_SPEC_V0_3.md`**                     | Defines citation creation without group or operation identity, checks handle collisions, writes only `citation.created` and optional `handle.bound`, and exposes no group, handle-ID, merge, reconciliation, or scoped-supersession commands. Archive it unchanged and remove it from active protocol authority.                                           |
| **`CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md`**               | Defines only citation and handle ledgers, says handles are aliases, makes collisions fail, uses global `citation.retracted`, lacks completed operation records, and indexes by string handle rather than group/handle authority objects and complete tallies. Archive it unchanged and remove it from active implementation authority.                   |
| **`SCHEMA_INDEX.md` and every referenced schema/example** | The inventory contains no group, stable handle, membership, scoped binding, scoped supersession, operation, reconciliation, tally, merge, or import-provenance schemas. Archive the inventory and examples unchanged; create a separate active replacement schema index.                                                                                |
| **`BRD.md`**                                              | Treats handles as properties attached to citations and “grouping” as indexes by artifact, handle, tag, status, and batch. It lacks groups as user authority objects, duplicate policy, rolling tallies, atomic operations, and semantic reconciliation.                                                                                                  |
| **`DRD.md`**                                              | Defines a handle as an editable alias, assumes collision/ambiguity behavior around one preferred handle, and describes site navigation without group hierarchy or complete group/handle tallies.                                                                                                                                                         |
| **`TRD.md`**                                              | Defines only citation and handle event ledgers, reduces handle bindings into preferred handles and aliases, and requires only the old flat index families. It lacks atomic operation completion, group and handle IDs, scoped state, merge validation, and tally requirements.                                                                           |
| **`CURRENT_STATUS_MATRIX.md`**                            | Claims the v1 implementation and stabilization contract are complete. The new RFC creates a replacement milestone and invalidates active “Done” claims around citation identity, handle semantics, authority paths, replay, grouping, compatibility, and stable contracts until replacement implementation and tests land. Historical completion claims may remain only inside the archive.                                           |
| **`PROJECT_PLAN.md`**                                     | Defines success as handles being editable aliases, uses the old grouping dimensions, records v1 stabilization as done, and contains no milestone for groups, tallies, operation atomicity, or reconciliation.                                                                                                                                            |
| **`BUILD_WORKFLOW_CURRENT.md`**                           | The create workflow appends only a citation and string handle binding; the handle workflow checks collisions; the grouping workflow means generated indexes rather than stable folder-like groups; and no semantic reconciliation workflow exists.                                                                                                       |
| **`USER_GUIDE.md`**                                       | Teaches one string handle per citation, rename/alias/retire through `set-handle`, global retract/restore, `E_HANDLE_COLLISION`, and only the old two authority histories. It requires a substantial workflow rewrite, not an added “duplicates” section.                                                                                                 |
| **`AGENT_GUIDE.md`**                                      | Says handles are editable aliases, documents no operation or item idempotency keys, tells agents to resolve handle collisions, and explicitly guarantees that identical evidence, artifact, and locator produce the same citation ID—the direct opposite of the RFC.                                                                                     |
| **`INTEGRATION_CONTRACT.md`**                             | Uses raw handle strings and `citation_id` only, exposes handle collision as an error, lacks group selection/default Inbox behavior, operation idempotency, scoped duplicate actions, and group/handle ambiguity handling.                                                                                                                                |
| **ADR `0004-handles-as-editable-refs.md`**                | Must be marked Superseded and archived without rewriting its original decision. It defines handles as aliases directly over citation IDs, while the RFC defines a handle as an independently identified, group-owned authority object with a complete tally.                                                                                         |
| **`COMPATIBILITY_CORPUS.md`**                             | Freezes old fixtures in which string handle collisions are errors and global citation retraction is the only state model. Its fixtures MUST be archived with the old contract and excluded from the active conformance suite. The replacement protocol needs a new compatibility corpus and an archived-format rejection fixture.                                                                                                                                                    |
| **`PRODUCT_OVERVIEW.md`**                                 | Describes the current 15-command lifecycle and old handle management but contains no groups, tallies, duplicate policies, operation atomicity, or reconciliation.                                                                                                                                                                                        |

# Schema and example files requiring revision

The existing schema inventory MUST be archived without being patched to resemble the replacement model. A new active schema inventory MUST be created for the replacement authority. At minimum:

### Existing schemas to archive

* `project.schema.json`
* `event-envelope.schema.json`
* `citation-created-event.schema.json`
* `workflow-citation-event.schema.json`
* `handle-bound-event.schema.json`
* `cite-batch-request.schema.json`
* `citations-response.schema.json`
* `lookup-actions-response.schema.json`
* `status-report.schema.json`
* `export-indexes.schema.json`

Every paired example MUST be archived with these schemas. These are the complete currently indexed schema and example families; they MUST NOT remain in the active schema index.

### New schemas required

The RFC requires normative representations for:

* group creation, rename, move, merge, retire, and alias;
* handle creation, rename, merge, retire, and alias;
* group membership and membership restoration/removal;
* handle binding and binding restoration/removal;
* scoped supersession;
* atomic operation identity and completion;
* reconciliation request, plan, conflict, and result;
* stable import provenance;
* group and handle rolling-tally projections;
* duplicate-policy configuration;
* archived-protocol detection and structured rejection before replay or writes.

The RFC requires these authority concepts explicitly; they cannot be left as undocumented internal implementation details.

# Documents needing a mandatory secondary sweep

I have not line-audited each of these in this pass, but they are in the repository’s declared authority or product-document chain and depend on the old model:

* `build-docs/external/overviews/ENGINEERING_OVERVIEW.md`
* `build-docs/external/overviews/WHITEPAPER.md`
* `build-docs/external/narratives/END_TO_END_NARRATIVE.md`
* `build-docs/external/narratives/PUBLISHING_AND_ADOPTION_PLAN.md`
* the active Chrome-extension milestone prompt, including `PHASE_07_PT2_POST_v1_CHECKPOINTS.md`
* extension/native-host protocol documentation and fixtures;
* `examples/integration/thin_client.py` documentation and integration fixtures;
* archival policy and archived-protocol rejection fixtures;
* release checklist and changelog;
* support policy;
* threat/privacy checklist where group-level publication metadata is introduced.

The build-doc map itself requires changes to requirements, workflows, architecture contracts, schemas, project planning, status, and ADRs to move together.

# New documents or decisions required

I recommend adding these rather than forcing all rationale into the protocol specification:

1. **The RFC itself** under `build-docs/architecture/`, with a stable filename and clear replacement-authority designation.
2. **ADR: Groups, stable handles, and rolling tallies.**
3. **ADR: Atomic operations and completed-operation replay.**
4. **ADR: Git semantic reconciliation and deterministic concurrent ordering.**
5. **Archival boundary specification** defining historical preservation, exclusion from active authority, and fail-closed rejection of archived repositories.
6. **Reconciliation workflow document** covering automatic hooks, structured conflicts, interruption recovery, and projection/publication retry.
7. **Replacement compatibility corpus** with archived-format rejection fixtures; the v1 corpus remains only in the historical archive.

ADR 0003 on append-only replay should also be amended to state that replay processes only completed atomic operations. ADR 0004 should be marked **Superseded**, not simply edited in a way that erases the original decision history.

# Documents that remain conceptually valid

These decisions do not need fundamental reversal, although cross-references may change:

* source-clean citations;
* dedicated citation repository;
* append-only authority;
* contextual actions rather than authoritative overlays;
* MkDocs as a publication projection;
* metadata-only publication by default;
* artifact index as a derived cache;
* session-gate rigor.

The new RFC extends these principles rather than contradicting them.

## Recommended documentation-pass order

1. Commit the RFC and new ADRs.
2. Archive the old protocol, implementation spec, stable contract, schemas, examples, and compatibility corpus; install the replacement authority package.
3. Update BRD, DRD, and TRD.
4. Define the archival boundary, archived-format rejection behavior, and replacement compatibility corpus.
5. Update the project plan, workflow, status matrix, AGENTS, and build-doc map.
6. Update user, agent, and integration guides.
7. Update README and external narratives last, once the implementation maturity is accurately labelled.

The critical point is that **the old v1/v0.3 documents MUST remain historically true and MUST be archived**. The replacement authority package supersedes them through a clean active-authority boundary, not through runtime migration, dual compatibility, or retrospective rewriting of what v1 promised.
