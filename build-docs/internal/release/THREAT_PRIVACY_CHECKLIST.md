# Threat And Privacy Checklist

**Status:** replacement checklist.

| Area | Requirement | Validation |
|---|---|---|
| Source-clean | Commands do not alter cited artifacts. | Source-byte tests. |
| Authority | Mutations write completed operations only. | Operation integrity tests. |
| Idempotency | Retries do not duplicate authority. | Idempotency tests. |
| Duplicates | Duplicate evidence is scoped, not rejected. | Supersession tests. |
| Publication | Metadata-only is default. | No-leak tests. |
| Archive | Archived repos fail before writes. | Rejection tests. |
| Integration | Native-host messages use replacement schemas. | Fixture and manual Chrome tests. |
