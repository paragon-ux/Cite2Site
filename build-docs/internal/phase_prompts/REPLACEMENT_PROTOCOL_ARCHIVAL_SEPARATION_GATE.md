# Replacement Protocol and Archival Separation Gate

**Status:** active prerequisite gate. Gate 9 is blocked until this gate passes.

## Objective

Replace the active v0.3/v1 authority chain with the refined replacement
protocol boundary before any Chrome-extension or integration milestone resumes.

## Required Deliverables

- Active policy package references the refined reconciliation RFC and clean
  archival migration policy.
- Historical v0.3/v1 material is excluded from active reading order.
- Active implementation and schema specifications describe replacement objects,
  completed operations, idempotency, groups, handles, tallies, scoped
  supersession, and reconciliation.
- Requirements, workflow, status, AGENTS, and the build-doc map stop claiming
  v0.3/v1 as current active authority.
- Archived-format repositories have specified fail-closed behavior.
- Interrupted Gate 9 work is preserved but not integrated.

## Non-Goals

- No in-place migration from v0.3/v1 repositories.
- No compatibility bridge or version switch.
- No Chrome-extension milestone work.
- No automatic import utility.

## Acceptance

This gate is accepted only when active docs have one clear protocol authority,
archived documents are not in the active reading order, replacement schemas are
indexed or explicitly pending, status labels are truthful, and tests prove
archived-format repositories fail closed before writes once replacement runtime
work begins.
