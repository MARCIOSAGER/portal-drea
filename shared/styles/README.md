# shared/styles/ — Design System SGA CSS

This directory contains the Design System SGA CSS, concatenated by each portal's
`build.py` at build time and injected into the `{{DS_CSS}}` placeholder.

## Cascade order (critical — do not change without updating `ds_build_helpers.py`)

1. `tokens/primitive.css` — Layer 1, raw values. Never referenced by components.
2. `tokens/semantic.css` — Layer 2, aliases with meaning. Components reference these only.
3. `tokens/density-{compact|comfortable}.css` — only ONE loaded, selected by `build.py` based on `portal.config.json`.
4. `base/fonts.css` — `@font-face` declarations (Inter Variable, base64-embedded).
5. `base/*.css` — `reset.css`, `typography.css`, `global.css` (added in Plan 2, not Plan 1).
6. `chrome/*.css` — `shell-bar.css`, `sidebar.css`, etc. (Plan 3).
7. `components/*.css` — alphabetical (Plan 2).
8. `print/print.css` — last (Plan 3).

## Namespace

During the migration (Plans 1-4), all tokens use the `--ds-*` prefix to avoid
collision with legacy variables like `--dark-blue`, `--medium-blue` that still
exist in the portal source HTMLs. In Plan 5 the namespace is removed globally.

## Governance

- **Components are auto-contained.** A file in `components/` never depends on
  another file in `components/`. Each component selects its own semantic tokens.
- **Primitives are opaque.** Components reference semantic tokens, never primitives.
- **Adding a new component** = create `components/<name>.css`, import semantic
  tokens as needed, follow existing conventions.
- **Adding a new token** = add to `primitive.css` first (if new raw value), then
  alias in `semantic.css` (if semantic meaning needed), then reference in components.

See `docs/superpowers/specs/2026-04-11-design-system-sga-design.md` for the full
design rationale and token catalogue.
