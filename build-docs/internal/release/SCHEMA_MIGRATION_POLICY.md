# Schema Migration Policy

**Status:** replacement policy.

The active replacement protocol does not migrate archived v0.3/v1 repositories.
Unsupported archived repositories fail closed before replay or writes.

Replacement schema changes must be represented as explicit replacement-schema
versions with tests and examples. Do not reuse archived schema IDs.
