# Agent Guidance

Cite2Site is source-clean and append-only.

- Do not add markers to cited artifacts.
- Treat `.c2s/citation-history.jsonl` and `.c2s/handle-bindings.jsonl` as the
  authority files.
- Treat status, exports, and MkDocs pages as replay projections.
- Handles are editable aliases, not citation identity.
- For overlapping contextual hits, mutating actions must name a concrete
  `citation_id`.
- Static-site publication defaults to metadata-only.
- Use `python -m unittest discover -s tests` before reporting code changes.
