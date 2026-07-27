# Phase 06: CI, Release, And Migration

**Status:** authorized after Phase 05 integration examples are accepted.

## Purpose

Make Cite2Site reproducible, releasable, and safely evolvable. A release is not
only a package version: it is a verified agreement among authority records,
CLI contracts, schemas, generated projections, migration policy, and docs.

## Required Reading

Read `AGENTS.md`, `DOCUMENTATION_STANDARD.md`, CI validation, the project plan,
status matrix, all active schemas, and the release/migration sections of the
specifications.

## Scope

Complete remote CI evidence, package build checks, release checklist,
changelog, threat/privacy checklist, schema migration policy, and migration
fixtures. Close the baseline CI gate only when its remote execution is observed.

## Non-Goals

- Do not introduce breaking schema changes without a versioned migration path.
- Do not mark a release ready solely because local tests pass.
- Do not make Git mandatory for cited artifacts; Git may version the citation
  repository and release source.

## Required Changes

- Ensure CI covers a clean install, unit tests, compile, CLI help, smoke flow,
  documentation links, JSON fixtures, source cleanliness, and deterministic
  export checks where implemented.
- Add package build and installation-from-artifact checks.
- Define supported schema versions, compatibility window, migration command or
  documented procedure, backup behavior, and refusal behavior.
- Add changelog and release checklist covering security, privacy, documentation
  truth labels, dependency review, and rollback plan.
- Record the first observed remote CI run and any platform-specific constraints
  in the status matrix.

## Required Tests

- Migration fixtures for every supported previous schema.
- Corrupt/unknown-version fixtures that fail with stable diagnostics and do not
  rewrite authority history.
- Clean-checkout smoke on every supported Python version.
- Package artifact install and CLI execution test.
- Deterministic export and documentation validation in CI.

## Acceptance Criteria

The phase is accepted only when CI is remotely observed green, a release can be
built and installed from a clean checkout, migrations are tested and reversible
or explicitly refuse, and all release documents identify current behavior
without promising future work.

