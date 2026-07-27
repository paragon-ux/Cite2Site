# ADR 0011: Policy-Gated Evidence Projections

## Status

Accepted

## Context

The earlier citation record shape stored accepted-evidence hashes and
measurements, but not the selected text. Privacy modes require a safe distinction between a
metadata-only public projection, a hash-bearing diagnostic projection, an
explicitly authorized snippet, and a private artifact link. Reconstructing a
snippet from the current artifact could disclose changed text that was never
accepted as evidence.

## Decision

Store the explicitly selected canonical text only within the append-only
citation authority record. Projection transforms remove it by default. A
repository publication policy authorizes `snippet` and `private_link` modes;
requests without the matching authorization fail with a structured policy
error. Private links require an absolute HTTPS base URL without credentials,
queries, or fragments. Snippets come only from accepted text and are bounded
deterministically.

## Alternatives Considered

- Reconstruct a snippet from the current artifact. This can disclose text that
  differs from accepted evidence.
- Omit snippets permanently. This avoids disclosure but leaves an approved
  privacy mode without useful, explicit behavior.
- Store snippets in generated site files. This makes derived output a source
  of evidence and breaks replay authority.

## Consequences

- Authority history can contain sensitive accepted text and must be protected
  as local citation state.
- Default and hash-only projections remain evidence-text free.
- Older events without retained accepted text can still replay safely but have
  no snippet to publish.

## Implementation Implications

- Citation creation records canonical accepted text beside its existing hash.
- `apply_privacy()` is a pure projection transform driven by effective policy.
- `E_PRIVACY_POLICY` reports disallowed rich-mode requests.
- Tests prove no-leak defaults, explicit rich-mode authorization, deterministic
  snippets, and source cleanliness.

## Validation Hooks

- G4 privacy transform and policy-refusal suites.
- TR privacy requirements and protocol privacy-mode contract.
- Security review of authority-only evidence text and generated projections.
