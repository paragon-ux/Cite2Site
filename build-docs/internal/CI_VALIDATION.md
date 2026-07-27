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
8. CLI smoke flow covering `init`, `cite-selection`, `lookup-actions`,
   `status`, `export`, and `check`;
9. source-clean behavior during the smoke flow;
10. expected flat export files are generated.

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

- G1 grouping/indexing adds grouped replay unit tests.
- G2 query CLI adds `c2s citations` smoke checks.
- G3 grouped export adds generated grouped-file checks.
- G4 privacy modes adds no-leak export checks for every publication mode.
- G5 workflow commands adds smoke checks for new mutating commands and
  structured errors.
- G6 adapter hardening adds adapter conformance fixture checks.
- G7 integration contracts adds fixture-based `lookup-actions` examples.
- G8 release hardening adds package build and migration fixture checks.

## Local Equivalent

Before reporting a gate as accepted, run the local equivalent of the CI stack:

```powershell
python -m unittest discover -s tests
python -m compileall src
python -m c2s --help
```

Also run docs validation and command-specific smoke checks for changed
surfaces. The exact local command may differ from CI shell syntax, but the
validated behavior must be the same.

For a documentation-only gate, validate local links, parse JSON schemas and
examples, search for unresolved placeholders and obsolete project references,
and confirm the current/target boundary remains coherent across the status
matrix, requirements, workflow, and specifications.

## Remote Status

Until a branch is pushed and GitHub Actions completes, CI status is local-file
ready but remote-unverified. The current status matrix must distinguish those
states.
