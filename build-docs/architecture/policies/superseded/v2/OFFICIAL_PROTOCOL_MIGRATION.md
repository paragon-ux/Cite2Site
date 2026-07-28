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

This is **not compatible with the frozen v0.3 protocol as currently documented**. The existing stable contract freezes citation IDs as deterministic hashes of artifact, locator, and evidence; handles as strings bound directly to citations; seven event types; six schema identifiers; 15 commands; and 38 error codes. The new RFC introduces record-instance citation IDs, `group_id`, `handle_id`, `operation_id`, group memberships, scoped bindings and supersession, explicit merges, new commands, and new errors. It therefore requires a protocol-version revision and migration path, regardless of what release number you choose.

# Confirmed stale documents

These files contain direct contradictions with the RFC, not merely missing elaboration.

| Document                                                  | What is stale                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`README.md`**                                           | Says handles are aliases over citation IDs and points readers to a frozen v1 contract. It does not introduce groups, stable handle IDs, rolling tallies, scoped supersession, or reconciliation.                                                                                                                                                         |
| **`AGENTS.md`**                                           | Declares only citation and handle-binding JSONL files authoritative and defines handles as editable aliases. Its reading order also lacks the new RFC.                                                                                                                                                                                                   |
| **`build-docs/README.md`**                                | The architecture map has no reconciliation RFC, group/handle authority package, or associated ADRs. Its change-control chain must include the new protocol source.                                                                                                                                                                                       |
| **`build-docs/architecture/V1_STABLE_CONTRACT.md`**       | The most substantially stale document. It freezes the old schema IDs, event envelope, string handle binding, workflow events, commands, error catalog, citation-ID canonicalization, and global status transitions. This should remain as the historical v1 contract and be superseded, not silently rewritten as if the earlier contract never existed. |
| **`CITE2SITE_PROTOCOL_SPEC_V0_3.md`**                     | Defines citation creation without group or operation identity, checks handle collisions, writes only `citation.created` and optional `handle.bound`, and exposes no group, handle-ID, merge, reconciliation, or scoped-supersession commands.                                                                                                            |
| **`CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md`**               | Defines only citation and handle ledgers, says handles are aliases, makes collisions fail, uses global `citation.retracted`, lacks completed operation records, and indexes by string handle rather than group/handle authority objects and complete tallies.                                                                                            |
| **`SCHEMA_INDEX.md` and every referenced schema/example** | The inventory contains no group, stable handle, membership, scoped binding, scoped supersession, operation, reconciliation, tally, merge, or import-provenance schemas.                                                                                                                                                                                  |
| **`BRD.md`**                                              | Treats handles as properties attached to citations and “grouping” as indexes by artifact, handle, tag, status, and batch. It lacks groups as user authority objects, duplicate policy, rolling tallies, atomic operations, and semantic reconciliation.                                                                                                  |
| **`DRD.md`**                                              | Defines a handle as an editable alias, assumes collision/ambiguity behavior around one preferred handle, and describes site navigation without group hierarchy or complete group/handle tallies.                                                                                                                                                         |
| **`TRD.md`**                                              | Defines only citation and handle event ledgers, reduces handle bindings into preferred handles and aliases, and requires only the old flat index families. It lacks atomic operation completion, group and handle IDs, scoped state, merge validation, and tally requirements.                                                                           |
| **`CURRENT_STATUS_MATRIX.md`**                            | Claims the v1 implementation and stabilization contract are complete. The new RFC creates a new planned/active milestone and invalidates “Done” claims around citation identity, handle semantics, authority paths, replay, grouping, compatibility, and stable contracts until implementation and tests land.                                           |
| **`PROJECT_PLAN.md`**                                     | Defines success as handles being editable aliases, uses the old grouping dimensions, records v1 stabilization as done, and contains no milestone for groups, tallies, operation atomicity, or reconciliation.                                                                                                                                            |
| **`BUILD_WORKFLOW_CURRENT.md`**                           | The create workflow appends only a citation and string handle binding; the handle workflow checks collisions; the grouping workflow means generated indexes rather than stable folder-like groups; and no semantic reconciliation workflow exists.                                                                                                       |
| **`USER_GUIDE.md`**                                       | Teaches one string handle per citation, rename/alias/retire through `set-handle`, global retract/restore, `E_HANDLE_COLLISION`, and only the old two authority histories. It requires a substantial workflow rewrite, not an added “duplicates” section.                                                                                                 |
| **`AGENT_GUIDE.md`**                                      | Says handles are editable aliases, documents no operation or item idempotency keys, tells agents to resolve handle collisions, and explicitly guarantees that identical evidence, artifact, and locator produce the same citation ID—the direct opposite of the RFC.                                                                                     |
| **`INTEGRATION_CONTRACT.md`**                             | Uses raw handle strings and `citation_id` only, exposes handle collision as an error, lacks group selection/default Inbox behavior, operation idempotency, scoped duplicate actions, and group/handle ambiguity handling.                                                                                                                                |
| **ADR `0004-handles-as-editable-refs.md`**                | Must be superseded or substantially amended. It defines handles as aliases directly over citation IDs, while the RFC defines a handle as an independently identified, group-owned authority object with a complete tally.                                                                                                                                |
| **`COMPATIBILITY_CORPUS.md`**                             | Freezes old fixtures in which string handle collisions are errors and global citation retraction is the only state model. It needs legacy fixtures retained plus new migration and protocol fixtures.                                                                                                                                                    |
| **`PRODUCT_OVERVIEW.md`**                                 | Describes the current 15-command lifecycle and old handle management but contains no groups, tallies, duplicate policies, operation atomicity, or reconciliation.                                                                                                                                                                                        |

# Schema and example files requiring revision

The existing schema inventory should not be patched in place without a protocol version bump. At minimum:

### Existing schemas to revise or version

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

Every paired example also needs revision. These are the complete currently indexed schema and example families.

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
* migration from legacy handles into stable handle IDs and the default group.

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
* migration policy and migration fixture documentation;
* release checklist and changelog;
* support policy;
* threat/privacy checklist where group-level publication metadata is introduced.

The build-doc map itself requires changes to requirements, workflows, architecture contracts, schemas, project planning, status, and ADRs to move together.

# New documents or decisions required

I recommend adding these rather than forcing all rationale into the protocol specification:

1. **The RFC itself** under `build-docs/architecture/`, with a stable filename and protocol-version designation.
2. **ADR: Groups, stable handles, and rolling tallies.**
3. **ADR: Atomic operations and completed-operation replay.**
4. **ADR: Git semantic reconciliation and deterministic concurrent ordering.**
5. **Migration specification** from protocol v0.3/v1 authority into the new group/handle/operation model.
6. **Reconciliation workflow document** covering automatic hooks, structured conflicts, interruption recovery, and projection/publication retry.
7. **Compatibility corpus revision** that retains v1 legacy fixtures while adding migrated expected results.

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
2. Version the protocol, implementation spec, stable contract, and schemas.
3. Update BRD, DRD, and TRD.
4. Define the migration and compatibility corpus.
5. Update the project plan, workflow, status matrix, AGENTS, and build-doc map.
6. Update user, agent, and integration guides.
7. Update README and external narratives last, once the implementation maturity is accurately labelled.

The critical point is that **the old v1/v0.3 documents should remain historically true**. The new authority package should supersede them through an explicit protocol version and migration path rather than retrospectively changing what v1 promised.
