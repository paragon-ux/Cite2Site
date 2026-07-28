# Release Checklist

**Status:** replacement release checklist.

Do not release while any active replacement gate needed by the advertised
behavior is Planned or Partial.

Required evidence:

- full replacement unit suite passes;
- `python -m compileall src` passes;
- CLI help and changed command smokes pass;
- docs link and JSON parse checks pass;
- package build passes;
- installed native host points at a replacement repository;
- metadata-only no-leak checks pass for publication;
- manual Chrome validation passes for R9 integration releases.
