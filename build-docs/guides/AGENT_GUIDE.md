# Agent Guide

**Status:** replacement agent guide.

## Rules For Agents

1. Never mutate cited artifacts.
2. Never read archived v0.3/v1 ledgers as active authority.
3. Include an `idempotency_key` on every mutating command.
4. Treat `citation_id`, `group_id`, `handle_id`, and `operation_id` as stable
   authority IDs.
5. Do not reject duplicate evidence locally.
6. Do not text-merge authority logs.

## Replacement Command Contract

Commands are delivered gate by gate. A mutating command is conformant only when
it writes one completed operation with a semantic payload hash and returns the
same result on an idempotent retry.

Read-only commands may produce projections, but projections are not authority.
