# Changelog

All notable Cite2Site release changes are recorded here. This changelog is a
maintainer release artifact, not capability authority; current availability is
still determined by `build-docs/internal/CURRENT_STATUS_MATRIX.md`.

## Unreleased

### Added

- Added the G8 release-documentation slice:
  - release checklist:
    `build-docs/internal/release/RELEASE_CHECKLIST.md`;
  - threat and privacy checklist:
    `build-docs/internal/release/THREAT_PRIVACY_CHECKLIST.md`;
  - schema migration policy and procedure:
    `build-docs/internal/release/SCHEMA_MIGRATION_POLICY.md`;
  - local package artifact check:
    `tools/check_package_artifact.py`.
- Added a local package validation path that builds a wheel, installs that
  wheel into a temporary virtual environment, runs the installed CLI, executes
  a source-clean citation smoke flow, writes export projections, and verifies
  repeat export determinism.

### Release Notes

- Remote CI evidence is intentionally not recorded here. A release entry may
  link to remote CI only after the run has actually completed.
- Cite2Site still has a stdlib-only runtime dependency set. The local artifact
  check uses Python packaging tools through `pip`; it does not add runtime
  package dependencies.

## 0.3.0

### Status

- Planned local first-slice version. See the current status matrix for the
  exact implemented capability set and release readiness.
