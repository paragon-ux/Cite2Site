# Replacement Schema Index

**Status:** active schema inventory, schemas pending.

The v0.3/v1 schema inventory at `build-docs/architecture/SCHEMA_INDEX.md` is
historical and unsupported by the active replacement runtime.

## Required Replacement Schema Families

The replacement protocol requires schemas for:

- repository/project identity;
- atomic operation envelope;
- completed operation record;
- citation creation with record-instance `citation_id`;
- target fingerprint;
- group creation, rename, move, merge, retire, and alias;
- group membership add, remove, restore, and supersession;
- handle creation, rename, merge, retire, and alias;
- handle binding add, remove, restore, and supersession;
- global citation retraction and restoration;
- duplicate policy configuration;
- group rolling-tally projection;
- handle rolling-tally projection;
- status and publication projections;
- reconciliation request, plan, conflict, and result;
- archived-protocol rejection error.

No replacement schema is accepted until it has a checked JSON schema, example,
and test evidence. The active implementation must not reuse v0.3/v1 schema IDs
for replacement objects.
