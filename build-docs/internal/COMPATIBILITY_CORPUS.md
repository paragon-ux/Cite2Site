# Cite2Site v1.0 Compatibility Corpus

**Status:** v1.0 stabilization authority. Defines the fixture set and test matrix
that future releases must preserve as a regression gate.

---

## Purpose

The compatibility corpus is a frozen set of inputs and expected outputs that
prove the v1.0 stable contract behaves identically across releases. Any future
release that breaks a corpus fixture must either fix the regression or document
a MAJOR version bump with an explicit migration path.

---

## Fixture Categories

### 1. Event Fixtures

Located in `tests/compat_fixtures/events/`.

| Fixture | Description | Expected |
|---|---|---|
| `citation_created.jsonl` | Single citation.created event | Replay resolves correctly |
| `citation_created_batch.jsonl` | 3 citation.created with shared batch_id | All 3 resolve; batch index populated |
| `handle_bound_bind.jsonl` | citation.created + handle.bound (bind) | Preferred handle set |
| `handle_bound_rename.jsonl` | bind + rename | Old handle preserved as alias |
| `handle_bound_retire.jsonl` | bind + retire | Handle retired, no preferred handle |
| `citation_accepted.jsonl` | citation.created + citation.accepted | Status resolved, idempotent |
| `citation_retracted.jsonl` | citation.created + citation.retracted | Status retracted |
| `citation_restored.jsonl` | created + retracted + restored | Status resolved |
| `citation_relocated.jsonl` | created + relocated (new locator) | Locator updated |
| `citation_noted.jsonl` | created + noted | Note present in metadata |
| `full_workflow.jsonl` | Complete workflow: create, accept, retract, restore, note | All states valid |

### 2. Error Fixtures

Located in `tests/compat_fixtures/errors/`.

| Fixture | Error Code | Trigger |
|---|---|---|
| `missing_artifact.jsonl` | E_ARTIFACT_MISSING | Artifact deleted |
| `corrupt_project.json` | E_JSON_INVALID | project.json is not valid JSON |
| `corrupt_history.jsonl` | E_JSONL_INVALID | citation-history.jsonl has non-JSON line |
| `tampered_event.jsonl` | E_EVENT_HASH | event_id replayed by evidence changed |
| `chain_break.jsonl` | E_EVENT_CHAIN | previous_event_hash mismatch |
| `missing_event_id.jsonl` | E_EVENT_ID_MISSING | Event without event_id |
| `unknown_schema_project.json` | E_SCHEMA_UNKNOWN | project.json with foreign schema_version |
| `unsupported_schema_project.json` | E_SCHEMA_UNSUPPORTED | project.json with c2s prefix but wrong version |
| `handle_collision.jsonl` | E_HANDLE_COLLISION | Two citations with same handle |
| `empty_batch.json` | E_BATCH_EMPTY | Batch request with no items |

### 3. Privacy Mode Fixtures

Located in `tests/compat_fixtures/privacy/`.

| Fixture | Mode | Expected |
|---|---|---|
| `metadata_only.json` | metadata_only | No `accepted_evidence.text` in any citation |
| `hash_only.json` | hash_only | No `text` or `line_hashes` in any citation |
| `snippet_allowed.json` | snippet (allow_snippet=true) | `text` present |
| `snippet_denied.json` | snippet (allow_snippet=false) | E_PRIVACY_POLICY |
| `private_link_allowed.json` | private_link (allow_private_link=true) | Private links present |
| `private_link_denied.json` | private_link (allow_private_link=false) | E_PRIVACY_POLICY |

### 4. Export Determinism Fixtures

Located in `tests/compat_fixtures/exports/`.

| Fixture | Description |
|---|---|
| `baseline/` | Full citation repository with 5+ citations, handles, tags, batch |
| `baseline/expected_exports.json` | Canonical export output (SHA of all export files) |

### 5. Batch Request Fixtures

Located in `tests/compat_fixtures/batch/`.

| Fixture | Description |
|---|---|
| `all_or_nothing_ok.json` | 3 valid items → all succeed |
| `all_or_nothing_fail.json` | 1 invalid → nothing appended |
| `partial_ok.json` | 2 valid + 1 invalid → valid appended, invalid reported |
| `content_hash_mismatch.json` | Expected hash mismatch → E_CONTENT_HASH_MISMATCH |

### 6. Integration Contract Fixtures

Located in `examples/integration/fixtures/`.

| Fixture | Description |
|---|---|
| `lookup-overlap-picker.json` | Multiple overlapping citations, requires_picker=true |
| `lookup-uncited-response.json` | No matching citation, single cite action |
| `picker-cancelled.json` | Picker cancellation response shape |
| `selection-citation-request.json` | cite-selection request contract |
| `unavailable-actions.json` | Citation with limited available actions |

---

## Test Matrix

| Test Class | What It Covers | Fixture Set | Minimum Assertions |
|---|---|---|---|
| `CompatEventTests` | Every event type replays correctly | events/ | Status, preferred_handle, citation_id, event chain valid |
| `CompatErrorTests` | Every error code triggers correctly | errors/ | Error code matches, structured JSON output |
| `CompatPrivacyTests` | Every privacy mode enforces policy | privacy/ | No evidence leak in metadata_only/hash_only; refusal for unauthorized snippet/link |
| `CompatExportTests` | Export determinism | exports/ | SHA of all export files matches canonical output |
| `CompatBatchTests` | Batch all-or-nothing + partial | batch/ | Created/rejected counts correct; no partial append unless requested |
| `CompatMigrationTests` | Schema version validation | errors/ (unknown/unsupported) | Correct refusal codes; no authority rewrite |
| `CompatIntegrationTests` | Lookup-actions contract | integration/ | Response shape matches schema; picker behavior correct |
| `CompatRegressionTests` | Source-clean + hash-chain + no-leak | events/ + privacy/ | Artifact unchanged; hash chain valid; no evidence leak |
| `CompatDeterminismTests` | Cross-run determinism | exports/ | Two export runs produce identical output |
| `CompatDocTests` | Doc links, schema examples, command refs | build-docs/ | All links resolve; all schema examples parse; all commands documented |

---

## Corpus Maintenance Rules

1. **Never modify a frozen fixture.** If a bug is found in a fixture, add a
   new fixture with a documented migration note.
2. **Never delete a frozen fixture.** If a fixture tests a deprecated
   behavior, mark it as deprecated but keep it in the corpus.
3. **Add fixtures for every new stable interface.** A MINOR release that adds
   a command, event type, or flag must include corresponding fixtures.
4. **Run the full corpus in CI.** Every PR and release must run all corpus
   tests. Failures block merge and release.
5. **Publish corpus results with release notes.** Each release must include
   the number of fixtures run and any new additions.

---

## Current Coverage

All 10 fixture categories are defined above. The corresponding test classes
are specified in this corpus document for future implementation. Frozen
fixtures are to be placed under `tests/compat_fixtures/` and tested by
`tests/test_compat.py` when built per the test matrix below.

Initial v1.0 corpus specification: 40+ fixture definitions across 6 categories
covering all 7 event types, 38 error codes, 4 privacy modes, export determinism,
batch semantics, schema migration, and integration contracts.
