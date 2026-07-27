# Publishing And Adoption Plan

## Local Adoption

The current entry point is local CLI use with generated flat projection files:

1. install package;
2. initialize `.c2s`;
3. cite a Markdown or text file;
4. export metadata-only pages;
5. inspect generated site files.

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

Agents should not inspect private source files when metadata-only export is
sufficient.

## Publication

The citation repository can be versioned and published through a static host
such as GitHub Pages once a MkDocs build is configured. Cite2Site's generated
Markdown is a projection input, not a hosted service requirement. Public
publication must default to metadata-only, and a publication gate must prove
that evidence text is absent before this becomes a release claim.

## Expansion Order

1. grouped indexes;
2. richer MkDocs pages;
3. privacy modes;
4. first-line handle mode;
5. adapter conformance tests;
6. right-click integration examples.

## Adoption Boundaries

Cite2Site does not replace an editor, browser, version-control system, or
knowledge platform. Its contribution is a portable citation record that those
tools can create, inspect, and publish without owning the record themselves.
