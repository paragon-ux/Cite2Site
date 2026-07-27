# End-To-End Narrative

## Current CLI Journey

1. A person or agent works with a local text or Markdown file.
2. They select a range and invoke `cite-selection`, optionally supplying a
   handle, tags, and a note.
3. Cite2Site records accepted evidence, locator, artifact identity, and handle
   binding in `.c2s`.
4. The source artifact remains unchanged.
5. `status` replays citation history against the current artifact observation.
6. `export` generates flat JSON and minimal MkDocs projection files.
7. A future agent can consume the structured projection rather than receiving a
   copied conversational log.

## Intended Integration Journey

1. A user works in an editor, browser, document tool, or another supported
   surface.
2. They select evidence and choose `Cite with C2S` from a native context menu.
3. The integration calls the same citation contract as the CLI; it does not
   create an overlay database or source marker.
4. Later, the integration calls `lookup-actions` for the region. If citations
   overlap, it presents an ordered picker before any mutation.
5. Once recovery commands exist, accepted evidence, relocation, retraction, and
   restoration will append compensating events rather than rewrite history.
6. Grouped projections will make a published site navigable by artifact,
   handle, tag, status, and batch.

The key design choice is that neither the original artifact nor the generated
site is the citation authority. Authority remains in append-only history.
