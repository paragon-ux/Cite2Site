# Publishing And Adoption Plan

## Local Adoption

The current entry point is local CLI use with generated citation projections:

1. install package;
2. initialize `.c2s`;
3. cite a Markdown or text file;
4. export local JSON and MkDocs projections;
5. inspect generated site files.

The configured default is `metadata_only`, and the export transform removes
accepted evidence before a default projection is returned or written.
`hash_only` keeps hashes and measurements but never accepted text. Snippets and
private links are refused unless repository policy explicitly authorizes them.

This requires no Git repository for the cited artifact. The citation repository
is separate so a user can preserve evidence references for documents, exported
conversations, or other files that do not belong to a code project.

## Agent Adoption

Agents should use:

- `cite-selection` for one citation;
- `cite-batch` for several citations;
- `lookup-actions` for a contextual-action contract that future integrations
  can render as a native menu;
- `status` and `export` for replay projections.

Agents should treat the citation repository as sensitive authority state even
when its default projections are metadata-only. A projection is safe only for
the configured mode; it does not grant rights to disclose the cited artifact.

## Publication

The citation repository can be versioned and published through a static host
such as GitHub Pages once a MkDocs build is configured. Cite2Site's generated
Markdown is a projection input, not a hosted service requirement. For local
preview, install MkDocs outside the stdlib core and run
`python -m mkdocs serve -f .c2s/site/mkdocs.yml`. Static hosting publishes the
generated `.c2s/site` projection and never becomes citation authority.

## Expansion Order

1. first-line handle mode and recovery workflows;
2. adapter conformance tests;
3. right-click integration examples;
4. hosted publication automation and review guidance.

## Adoption Boundaries

Cite2Site does not replace an editor, browser, version-control system, or
knowledge platform. Its contribution is a portable citation record that those
tools can create, inspect, and publish without owning the record themselves.
