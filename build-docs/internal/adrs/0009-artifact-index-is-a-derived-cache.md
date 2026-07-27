# ADR 0009: Artifact Index Is A Derived Cache

## Status

Accepted

## Context

Cite2Site's authority is deliberately narrow: citation history and handle
binding history are append-only records. The repository layout also includes
`artifact-index.jsonl`, and the grouping gate requires it to be populated.
Treating that index as a third authority history would create two competing
descriptions of the same citations and would make replay depend on mutable
index maintenance.

## Decision

`artifact-index.jsonl` is a deterministic, replaceable replay cache. It is
generated from the two authority histories and current artifact observations;
it is never read as evidence when replaying citations or validating integrity.
The cache contains one deterministic record per artifact and may be rewritten
atomically whenever a mutating command refreshes the projection.

## Alternatives Considered

- Make `artifact-index.jsonl` an append-only authority log. This duplicates
  citation membership and status facts, complicates repairs, and introduces
  cross-file consistency requirements.
- Do not persist an artifact index at all. This avoids a cache but leaves the
  documented repository layout and artifact-level inspection contract empty.
- Update the cache during read-only replay. This makes status and query
  commands mutate state, breaking replay's read-only guarantee.

## Consequences

- Deleting or corrupting the cache cannot change citation truth; a refresh
  recreates it from authority histories.
- Cache observations can lag an external source edit until the next mutating
  command or explicit projection refresh; authoritative replay remains
  current whenever it runs.
- Integrity checks continue to validate only authority histories, not cache
  continuity.

## Implementation Implications

- `replay()` builds indexes in memory and does not write files.
- `populate_artifact_index()` writes sorted JSONL records from a replay
  projection, using atomic replacement.
- Citation and handle mutations attempt a cache refresh only after successful
  authority appends. A refresh failure is returned as structured, non-fatal
  projection metadata and cannot recast a committed append as a failed action.
- Export and publication gates may refresh the cache, but must not treat it as
  their input authority.

## Validation Hooks

- TR-102 through TR-105 and TR indexing requirements.
- Tests prove cache records are deterministic and populated after mutation.
- Tests prove deleting the cache does not change replay output.
- Source-clean and event-chain tests remain unchanged because cache writes do
  not touch cited artifacts or authority histories.
