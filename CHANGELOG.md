# Changelog

All notable Cite2Site release changes are recorded here. This changelog is a
maintainer release artifact, not capability authority; current availability is
still determined by `build-docs/internal/CURRENT_STATUS_MATRIX.md`.

## Unreleased

### Added

- G6 adapter hardening:
  - adapter protocol (`src/c2s/adapter.py`): `BaseAdapter` ABC, `FilesystemTextAdapter`,
    `MarkdownAdapter`, registry, diagnostics;
  - adapter conformance harness (`tests/test_adapter_conformance.py`): 35 test
    methods covering all 8 contract methods across both adapters;
  - workspace boundary enforcement (`E_ARTIFACT_OUTSIDE_WORKSPACE`).
- G7 integration examples:
  - integration contract documentation
    (`build-docs/architecture/INTEGRATION_CONTRACT.md`);
  - editor plugin mock (`examples/integration/editor_plugin_mock.py`);
  - updated integration fixtures and README.
- G8 release hardening:
  - migration fixture tests (`tests/test_migration_fixtures.py`): 9 tests
    covering schema version validation, corrupt-file rejection, hash-chain integrity,
    and source preservation.
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
