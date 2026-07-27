# End-To-End Narrative

1. A user works in a normal document, note, exported conversation, or code file.
2. The user selects a passage and chooses `Cite with C2S`.
3. Cite2Site records accepted evidence, locator, artifact identity, and optional
   handle in `.c2s`.
4. The source artifact remains unchanged.
5. The user or agent continues working.
6. Later, the user right-clicks the cited region to rename a handle, open the
   citation, undo, redo, accept current evidence, relocate, or retire.
7. Cite2Site appends another event rather than editing history.
8. `status` replays citation history against current artifacts.
9. `export` generates JSON and MkDocs pages.
10. The user publishes the site through static hosting.
11. A future agent can read the citation site or JSON export to recover durable
    context without receiving a pasted log.

The key design choice is that neither the original artifact nor the generated
site is the citation authority. Authority remains in append-only history.
