# Build Readiness Contract

The first Cite2Site build slice implements:

1. dedicated `.c2s` citation repository initialization;
2. filesystem text and Markdown adapters;
3. `cite-selection`;
4. `cite-batch`;
5. `set-handle`;
6. `lookup-actions`;
7. replay `status`;
8. MkDocs JSON/Markdown export;
9. metadata-only publication by default;
10. structured JSON errors for every command.

Authority lives in append-only history files:

```text
.c2s/citation-history.jsonl
.c2s/handle-bindings.jsonl
```

Source artifacts are never rewritten. Handles are editable aliases over
immutable citation IDs. Replay computes projected state from history plus
current artifact observations.
