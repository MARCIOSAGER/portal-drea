# shared/assets/fonts/

## Inter Variable Font

**File:** `Inter-VariableFont.woff2`
**Source:** https://github.com/rsms/inter
**Downloaded from:** https://github.com/rsms/inter/raw/master/docs/font-files/InterVariable.woff2
**License:** SIL Open Font License 1.1 — see `LICENSE-OFL.txt`
**Downloaded on:** 2026-04-11 (during Plan 1 Task 7)

## Usage by Portal DREA

The Inter Variable woff2 is read at build time by `scripts/ds_build_helpers.py::encode_font_woff2_base64`,
base64-encoded, and injected into each portal HTML via the `{{DS_INTER_WOFF2_BASE64}}`
placeholder inside `shared/styles/base/fonts.css`. This makes each portal HTML
self-contained — no CDN calls, no external font files, works offline.

## Updating Inter

1. Download the new `InterVariable.woff2` from https://github.com/rsms/inter/releases
2. Replace `Inter-VariableFont.woff2` in this directory (keep the same filename)
3. Run `python scripts/build-all.py` and verify both portals still build OK
4. Manual smoke test: open each HTML in a browser and verify text still renders
   with Inter (should look the same unless Inter's glyph metrics changed)
5. Update the "Downloaded on" date in this README
6. Commit with a message like `chore(ds): update Inter Variable to vX.Y.Z`

## Why not use a CDN?

Portal DREA is distributed as a single self-contained HTML file that must work
offline in airport operations rooms. CDNs may be blocked by airport firewalls,
may be unavailable during incidents, and introduce external trust. Embedding the
font as base64 inside the HTML adds ~200 KB per portal but eliminates all
runtime network dependencies.
