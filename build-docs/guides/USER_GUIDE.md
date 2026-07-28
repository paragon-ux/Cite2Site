# User Guide

**Status:** replacement guide.

## What Cite2Site Does

Cite2Site records citations without changing the cited file. The citation
repository stores completed operations; status, exports, and published pages
are derived by replay.

## Replacement Concepts

- A citation ID identifies one intentional citation record.
- A group is a stable container with a `group_id`.
- A handle is a stable name object inside one group with a `handle_id`.
- Duplicate evidence can create another citation. Duplicate policy only
  determines scoped supersession in a group or handle.
- Retrying the same mutation uses an `idempotency_key`; it does not create a
  second citation.

## Basic Flow

```bash
python -m c2s init --repo .c2s --idempotency-key init-demo
python -m c2s cite-selection --repo .c2s --artifact notes.md --start 0 --end 11 --handle ALPHA --idempotency-key cite-alpha-1
python -m c2s status --repo .c2s
```

The old v0.3/v1 command behavior is archived outside this repository. Use only
the replacement docs for current behavior.
