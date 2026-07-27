# Phase 07: v1 Stabilization

**Status:** authorized only after Phase 06 release and migration hardening is accepted.

## Purpose

Freeze a durable public contract for people, agents, and integrations. v1 is a
claim of compatibility discipline, not merely a feature count.

## Required Reading

Read every active requirement, ADR, protocol/specification, schema, CI and
release document, status matrix, and completed phase prompt. Reconcile any
contradiction before declaring a compatibility boundary.

## Scope

Stabilize the event schema, CLI, JSON envelopes, MkDocs projection shape,
privacy policy, adapter conformance rules, migration policy, user guide, agent
guide, and reference examples.

## Non-Goals

- Do not add a speculative feature merely to increase the v1 scope.
- Do not preserve an unstable interface without documenting its migration path.
- Do not call an output stable while its ordering, privacy fields, or error
  codes can change without versioning.

## Required Decisions

1. Identify every v1-stable command, flag, event field, projection field,
   schema identifier, error code, and generated-site URL shape.
2. Identify each explicitly experimental or deferred surface and its isolation
  boundary.
3. Define semantic-versioning and deprecation policy for CLI, schema, and site
   projections.
4. Define a compatibility test corpus that future releases must preserve.

## Required Changes

- Version and freeze v1 schemas and examples.
- Publish complete user and agent guides grounded in implemented workflows.
- Add compatibility fixtures for histories, batch requests, response envelopes,
  grouped exports, privacy modes, and integration contracts.
- Finalize release notes, threat/privacy review, support policy, and migration
  guide.
- Update every status row from Target/Partial only when its evidence exists;
  defer remaining work explicitly rather than hiding it.

## Required Tests

- Full compatibility suite against frozen fixtures.
- Cross-version migration and downgrade/refusal tests.
- Deterministic output comparison across supported runtimes.
- Source-clean, privacy no-leak, ambiguous-mutation, and hash-chain integrity
  regression suites.
- Documentation link, schema/example, and command-reference consistency checks.

## Acceptance Criteria

v1 is accepted only when there are no known untested authority paths, no known
privacy leak in default publication, all stable interfaces have compatibility
fixtures, and the source, tests, requirements, specifications, ADRs, and public
guides make the same claims.

