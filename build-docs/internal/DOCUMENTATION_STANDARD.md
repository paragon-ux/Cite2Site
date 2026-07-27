# Cite2Site Documentation Standard

**Status:** internal documentation authority.

## Purpose

Cite2Site documentation is part of the product's trust boundary. It must let a
reader understand what the system claims, why the claim is defensible, what is
implemented today, and how a maintainer can falsify or verify the claim. It is
not a place to make the architecture sound smaller, friendlier, or more
complete than it is.

The project therefore aims for scholarly rigor and proportionate friendliness:
public documents explain consequences in ordinary language; internal documents
state scope, authority, evidence, and acceptance conditions precisely.

## Non-Negotiable Qualities

Every maintained document must answer, where relevant:

1. **Audience:** who should rely on this document?
2. **Authority:** is it explanatory, a decision record, a requirement, a
   protocol contract, or a current-state report?
3. **Truth state:** which statements describe implemented behavior, which are
   approved target behavior, and which remain open?
4. **Rationale:** why does the rule or decision exist, including meaningful
   alternatives and constraints?
5. **Verification:** how can a reader test, inspect, or disprove the claim?

Do not trade any of these for brevity. Concision is useful only after the
reader can establish the above without inference.

## Evidence And Terminology

- Preserve the source-clean invariant: cited artifacts are not citation state.
- Treat `.c2s` histories as authority and status, exports, sites, and indexes
  as replay projections.
- Distinguish accepted evidence from a later observation of the artifact.
- Do not call a citation "stale" or describe it as refreshing itself. Replay
  can report a changed, missing, or resolved observation while history remains
  append-only.
- Use normative language deliberately: **must** for a binding requirement,
  **should** for a recommended but defeasible practice, and **may** for an
  option. Never use these words casually.

## Truth Labels

Use these labels whenever a document spans more than one maturity state:

| Label | Meaning | Required evidence |
|---|---|---|
| **Implemented** | Present in the checked-in runtime. | Test, CLI check, or source reference. |
| **Partial** | Present, but a named limitation prevents the target claim. | Limitation and next gate. |
| **Target** | Approved design contract not yet delivered. | Requirement and planned validation. |
| **Open** | A decision remains unresolved. | Owner or decision trigger. |

External documents may use plain language instead, but must not imply that a
Target capability is currently usable.

## Document Shapes

### External documents

Open with the problem and the practical consequence for the reader. Explain
the source-clean model before implementation details. State current availability
plainly, then describe intended integrations as future work. Avoid marketing
language, invented certainty, and internal gate terminology.

### Internal requirements and workflow documents

State the authority level, scope, dependencies, requirement identifiers, and
acceptance evidence. A workflow is not an aspiration: every step must map to a
command, event, projection, or explicit future integration contract.

### ADRs

Every decision record must include context, decision, alternatives considered,
consequences, implementation implications, and validation hooks. An ADR records
why a decision was made; it does not claim that its implementation is complete.

### Architecture specifications and schemas

Begin with intent, scope, and maturity. Define terms before relying on them.
For each behavior, state inputs, outputs, mutation authority, failure mode, and
deterministic ordering where applicable. JSON Schema captures shape, not all
semantic invariants; list semantic checks explicitly.

## Maintenance Rule

When behavior changes, update in the same gate:

1. the status matrix;
2. the relevant requirement and workflow;
3. the protocol/specification and schema/example when a contract changes;
4. the test or smoke evidence that supports the new truth label.

When a document is absent from the worktree, do not silently recreate or
rewrite it. Record the availability issue and preserve its owner-controlled
state.

