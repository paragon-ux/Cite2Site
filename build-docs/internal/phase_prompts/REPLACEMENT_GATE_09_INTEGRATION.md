# R9: Integration And Chrome Extension

**Status:** planned.

## Objective

Implement the replacement-aware native-host and Chrome-extension integration.

## Deliverables

- Native-host dispatch uses replacement schemas and commands.
- Extension lookup, cite, group, handle, and duplicate displays use stable IDs.
- Mutating messages include `idempotency_key`.
- Package build includes the replacement native-host implementation.
- Gate 9 manual validation script is current and replacement-aware.

## Acceptance

- Integration fixtures validate message shapes.
- Native-host smoke tests pass.
- Package builds and installs locally.
- Manual Chrome validation passes. If manual validation is needed, stop and
  ask the user before marking this gate Done.
