# CI Validation

**Status:** current internal CI contract.

CI is the automated enforcement layer for session gates. It must stay aligned
with `BUILD_WORKFLOW_CURRENT.md` and `AGENTS.md`.

## Documentation Integrity

The local link check verifies the mapped build-doc set, including external
narratives and ADRs. It does not establish that prose is truthful, so every
documentation gate must also review maturity labels, cross-references, and
current-versus-target language against the status matrix.

## Workflow File

Authoritative CI implementation:

- `.github/workflows/ci.yml`

The workflow runs on pull requests and pushes to `main` or `codex/**`
branches.

## Required CI Checks

Every CI run must verify:

1. clean checkout package install with `python -m pip install -e .`;
2. build-doc local Markdown links;
3. build-doc JSON schema and example parsing;
4. `AGENTS.md` reading-order targets exist;
5. unit tests with `python -m unittest discover -s tests`;
6. import/compile health with `python -m compileall src`;
7. CLI help with `python -m c2s --help`;
8. archived-format repository rejection before replacement replay or writes,
   once replacement runtime work begins;
9. source-clean behavior for any replacement command touching artifacts;
10. expected replacement projections are generated once projection work begins.

The check list is evidence, not ceremony. A changed public behavior must add a
test at the layer where it can regress: core/replay, CLI envelope, generated
projection, or integration fixture.

## Python Matrix

Current matrix:

- Python 3.11;
- Python 3.12.

The project currently declares `requires-python = ">=3.11"`, so CI should not
test older Python versions.

## Gate Expansion Rules

When a session gate adds behavior, CI must expand in the same gate if the new
behavior is part of a public or agent-facing contract.

Examples:

- R1 repository identity adds replacement init and archived-repository
  rejection checks.
- R2 atomic operations adds idempotency and incomplete-operation checks.
- R3 citations adds distinct duplicate-evidence citation and source-clean
  checks.
- R4/R5 group and handle gates add complete rolling-tally checks.
- R6 duplicate policy adds scoped supersession checks.
- R7 reconciliation adds replacement-only merge-direction checks.
- R8 projections adds deterministic export and metadata-only no-leak checks.
- R9 integration adds native-host fixtures, package build, and manual Chrome
  evidence.

## Local Equivalent

Before reporting a gate as accepted, run the local equivalent of the CI stack:

```powershell
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
```

Also run docs validation and command-specific smoke checks for changed
replacement surfaces. Old v0.3/v1 CLI smoke checks are not active replacement
conformance.

For a documentation-only gate, validate local links, parse JSON schemas and
examples, search for unresolved placeholders and obsolete project references,
and confirm the current/target boundary remains coherent across the status
matrix, requirements, workflow, and specifications.

## Remote Status

Until a branch is pushed and GitHub Actions completes, CI status is local-file
ready but remote-unverified. The current status matrix must distinguish those
states.
