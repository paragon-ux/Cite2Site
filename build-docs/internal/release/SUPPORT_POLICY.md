# Support Policy — v1.0

**Status:** v1.0 stable. Effective from the v1.0.0 release tag.

---

## Supported Versions

| Version | Status | Support End |
|---|---|---|
| 1.0.x | Supported | Until 2.0.0 + 6 months |
| < 1.0 | Unsupported | N/A (pre-release) |

Only the latest PATCH release within a supported MINOR line receives updates.

---

## Supported Python Versions

Cite2Site v1.0 is built and tested on Python 3.11+. Earlier Python versions
are not supported. The `python_requires` in `pyproject.toml` enforces this.

---

## Supported Operating Systems

Cite2Site is tested on Linux, macOS, and Windows. The CI workflow
(`.github/workflows/ci.yml`) runs all tests on ubuntu-latest.
Platform-specific issues should be reported with full environment details.

---

## What Is Covered

- Command behavior matching the v1.0 Stable Contract.
- Deterministic replay and export for the same inputs.
- Source-clean citation (artifacts never modified).
- Hash-chain validation.
- Structured JSON errors with stable error codes.
- Privacy policy enforcement (metadata_only default, policy-gated snippet/link).

---

## What Is Not Covered

- Integration with specific editors, browsers, or document tools beyond the
  provided reference examples.
- Custom grouping dimensions or field-level projection profiles.
- Signed or encrypted export transport.
- Third-party runtime dependencies.
- Adapters beyond filesystem-text and markdown.

---

## Reporting Issues

Issues should include:

1. Cite2Site version (`python -m c2s --help` shows the version).
2. Python version (`python --version`).
3. Operating system and architecture.
4. Exact command that triggers the issue.
5. Structured error output (JSON from stderr).
6. Whether the issue is reproducible on a fresh repository.

---

## Security Issues

Report security issues privately. Do not include `.c2s/` authority files,
evidence text, or private-link URLs in public issues. See
`build-docs/internal/release/THREAT_PRIVACY_CHECKLIST.md` for the security
review process.

---

## Migration Support

When a future MAJOR release changes the authority schema, the release will
include migration procedures and fixtures. See
`build-docs/internal/release/SCHEMA_MIGRATION_POLICY.md` for the migration
policy.

---

## Deprecation Policy

- A stable interface may be deprecated in a MINOR release with a documented
  replacement.
- Deprecated interfaces remain functional through the next MAJOR release.
- Removal of a deprecated interface is a breaking change requiring a MAJOR bump.
