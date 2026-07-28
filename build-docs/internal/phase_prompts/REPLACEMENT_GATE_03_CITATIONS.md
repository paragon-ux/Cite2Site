# R3: Citations And Fingerprints

**Status:** planned.

## Objective

Implement record-instance citation creation and deterministic target
fingerprints without artifact mutation.

## Deliverables

- Distinct `citation_id` allocation per intentional citation.
- Deterministic `target_fingerprint` for duplicate buckets.
- Source observation and locator validation.
- Source-clean regression tests.

## Acceptance

- Identical evidence in two distinct operations receives two distinct
  citation IDs.
- Idempotent retry returns the first citation ID and appends no duplicate.
- Cited artifact bytes are unchanged.
