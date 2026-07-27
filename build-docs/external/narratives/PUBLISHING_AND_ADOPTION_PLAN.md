# Publishing And Adoption Plan

## Local Adoption

Start with local CLI and generated MkDocs files:

1. install package;
2. initialize `.c2s`;
3. cite a Markdown or text file;
4. export metadata-only pages;
5. inspect generated site files.

## Agent Adoption

Agents should use:

- `cite-selection` for one citation;
- `cite-batch` for several citations;
- `lookup-actions` for contextual right-click behavior;
- `status` and `export` for replay projections.

Agents should not inspect private source files when metadata-only export is
sufficient.

## Publication

The citation repository can be pushed to GitHub and published with GitHub Pages
after MkDocs generation. Public publication must default to metadata-only.

## Expansion Order

1. grouped indexes;
2. richer MkDocs pages;
3. privacy modes;
4. first-line handle mode;
5. adapter conformance tests;
6. right-click integration examples.
