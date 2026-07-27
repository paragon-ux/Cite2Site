# Cite2Site

Cite2Site (C2S) is a source-clean universal citation tool. It records accepted
evidence in a dedicated citation repository, then replays that append-only
history into JSON and MkDocs-friendly projections.

Core first-slice commands:

```bash
python -m pip install -e .
python -m c2s init
python -m c2s cite-selection --artifact notes.md --start 0 --end 42 --handle NOTE-1
python -m c2s cite-batch --request batch.json
python -m c2s set-handle --citation-id sha256:... --handle FRIENDLY-HANDLE
python -m c2s lookup-actions --artifact notes.md --start 10 --end 10
python -m c2s status
python -m c2s export
```

The source artifact is never rewritten. Handles are editable aliases over
immutable citation IDs. Static-site export defaults to metadata-only.

## Validation

```bash
python -m unittest discover -s tests
```

## Build Documentation

The end-to-end build plan, requirements, workflows, whitepaper, specification,
current status matrix, and ADRs live under [build-docs/](build-docs/README.md).
