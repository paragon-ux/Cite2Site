# Release Checklist

**Status:** internal release procedure.

## Authority And Scope

This checklist is used by a maintainer preparing a Cite2Site release candidate.
It does not mark a release ready by itself. Release readiness requires matching
evidence in the current status matrix, passing local validation, and observed
remote CI when the release gate requires it.

Relevant authority:

- [CI validation](../CI_VALIDATION.md)
- [Current status matrix](../CURRENT_STATUS_MATRIX.md)
- [Project plan](../PROJECT_PLAN.md)
- [Documentation standard](../DOCUMENTATION_STANDARD.md)
- [Implementation specification](../../architecture/CITE2SITE_IMPLEMENTATION_SPEC_V0_3.md)
- [Protocol specification](../../architecture/CITE2SITE_PROTOCOL_SPEC_V0_3.md)
- [Schema index](../../architecture/SCHEMA_INDEX.md)
- [Schema migration policy](SCHEMA_MIGRATION_POLICY.md)
- [Threat and privacy checklist](THREAT_PRIVACY_CHECKLIST.md)
- [Local package artifact check](../../../tools/check_package_artifact.py)

## Release Candidate Inputs

Record these before starting the checklist:

| Field | Value |
|---|---|
| Candidate version | |
| Git branch | |
| Commit SHA | |
| Python versions validated locally | |
| Remote CI run URL | |
| Remote CI conclusion | |
| Release owner | |
| Date | |

Remote CI fields may remain blank for local-only preparation work, but a public
release must not proceed while they are blank.

## Current-State Truth Review

1. Compare every release note claim against
   [CURRENT_STATUS_MATRIX.md](../CURRENT_STATUS_MATRIX.md).
2. Confirm every user-visible capability in the changelog is labelled Done or
   Partial in the status matrix with evidence.
3. Confirm Target and Open capabilities are not described as available.
4. Confirm external docs do not imply right-click integrations, rich adapters,
   lifecycle commands, or remote publication features are shipped unless the
   status matrix says so.
5. Confirm no release document treats generated exports, MkDocs pages, or
   artifact indexes as authority.

## Local Validation

Run these commands from a clean working tree or record why the tree cannot be
cleaned:

```powershell
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
python tools/check_package_artifact.py
```

The package artifact check must build an installable artifact and validate the
installed package, not the source checkout.

## Documentation Validation

1. Parse every JSON file under `build-docs/`.
2. Check every local Markdown link under `build-docs/`.
3. Confirm every `AGENTS.md` reading-order target exists.
4. Search changed docs for stale internal references, outdated phase claims,
   and unlabelled Target language.
5. Confirm architecture, workflow, and release docs agree on schema versions,
   publication privacy defaults, and source-clean authority.

## Package Artifact Validation

1. Build the wheel from the candidate source tree.
2. Install the wheel into a new temporary virtual environment with `--no-deps`.
3. Run the installed package with `python -m c2s --help`.
4. Run `init`, `cite-selection`, `lookup-actions`, `status`, `citations`,
   `export`, and `check` through the installed package.
5. Hash the cited artifact before and after the smoke flow.
6. Verify required flat and grouped export files exist.
7. Run export twice and compare projection bytes for deterministic output.
8. Delete the temporary environment unless debugging requires preserving it.

## Schema And Migration Review

1. List every supported schema version.
2. Confirm new schema versions have migration fixtures before release.
3. Confirm unknown or corrupt schema fixtures fail with stable diagnostics.
4. Confirm migration procedures back up authority files before writing.
5. Confirm migration procedures never rewrite cited artifacts.
6. Confirm generated projections are regenerated after migration rather than
   migrated as authority.

## Security, Privacy, And Dependency Review

1. Complete [THREAT_PRIVACY_CHECKLIST.md](THREAT_PRIVACY_CHECKLIST.md).
2. Confirm `pyproject.toml` still has no runtime dependencies unless a
   dependency ADR and review exist.
3. Confirm packaging metadata does not include local secrets, temporary paths,
   generated `.c2s` repositories, or private artifacts.
4. Confirm default exports are `metadata_only`.
5. Confirm snippet and private-link projections remain policy-gated.

## Release Decision

Use these outcomes:

| Outcome | Meaning |
|---|---|
| Proceed | Local validation passes, remote CI is observed green, and release docs match current status. |
| Hold | A non-release-blocking issue needs owner review before publishing. |
| Block | Validation fails, CI is absent for a public release, privacy review fails, or docs overstate current behavior. |

Record the decision, evidence links, and rollback owner before tagging.

## Rollback Plan

1. Stop publication of the release artifact.
2. Leave citation repositories untouched.
3. Publish a corrective changelog entry that identifies the affected package
   version and the safer replacement version or commit.
4. If a schema migration was released, document whether repositories that ran it
   can continue safely, need restoration from the migration backup, or require a
   forward repair.
5. Open a follow-up issue or gate with exact validation evidence.
