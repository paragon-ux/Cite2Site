# Engineering Overview

**Status:** replacement overview.

Cite2Site authority is append-only and operation based. A mutating command
must create a completed operation containing all required authority events.
Replay ignores derived files and builds projections from completed operations.

Archived repositories are rejected before replay or writes. Replacement
repositories use `project.json` for identity and `operations.jsonl` for
authority.
