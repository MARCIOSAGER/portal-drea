# shared/assets/icons/

## `sprite.svg`

Single SVG sprite containing all icons used by the Design System SGA. Each icon
is a `<symbol id="icon-NAME">` and is referenced from HTML as:

```html
<svg class="icon"><use href="#icon-NAME"/></svg>
```

The whole sprite is injected at build time as the first child of `<body>` in each
portal HTML, styled `display:none aria-hidden="true"` so it contributes zero
layout. Only its `<symbol>` definitions are picked up by `<use>` references
elsewhere in the document.

## Conventions

- **viewBox**: always `0 0 24 24`
- **fill/stroke**: use `stroke="currentColor"` (or `fill="currentColor"`) so colour
  is controlled by the parent CSS context via the `color` property
- **stroke-width**: 1.5 or 2 (match Heroicons Outline convention)
- **`<title>`**: always include — provides accessible name to screen readers
- **Ids**: `icon-NAME` where NAME is kebab-case

## Base

Icons are derived from [Heroicons Outline v2](https://heroicons.com/) (MIT
License, Copyright Refactoring UI Inc.). New icons may be added by:

1. Adding a source SVG under `sources/icon-NAME.svg` (optional, for editing)
2. Copying the `<path>` markup into a new `<symbol>` in `sprite.svg`
3. Adjusting stroke-width and viewBox to match

## Plan evolution

- **Plan 1**: seeds 3 icons (sga-mark, menu, close) to validate the pipeline.
- **Plan 2**: expands to ~20 (navigation, status, action icons).
- **Plan 3**: adds chrome icons (user, airplane, helmet, fire, shield, siren).

## Rationale for inline sprite vs other approaches

Icon fonts (Font Awesome, Material Icons) were considered and rejected: they
require either a CDN (blocked by airport firewalls) or a separate font file
(violates the single-file HTML constraint). Inline SVG sprite is the only
approach that keeps everything in one file, works offline, and preserves full
icon fidelity.
