# Design System SGA — Plan 1: Foundation Dormant (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Populate `shared/` with the Design System SGA foundation (tokens, Inter font, minimal SVG sprite), extend both `build.py` scripts to consume these inputs, and produce `dist/` HTMLs that render **visually identical** to the current `v2.0.0-beta.1` output while carrying the dormant design system payload.

**Architecture:** Layer 1 (primitive) and Layer 2 (semantic) tokens live in `shared/styles/tokens/` with a `--ds-*` namespace prefix to avoid collision with legacy `--dark-blue`, `--medium-blue` variables. Both `build.py` scripts import a new shared helper module `scripts/ds_build_helpers.py` containing: `load_portal_config`, `resolve_density`, `compile_design_system_css`, `encode_font_woff2_base64`. New placeholders (`{{DS_CSS}}`, `{{DS_INTER_WOFF2_BASE64}}`, `{{ICON_SPRITE}}`, `{{PORTAL.*}}`, `{{BUILD_TIMESTAMP}}`) are resolved by extending the existing `substitute_placeholders` mechanism. The new `<style>` block is positioned **before** the legacy block in each source HTML so legacy wins any specificity ties — components not yet migrated continue to behave identically.

**Tech Stack:** Python 3.8+ (build scripts), pytest (unit tests for helpers), vanilla CSS (tokens), Inter Variable woff2 (SIL OFL), Heroicons Outline (MIT, for initial sprite seed), git (atomic commits, worktree isolation).

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) (v1.1 approved 2026-04-11)

**Invariant this plan must preserve:** after running `python scripts/build-all.py` with Plan 1 fully executed, opening both `dist/Portal_COE_AWM.html` and `dist/Portal_PSCI_AWM.html` side-by-side with the previous version must show **zero visual differences**. The dormant foundation is loaded (`@font-face`, CSS tokens, hidden sprite) but nothing consumes it yet.

**Out of scope for Plan 1** (deferred to later plans):
- `shared/styles/base/reset.css`, `typography.css`, `global.css` — would affect existing layout, deferred to Plan 2
- `shared/styles/chrome/*.css` — Plan 3
- `shared/styles/components/*.css` — Plan 2
- `shared/styles/print/print.css` — Plan 3
- `shared/scripts/awm-*.js` extraction — Plan 2
- Logo SGA inline SVGs — Plan 3 (no consumer yet)
- Full ~40 icon sprite — Plan 1 creates a minimal seed, expanded in later plans as needed

---

## File Structure (Plan 1 scope)

### Files to **create** (~17 files + 1 binary)

```
Portal_DREA/
├── shared/
│   ├── styles/
│   │   ├── README.md                                  NEW
│   │   ├── tokens/
│   │   │   ├── primitive.css                          NEW (~1.2 KB, Layer 1)
│   │   │   ├── semantic.css                           NEW (~2 KB, Layer 2)
│   │   │   ├── density-compact.css                    NEW (~0.3 KB)
│   │   │   └── density-comfortable.css                NEW (~0.3 KB)
│   │   └── base/
│   │       └── fonts.css                              NEW (@font-face Inter stub with placeholder)
│   │
│   └── assets/
│       ├── fonts/
│       │   ├── Inter-VariableFont.woff2               NEW (binary, ~150 KB)
│       │   ├── LICENSE-OFL.txt                        NEW (SIL OFL text)
│       │   └── README.md                              NEW
│       └── icons/
│           ├── sprite.svg                             NEW (minimal seed, ~2 KB)
│           └── README.md                              NEW
│
├── packages/
│   ├── portal-coe/
│   │   └── portal.config.json                         NEW (~0.5 KB)
│   └── portal-ssci/
│       └── portal.config.json                         NEW (~0.5 KB)
│
├── scripts/
│   └── ds_build_helpers.py                            NEW (~150 lines, shared across both build.py)
│
└── tests/
    ├── __init__.py                                    NEW (empty)
    ├── conftest.py                                    NEW (pytest shared fixtures)
    └── test_ds_build_helpers.py                       NEW (~200 lines, unit tests)
```

### Files to **modify** (4)

```
packages/portal-coe/scripts/build.py                   MODIFY (import helpers, extend build())
packages/portal-ssci/scripts/build.py                  MODIFY (same changes, parallel)
packages/portal-coe/src/Portal_COE_AWM.source.html     MODIFY (3 line-level insertions)
packages/portal-ssci/src/Portal_PSCI_AWM.source.html   MODIFY (3 line-level insertions)
```

### Files NOT touched
Nothing in `docs/`, `config/`, `VERSION`, `.gitignore`, etc.

---

## Task 0: Prerequisites — worktree and branch setup

**Files:** none (infrastructure)

- [ ] **Step 1: Verify clean working tree**

Run: `cd d:/VSCode_Claude/03-Resende/Portal_DREA && git status --short`
Expected: empty output (no uncommitted changes on main)

- [ ] **Step 2: Create feature branch via worktree**

Using the @superpowers:using-git-worktrees skill, create an isolated worktree for the design system migration. This worktree will be reused by Plans 2-5:

```bash
git worktree add ../Portal_DREA-ds feat/design-system
```

Expected: worktree created at `d:/VSCode_Claude/03-Resende/Portal_DREA-ds/` on branch `feat/design-system`

- [ ] **Step 3: Switch working directory to the worktree**

All subsequent steps in Plan 1 execute from `d:/VSCode_Claude/03-Resende/Portal_DREA-ds/`. Verify:

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA-ds && git branch --show-current
```

Expected: `feat/design-system`

- [ ] **Step 4: Verify build passes on branch baseline**

Run: `python scripts/build-all.py`
Expected: both portals build OK, exit 0. This is the pre-Plan-1 baseline — we'll compare Plan 1 output against this at the end.

- [ ] **Step 5: Capture baseline file sizes to a gitignored file**

Persist the baseline sizes to a temporary file (outside git) so Task 13 can read them automatically instead of relying on the executor to remember numbers:

```bash
python -c "
import json
from pathlib import Path
baseline = {
    'portal-coe': Path('packages/portal-coe/dist/Portal_COE_AWM.html').stat().st_size,
    'portal-ssci': Path('packages/portal-ssci/dist/Portal_PSCI_AWM.html').stat().st_size,
}
Path('.plan1-baseline.json').write_text(json.dumps(baseline, indent=2))
print(json.dumps(baseline, indent=2))
"
```

Expected output:
```json
{
  "portal-coe": 4XXXXXX,
  "portal-ssci": 1XXXXXX
}
```

Expected sizes: COE ~4.0 MB (contains embedded PDFs), SSCI ~1.5 MB. The file `.plan1-baseline.json` is placed at the repo root; add it to `.gitignore` or just leave it (it's local-only).

- [ ] **Step 6: Capture baseline screenshots (manual)**

Open both `dist/*.html` files in Chrome. Take full-page screenshots of the dashboard, a form section, and the contacts list for each portal. Save to `d:/tmp/plan1-baseline/` (outside the repo). These will be compared to the post-Plan-1 output in Task 14.

---

## Task 1: Scaffold pytest infrastructure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_ds_build_helpers.py` (stub with smoke test)

- [ ] **Step 1: Verify pytest is installed**

Run: `python -m pytest --version`
Expected: `pytest 7.x.x` or newer.
If not installed: `pip install pytest`

- [ ] **Step 2: Create `tests/__init__.py`**

Empty file. Marks `tests/` as a Python package.

```python
# Intentionally empty — marks this directory as a Python package for pytest discovery.
```

- [ ] **Step 3: Create `tests/conftest.py`**

Shared pytest fixtures — in Plan 1 only one is needed: the path to the repo root.

```python
"""Shared pytest fixtures for Portal DREA test suite."""
from pathlib import Path
import pytest


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the Portal DREA repo root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def shared_styles_root(repo_root: Path) -> Path:
    """Absolute path to shared/styles/."""
    return repo_root / "shared" / "styles"


@pytest.fixture
def shared_assets_root(repo_root: Path) -> Path:
    """Absolute path to shared/assets/."""
    return repo_root / "shared" / "assets"
```

- [ ] **Step 4: Create stub `tests/test_ds_build_helpers.py` with a smoke test**

```python
"""Unit tests for scripts/ds_build_helpers.py — helpers used by both portal build.py scripts."""


def test_pytest_infrastructure_is_working():
    """Smoke test: verifies pytest itself runs and imports from the module path work."""
    assert 1 + 1 == 2
```

- [ ] **Step 5: Run the smoke test**

Run: `python -m pytest tests/test_ds_build_helpers.py -v`
Expected: `1 passed in 0.0Xs`

- [ ] **Step 6: Commit**

```bash
git add tests/
git commit -m "test(ds): scaffold pytest infrastructure for ds build helpers

Adds tests/__init__.py, tests/conftest.py with repo_root fixtures,
and tests/test_ds_build_helpers.py with a smoke test.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 2: Create token CSS files (primitive, semantic, density)

**Files:**
- Create: `shared/styles/README.md`
- Create: `shared/styles/tokens/primitive.css`
- Create: `shared/styles/tokens/semantic.css`
- Create: `shared/styles/tokens/density-compact.css`
- Create: `shared/styles/tokens/density-comfortable.css`

- [ ] **Step 1: Create `shared/styles/README.md`**

```markdown
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
```

- [ ] **Step 2: Create `shared/styles/tokens/primitive.css`**

```css
/* =========================================================================
 * Design System SGA — Layer 1: Primitives
 * =========================================================================
 * Raw values with no semantic meaning. These are NEVER referenced directly
 * by components — only by semantic.css which gives them names.
 *
 * During the v2.1.0 migration these are prefixed --ds-* to avoid collision
 * with legacy --dark-blue, --medium-blue variables still in the portal
 * source HTMLs. The prefix is removed in Plan 5 when legacy is cleaned up.
 * ========================================================================= */

:root {
  /* ---------- Neutrals (chrome) ---------- */
  --ds-gray-50:  #f6f8fa;  /* body canvas */
  --ds-gray-100: #eef2f7;  /* hover, divider fundo */
  --ds-gray-200: #e1e5eb;  /* borders default */
  --ds-gray-300: #d1d7e0;  /* borders strong */
  --ds-gray-400: #8b95a1;  /* fg-subtle (large text only) */
  --ds-gray-500: #57606a;  /* fg-muted (secondary text) */
  --ds-gray-600: #4a5560;
  --ds-gray-700: #32383f;
  --ds-gray-800: #24292f;  /* fg-default (primary text) */
  --ds-gray-900: #0d1117;  /* nearly-black */
  --ds-white:    #ffffff;  /* surface */

  /* ---------- Brand SGA — Blues ---------- */
  --ds-blue-900: #003a5e;  /* brand-primary-hover */
  --ds-blue-800: #004C7B;  /* brand-primary (official SGA dark blue) */
  --ds-blue-700: #0073a0;  /* brand-secondary-text / focus ring */
  --ds-blue-600: #0094CF;  /* brand-secondary-fill (official SGA medium blue) */
  --ds-blue-500: #38C7F4;  /* brand-accent (official SGA light cyan) */
  --ds-blue-100: #e6f4fb;  /* info bg subtle */

  /* ---------- Greens (NEW — success, not in original SGA palette) ---------- */
  --ds-green-900: #1b5e20;
  --ds-green-800: #2e7d32;
  --ds-green-100: #e8f5e9;

  /* ---------- Ambers (warning semantic + original SGA AVSEC) ---------- */
  --ds-amber-900: #8a5a00;  /* warning fg (dark text on bg subtle) */
  --ds-amber-700: #e67e22;
  --ds-amber-500: #f39c12;  /* warning border + emphasis (official SGA amber) */
  --ds-amber-100: #fef5e7;  /* warning bg subtle */
  --ds-amber-on:  #1a1200;  /* text on amber emphasis — MUST be dark, not white */

  /* ---------- Reds (alert/emergency + AVSEC branding in new scheme) ---------- */
  --ds-red-900: #8b0000;    /* emergency border + fg */
  --ds-red-800: #b71c1c;    /* alert fg */
  --ds-red-700: #c62828;    /* alert border/emphasis + cat-avsec-bombeiros */
  --ds-red-100: #fdecea;    /* alert bg subtle */
  --ds-red-50:  #ffcdd2;    /* emergency bg subtle */

  /* ---------- Category accents ---------- */
  --ds-brown-700:  #5d4037;  /* cat-seg-ordem */
  --ds-purple-800: #6a1b9a;  /* cat-externa-emg */
  --ds-slate-600:  #455a64;  /* cat-operadores */

  /* ---------- Shadows (light-theme-appropriate, cribbed from Atlassian/Primer) ---------- */
  --ds-shadow-1: 0 1px 2px rgba(9,30,66,0.08);
  --ds-shadow-2: 0 2px 8px rgba(9,30,66,0.12);
  --ds-shadow-3: 0 8px 24px rgba(9,30,66,0.15);
  --ds-shadow-4: 0 24px 48px rgba(9,30,66,0.20);

  /* ---------- Border radii ---------- */
  --ds-radius-sm:   3px;
  --ds-radius-md:   6px;
  --ds-radius-lg:   8px;
  --ds-radius-pill: 9999px;

  /* ---------- Motion ---------- */
  --ds-transition-fast: 120ms cubic-bezier(.2, 0, 0, 1);
  --ds-transition-base: 200ms cubic-bezier(.2, 0, 0, 1);
  --ds-transition-slow: 320ms cubic-bezier(.2, 0, 0, 1);

  /* ---------- Type scale (Major Third 1.250) ---------- */
  --ds-text-xs:    11px;
  --ds-text-sm:    13px;
  /* --ds-text-base is overridden by density files (14px compact, 16px comfortable) */
  --ds-text-md:    16px;
  --ds-text-lg:    20px;
  --ds-text-xl:    25px;
  --ds-text-2xl:   31px;
  --ds-text-3xl:   39px;

  --ds-line-xs:    15px;
  --ds-line-sm:    18px;
  --ds-line-md:    24px;
  --ds-line-lg:    26px;
  --ds-line-xl:    30px;
  --ds-line-2xl:   38px;
  --ds-line-3xl:   46px;

  /* ---------- Focus ring ---------- */
  --ds-focus-ring-width:  2px;
  --ds-focus-ring-offset: 2px;
}
```

- [ ] **Step 3: Create `shared/styles/tokens/semantic.css`**

```css
/* =========================================================================
 * Design System SGA — Layer 2: Semantic tokens
 * =========================================================================
 * Meaningful aliases over primitives. These are the ONLY tokens that
 * components should reference. Primitives are opaque.
 * ========================================================================= */

:root {
  /* ---------- Neutrals / chrome ---------- */
  --ds-neutral-canvas:    var(--ds-gray-50);
  --ds-neutral-surface:   var(--ds-white);
  --ds-neutral-subtle:    var(--ds-gray-100);
  --ds-neutral-muted:     var(--ds-gray-200);
  --ds-neutral-strong:    var(--ds-gray-300);
  --ds-neutral-fg:        var(--ds-gray-800);
  --ds-neutral-fg-muted:  var(--ds-gray-500);
  --ds-neutral-fg-subtle: var(--ds-gray-400);

  /* ---------- Brand SGA ---------- */
  --ds-brand-primary:        var(--ds-blue-800);  /* 9.1:1 AAA */
  --ds-brand-primary-hover:  var(--ds-blue-900);  /* 11.8:1 AAA */
  --ds-brand-secondary-fill: var(--ds-blue-600);  /* 3.5:1 — FILL ONLY, never text */
  --ds-brand-secondary-text: var(--ds-blue-700);  /* 4.9:1 AA — safe as text */
  --ds-brand-accent:         var(--ds-blue-500);

  /* ---------- Status — info ---------- */
  --ds-status-info-bg:            var(--ds-blue-100);
  --ds-status-info-border:        var(--ds-blue-700);
  --ds-status-info-fg:            var(--ds-blue-900);  /* 11.2:1 AAA */
  --ds-status-info-emphasis:      var(--ds-blue-700);
  --ds-status-info-on-emphasis:   var(--ds-white);

  /* ---------- Status — success ---------- */
  --ds-status-success-bg:          var(--ds-green-100);
  --ds-status-success-border:      var(--ds-green-800);
  --ds-status-success-fg:          var(--ds-green-900);  /* 9.7:1 AAA */
  --ds-status-success-emphasis:    var(--ds-green-800);
  --ds-status-success-on-emphasis: var(--ds-white);

  /* ---------- Status — warning ---------- */
  --ds-status-warning-bg:          var(--ds-amber-100);
  --ds-status-warning-border:      var(--ds-amber-500);
  --ds-status-warning-fg:          var(--ds-amber-900);  /* 6.3:1 AA */
  --ds-status-warning-emphasis:    var(--ds-amber-500);
  --ds-status-warning-on-emphasis: var(--ds-amber-on);   /* #1a1200 — MUST be dark */

  /* ---------- Status — alert ---------- */
  --ds-status-alert-bg:            var(--ds-red-100);
  --ds-status-alert-border:        var(--ds-red-700);
  --ds-status-alert-fg:            var(--ds-red-800);    /* 6.8:1 AA */
  --ds-status-alert-emphasis:      var(--ds-red-700);
  --ds-status-alert-on-emphasis:   var(--ds-white);

  /* ---------- Status — emergency ---------- */
  --ds-status-emergency-bg:          var(--ds-red-50);
  --ds-status-emergency-border:      var(--ds-red-900);
  --ds-status-emergency-fg:          var(--ds-red-900);  /* 9.3:1 AAA */
  --ds-status-emergency-emphasis:    var(--ds-red-900);
  --ds-status-emergency-on-emphasis: var(--ds-white);

  /* ---------- Category — branding of contact taxonomy ---------- */
  --ds-cat-avsec-bombeiros: var(--ds-red-700);
  --ds-cat-sga-interna:     var(--ds-blue-800);
  --ds-cat-enna-navegacao:  var(--ds-blue-600);
  --ds-cat-seg-ordem:       var(--ds-brown-700);
  --ds-cat-externa-emg:     var(--ds-purple-800);
  --ds-cat-operadores:      var(--ds-slate-600);

  /* ---------- Elevation aliases ---------- */
  --ds-elevation-card:    var(--ds-shadow-1);
  --ds-elevation-hover:   var(--ds-shadow-2);
  --ds-elevation-overlay: var(--ds-shadow-3);
  --ds-elevation-modal:   var(--ds-shadow-4);

  /* ---------- Focus ring ---------- */
  --ds-focus-ring-color: var(--ds-blue-700);
}
```

- [ ] **Step 4: Create `shared/styles/tokens/density-compact.css`**

```css
/* =========================================================================
 * Density — Compact (COE default, futuros SOA e AVSEC)
 * =========================================================================
 * Scoped to :root[data-density="compact"] so only portals with
 * data-density="compact" on <html> pick up these values.
 * ========================================================================= */

:root[data-density="compact"] {
  --ds-space-1: 2px;
  --ds-space-2: 4px;
  --ds-space-3: 6px;
  --ds-space-4: 8px;    /* default stack gap */
  --ds-space-5: 12px;
  --ds-space-6: 16px;   /* card padding */
  --ds-space-7: 24px;
  --ds-space-8: 32px;

  --ds-row-height:      32px;  /* table row */
  --ds-input-height:    32px;  /* form input */
  --ds-nav-item-height: 36px;  /* sidebar nav item */

  --ds-text-base: 14px;
  --ds-line-base: 21px;
}
```

- [ ] **Step 5: Create `shared/styles/tokens/density-comfortable.css`**

```css
/* =========================================================================
 * Density — Comfortable (SSCI default, futuro DIRECÇÃO)
 * =========================================================================
 * Scoped to :root[data-density="comfortable"].
 * ========================================================================= */

:root[data-density="comfortable"] {
  --ds-space-1: 4px;
  --ds-space-2: 6px;
  --ds-space-3: 8px;
  --ds-space-4: 12px;   /* default stack gap */
  --ds-space-5: 16px;
  --ds-space-6: 24px;   /* card padding */
  --ds-space-7: 32px;
  --ds-space-8: 48px;

  --ds-row-height:      40px;
  --ds-input-height:    40px;
  --ds-nav-item-height: 44px;

  --ds-text-base: 16px;
  --ds-line-base: 24px;
}
```

- [ ] **Step 6: Verify CSS files are syntactically valid**

Open each file in VS Code and check there are no red squiggles. Alternatively, run a quick syntax check:

```bash
python -c "
from pathlib import Path
for p in Path('shared/styles/tokens').glob('*.css'):
    content = p.read_text(encoding='utf-8')
    # Basic sanity: balanced braces
    assert content.count('{') == content.count('}'), f'{p}: unbalanced braces'
    print(f'OK: {p} ({len(content)} bytes)')
"
```

Expected: four `OK:` lines, no assertion errors.

- [ ] **Step 7: Commit**

```bash
git add shared/styles/
git commit -m "feat(ds): create token layer (primitive, semantic, density)

Layer 1 primitives in shared/styles/tokens/primitive.css — raw values
for neutrals, SGA blues, greens, ambers, reds, category accents,
shadows, radii, motion, type scale. All prefixed --ds-* during migration.

Layer 2 semantics in shared/styles/tokens/semantic.css — meaningful
aliases that components will consume. Includes the 5-level status
scale (info/success/warning/alert/emergency) with bg/border/fg/
emphasis/on-emphasis tokens, category branding, elevation aliases,
and focus ring.

Density scoping in density-{compact,comfortable}.css via
:root[data-density=X] attribute selector. Activated per portal at
build time via portal.config.json.

Governance documented in shared/styles/README.md. Tokens are
currently dormant — nothing consumes them yet.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 3: Scaffold `ds_build_helpers.py` and TDD `load_portal_config`

**Files:**
- Create: `scripts/ds_build_helpers.py`
- Modify: `tests/test_ds_build_helpers.py` (add import and new tests)

- [ ] **Step 1: Create empty helper module**

```python
# scripts/ds_build_helpers.py
"""
Design System SGA — build helper functions.

Shared by both packages/portal-coe/scripts/build.py and
packages/portal-ssci/scripts/build.py. Exposes:

- load_portal_config(path)        → dict
- resolve_density(airport, portal_config, default="compact") → str
- compile_design_system_css(styles_root, density) → str
- encode_font_woff2_base64(woff2_path) → str

Import with:
    import sys
    from pathlib import Path
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import ds_build_helpers as dsh
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
```

- [ ] **Step 2: Write failing test for `load_portal_config`**

Add to `tests/test_ds_build_helpers.py`:

```python
import sys
from pathlib import Path

# Make scripts/ importable for tests
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import ds_build_helpers as dsh  # noqa: E402


def test_pytest_infrastructure_is_working():
    """Smoke test: verifies pytest itself runs and imports from the module path work."""
    assert 1 + 1 == 2


class TestLoadPortalConfig:
    def test_loads_valid_json_file(self, tmp_path: Path):
        config_file = tmp_path / "portal.config.json"
        config_file.write_text(
            '{"id": "portal-test", "name": "Portal Test", "density": "compact"}',
            encoding="utf-8",
        )

        result = dsh.load_portal_config(config_file)

        assert result["id"] == "portal-test"
        assert result["name"] == "Portal Test"
        assert result["density"] == "compact"

    def test_raises_on_missing_file(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.json"
        import pytest
        with pytest.raises(FileNotFoundError):
            dsh.load_portal_config(missing)
```

- [ ] **Step 3: Run tests — verify failure**

Run: `python -m pytest tests/test_ds_build_helpers.py -v`
Expected: `TestLoadPortalConfig::test_loads_valid_json_file FAILED` with `AttributeError: module 'ds_build_helpers' has no attribute 'load_portal_config'`

- [ ] **Step 4: Implement `load_portal_config`**

Add to `scripts/ds_build_helpers.py`:

```python
def load_portal_config(path: Path) -> dict:
    """
    Load a packages/portal-XXX/portal.config.json file.

    Returns the parsed JSON as a dict. Raises FileNotFoundError if missing,
    json.JSONDecodeError if malformed.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))
```

- [ ] **Step 5: Run tests — verify pass**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestLoadPortalConfig -v`
Expected: both tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py
git commit -m "feat(ds): add load_portal_config helper with tests

First helper in scripts/ds_build_helpers.py — reads a
portal.config.json file and returns the parsed dict.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 4: TDD `resolve_density` helper

**Files:**
- Modify: `scripts/ds_build_helpers.py` (add function)
- Modify: `tests/test_ds_build_helpers.py` (add test class)

- [ ] **Step 1: Write failing tests for `resolve_density`**

Add to `tests/test_ds_build_helpers.py`:

```python
class TestResolveDensity:
    def test_airport_override_wins_over_portal_config(self):
        airport = {
            "airport": {"name": "Test"},
            "portals": {"portal-coe": {"density": "comfortable"}},
        }
        portal_config = {"id": "portal-coe", "density": "compact"}

        assert dsh.resolve_density(airport, portal_config) == "comfortable"

    def test_portal_config_wins_when_no_airport_override(self):
        airport = {"airport": {"name": "Test"}}
        portal_config = {"id": "portal-coe", "density": "compact"}

        assert dsh.resolve_density(airport, portal_config) == "compact"

    def test_default_when_neither_specifies(self):
        airport = {"airport": {"name": "Test"}}
        portal_config = {"id": "portal-coe"}

        assert dsh.resolve_density(airport, portal_config) == "compact"

    def test_custom_default_respected(self):
        airport = {}
        portal_config = {"id": "portal-ssci"}

        assert dsh.resolve_density(airport, portal_config, default="comfortable") == "comfortable"

    def test_airport_override_for_different_portal_ignored(self):
        airport = {
            "portals": {"portal-ssci": {"density": "comfortable"}},  # override for SSCI only
        }
        portal_config = {"id": "portal-coe", "density": "compact"}

        # Building portal-coe, so SSCI override does not apply
        assert dsh.resolve_density(airport, portal_config) == "compact"
```

- [ ] **Step 2: Run tests — verify failure**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestResolveDensity -v`
Expected: all 5 tests fail with `AttributeError: module 'ds_build_helpers' has no attribute 'resolve_density'`

- [ ] **Step 3: Implement `resolve_density`**

Add to `scripts/ds_build_helpers.py`:

```python
def resolve_density(
    airport: dict,
    portal_config: dict,
    default: str = "compact",
) -> str:
    """
    Resolve the density mode for a portal build.

    Resolution order (first wins):
      1. airport.portals[portal_id].density  — per-airport per-portal override
      2. portal_config.density               — portal default
      3. default parameter                   — fallback (defaults to "compact")

    Returns one of "compact" | "comfortable".
    """
    portal_id = portal_config.get("id", "")

    # Step 1: airport override
    airport_portals = airport.get("portals", {}) or {}
    override = airport_portals.get(portal_id, {}) or {}
    if "density" in override:
        return override["density"]

    # Step 2: portal default
    if "density" in portal_config:
        return portal_config["density"]

    # Step 3: fallback
    return default
```

- [ ] **Step 4: Run tests — verify pass**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestResolveDensity -v`
Expected: all 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py
git commit -m "feat(ds): add resolve_density helper with tests

Implements the airport-override → portal-default → fallback
resolution chain documented in the spec (Section 6.3). Allows
an airport config to override per-portal density if a specific
airport (e.g., VIP Luanda) wants COE to be comfortable instead
of the default compact.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 5: TDD `compile_design_system_css` helper

**Files:**
- Modify: `scripts/ds_build_helpers.py`
- Modify: `tests/test_ds_build_helpers.py`

- [ ] **Step 1: Write failing tests for `compile_design_system_css`**

Add to `tests/test_ds_build_helpers.py`:

```python
class TestCompileDesignSystemCss:
    def _setup_fake_styles(self, root: Path) -> None:
        """Build a minimal shared/styles/ tree for tests."""
        (root / "tokens").mkdir(parents=True)
        (root / "tokens" / "primitive.css").write_text(
            "/* primitive */\n:root { --a: 1; }\n", encoding="utf-8"
        )
        (root / "tokens" / "semantic.css").write_text(
            "/* semantic */\n:root { --b: var(--a); }\n", encoding="utf-8"
        )
        (root / "tokens" / "density-compact.css").write_text(
            "/* compact */\n:root[data-density='compact'] { --c: 1; }\n", encoding="utf-8"
        )
        (root / "tokens" / "density-comfortable.css").write_text(
            "/* comfortable */\n:root[data-density='comfortable'] { --c: 2; }\n", encoding="utf-8"
        )
        (root / "base").mkdir()
        (root / "base" / "fonts.css").write_text(
            "/* fonts */\n@font-face { font-family: 'Test'; }\n", encoding="utf-8"
        )

    def test_concatenates_tokens_in_cascade_order(self, tmp_path: Path):
        self._setup_fake_styles(tmp_path)

        result = dsh.compile_design_system_css(tmp_path, density="compact")

        # All expected content present
        assert "/* primitive */" in result
        assert "/* semantic */" in result
        assert "/* compact */" in result
        assert "/* fonts */" in result

        # Order: primitive → semantic → density → fonts
        assert result.index("/* primitive */") < result.index("/* semantic */")
        assert result.index("/* semantic */") < result.index("/* compact */")
        assert result.index("/* compact */") < result.index("/* fonts */")

    def test_compact_excludes_comfortable_tokens(self, tmp_path: Path):
        self._setup_fake_styles(tmp_path)

        result = dsh.compile_design_system_css(tmp_path, density="compact")

        assert "/* compact */" in result
        assert "/* comfortable */" not in result
        assert "--c: 1" in result
        assert "--c: 2" not in result

    def test_comfortable_excludes_compact_tokens(self, tmp_path: Path):
        self._setup_fake_styles(tmp_path)

        result = dsh.compile_design_system_css(tmp_path, density="comfortable")

        assert "/* comfortable */" in result
        assert "/* compact */" not in result

    def test_raises_on_invalid_density(self, tmp_path: Path):
        self._setup_fake_styles(tmp_path)
        import pytest

        with pytest.raises(ValueError, match="density"):
            dsh.compile_design_system_css(tmp_path, density="medium")

    def test_raises_when_primitive_css_missing(self, tmp_path: Path):
        (tmp_path / "tokens").mkdir()
        # Do not create primitive.css
        import pytest

        with pytest.raises(FileNotFoundError):
            dsh.compile_design_system_css(tmp_path, density="compact")

    def test_handles_missing_base_fonts_css_gracefully_in_phase_1(self, tmp_path: Path):
        """Phase 1 may or may not have base/fonts.css at first — compile must not
        crash if it is missing (fonts are optional during dormant phase)."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "base" / "fonts.css").unlink()

        # Should not raise; result omits the fonts section
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* fonts */" not in result
        assert "/* primitive */" in result  # tokens still present
```

- [ ] **Step 2: Run tests — verify failure**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestCompileDesignSystemCss -v`
Expected: all tests fail with `AttributeError: module 'ds_build_helpers' has no attribute 'compile_design_system_css'`

- [ ] **Step 3: Implement `compile_design_system_css`**

Add to `scripts/ds_build_helpers.py`:

```python
_VALID_DENSITIES = ("compact", "comfortable")


def compile_design_system_css(styles_root: Path, density: str) -> str:
    """
    Read the Design System CSS files under `styles_root` and concatenate them
    in the deterministic cascade order defined in the spec (Section 6.2).

    Current cascade (Plan 1 — Foundation Dormant):
      1. tokens/primitive.css     (required)
      2. tokens/semantic.css      (required)
      3. tokens/density-<X>.css   (required, where X = density param)
      4. base/fonts.css           (optional — OK if missing during Plan 1)

    Plans 2-3 will extend this by adding base/reset.css, base/typography.css,
    base/global.css, chrome/*.css, components/*.css, print/print.css.

    Args:
        styles_root: absolute Path to shared/styles/
        density: "compact" or "comfortable"

    Returns:
        A single string containing the concatenated CSS. Files are separated
        by a blank line and a banner comment indicating the source file.

    Raises:
        ValueError: if density is not "compact" or "comfortable"
        FileNotFoundError: if any required file is missing
    """
    if density not in _VALID_DENSITIES:
        raise ValueError(
            f"Invalid density {density!r}; must be one of {_VALID_DENSITIES}"
        )

    styles_root = Path(styles_root)

    # Build the ordered list of files to concatenate.
    # Required files come first; optional files are skipped if missing.
    required_files = [
        styles_root / "tokens" / "primitive.css",
        styles_root / "tokens" / "semantic.css",
        styles_root / "tokens" / f"density-{density}.css",
    ]
    optional_files = [
        styles_root / "base" / "fonts.css",
    ]

    # Verify all required files exist up-front
    for f in required_files:
        if not f.exists():
            raise FileNotFoundError(f"Required DS CSS file not found: {f}")

    pieces: list[str] = []
    for f in required_files + optional_files:
        if not f.exists():
            continue  # optional file, skip
        rel_path = f.relative_to(styles_root.parent).as_posix()
        banner = f"/* ---------- {rel_path} ---------- */"
        pieces.append(banner)
        pieces.append(f.read_text(encoding="utf-8").rstrip())
        pieces.append("")  # blank line separator

    return "\n".join(pieces)
```

- [ ] **Step 4: Run tests — verify pass**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestCompileDesignSystemCss -v`
Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py
git commit -m "feat(ds): add compile_design_system_css helper with tests

Reads shared/styles/ files in deterministic cascade order
(primitive → semantic → density → base/fonts) and concatenates
them into a single CSS string ready for {{DS_CSS}} substitution.

Plan 1 handles: tokens/*.css (required) + base/fonts.css (optional).
Plans 2-3 will extend this to include base/reset/typography/global,
chrome/*, components/*, and print/print.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 6: TDD `encode_font_woff2_base64` helper

**Files:**
- Modify: `scripts/ds_build_helpers.py`
- Modify: `tests/test_ds_build_helpers.py`

- [ ] **Step 1: Write failing tests for `encode_font_woff2_base64`**

Add to `tests/test_ds_build_helpers.py`:

```python
class TestEncodeFontWoff2Base64:
    def test_encodes_bytes_to_base64_string(self, tmp_path: Path):
        woff2 = tmp_path / "Test.woff2"
        woff2.write_bytes(b"fake-woff2-content")

        result = dsh.encode_font_woff2_base64(woff2)

        import base64 as b64
        expected = b64.b64encode(b"fake-woff2-content").decode("ascii")
        assert result == expected

    def test_empty_file_returns_empty_string(self, tmp_path: Path):
        woff2 = tmp_path / "Empty.woff2"
        woff2.write_bytes(b"")

        result = dsh.encode_font_woff2_base64(woff2)

        assert result == ""

    def test_raises_on_missing_file(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.woff2"
        import pytest
        with pytest.raises(FileNotFoundError):
            dsh.encode_font_woff2_base64(missing)
```

- [ ] **Step 2: Run tests — verify failure**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestEncodeFontWoff2Base64 -v`
Expected: all fail with `AttributeError`.

- [ ] **Step 3: Implement `encode_font_woff2_base64`**

Add to `scripts/ds_build_helpers.py`:

```python
def encode_font_woff2_base64(woff2_path: Path) -> str:
    """
    Read a .woff2 font file and return its base64-encoded content as an ASCII
    string suitable for embedding in a CSS `src: url('data:font/woff2;base64,...')`
    rule.

    Args:
        woff2_path: absolute Path to the .woff2 file

    Returns:
        base64-encoded ASCII string (no data: prefix, no line wraps)

    Raises:
        FileNotFoundError: if the file does not exist
    """
    data = Path(woff2_path).read_bytes()
    return base64.b64encode(data).decode("ascii")
```

- [ ] **Step 4: Run tests — verify pass**

Run: `python -m pytest tests/test_ds_build_helpers.py::TestEncodeFontWoff2Base64 -v`
Expected: all 3 tests pass.

- [ ] **Step 5: Run the full test suite**

Run: `python -m pytest tests/ -v`
Expected: all tests from Tasks 1-6 pass (~15 tests total).

- [ ] **Step 6: Commit**

```bash
git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py
git commit -m "feat(ds): add encode_font_woff2_base64 helper with tests

Reads a .woff2 file and returns its base64-encoded content as
an ASCII string for embedding in a CSS @font-face src: url()
data URI. Used by the build pipeline to resolve the
{{DS_INTER_WOFF2_BASE64}} placeholder.

All helpers in scripts/ds_build_helpers.py now complete for Plan 1:
- load_portal_config
- resolve_density
- compile_design_system_css
- encode_font_woff2_base64

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 7: Download Inter Variable font + create base/fonts.css

**Files:**
- Create: `shared/assets/fonts/Inter-VariableFont.woff2` (binary)
- Create: `shared/assets/fonts/LICENSE-OFL.txt`
- Create: `shared/assets/fonts/README.md`
- Create: `shared/styles/base/fonts.css`

- [ ] **Step 1: Fetch Inter Variable woff2**

Inter Variable is published by Rasmus Andersson (rsms) under the SIL Open Font License. Official sources (try in order until one succeeds):

1. **Latest release zip** — https://github.com/rsms/inter/releases/latest
   - Download `Inter-X.Y.zip`, extract `Inter/extras/woff2/InterVariable.woff2` (or the closest name)
2. **Direct raw** (may lag behind releases) — https://github.com/rsms/inter/raw/master/docs/font-files/InterVariable.woff2
3. **rsms.me bundle** — https://rsms.me/inter/inter.zip

Save the final file to: `shared/assets/fonts/Inter-VariableFont.woff2`

**Manual step** — run in a shell with internet access (adjust to your OS):

```bash
cd shared/assets/fonts
# Option A: direct raw download (fastest if it works)
curl -L -o Inter-VariableFont.woff2 \
  "https://github.com/rsms/inter/raw/master/docs/font-files/InterVariable.woff2"

# Option B: if A fails, download the latest release zip manually from
# https://github.com/rsms/inter/releases/latest in a browser, unzip,
# and copy the InterVariable.woff2 file to this directory renamed to
# Inter-VariableFont.woff2
```

Verify file size:
```bash
ls -l Inter-VariableFont.woff2
```

Expected: approximately **150-350 KB** (depends on Inter version; anywhere in that range is OK — newer versions may be larger due to more glyphs).

**If download fails** (no internet, firewall, corporate proxy): STOP and consult the user. They may need to download manually via browser and drop the file in place. Do NOT fabricate or generate a fake woff2 file — the build pipeline needs the real binary for base64 encoding to produce valid `data: url(...)` rules.

- [ ] **Step 2: Add SIL OFL license text**

Create `shared/assets/fonts/LICENSE-OFL.txt` with the full SIL OFL 1.1 license text. Fetch from: https://openfontlicense.org/ or copy from the Inter repo: https://github.com/rsms/inter/blob/master/LICENSE.txt

**Required content** (the full SIL OFL 1.1 text, ~4 KB). Do not abbreviate or edit. If the executor cannot fetch, they should ask the user to paste the text.

- [ ] **Step 3: Create `shared/assets/fonts/README.md`**

```markdown
# shared/assets/fonts/

## Inter Variable Font

**File:** `Inter-VariableFont.woff2`
**Version:** (record the version downloaded — check Inter's releases)
**Source:** https://github.com/rsms/inter
**License:** SIL Open Font License 1.1 — see `LICENSE-OFL.txt`

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
5. Update the "Version" field in this README
6. Commit with a message like `chore(ds): update Inter Variable to vX.Y.Z`

## Why not use a CDN?

Portal DREA is distributed as a single self-contained HTML file that must work
offline in airport operations rooms. CDNs may be blocked by airport firewalls,
may be unavailable during incidents, and introduce external trust. Embedding the
font as base64 inside the HTML adds ~200 KB per portal but eliminates all
runtime network dependencies.
```

- [ ] **Step 4: Create `shared/styles/base/fonts.css`**

```css
/* =========================================================================
 * Design System SGA — Base: Fonts
 * =========================================================================
 * Inter Variable font declared via @font-face with the woff2 data embedded
 * as base64. The {{DS_INTER_WOFF2_BASE64}} placeholder is resolved at build
 * time by scripts/ds_build_helpers.py::encode_font_woff2_base64() via the
 * normal substitute_placeholders pipeline.
 *
 * NOTE (Plan 1 — Dormant): this declaration makes the Inter font AVAILABLE
 * to the browser, but nothing applies it yet. Legacy CSS in the portal
 * sources still declares `font-family: 'Segoe UI', ...` so the visible text
 * remains unchanged. Plan 2 will introduce `body { font-family: 'Inter',
 * system-ui, ...; }` once the typography.css is activated.
 *
 * Inter Variable is a single variable font file covering weights 100-900.
 * Glyph caching note: font-display: swap means legacy fallback text renders
 * first, then re-renders with Inter once loaded — but since nothing uses
 * Inter in Plan 1, there is no perceptible swap.
 * ========================================================================= */

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url('data:font/woff2;base64,{{DS_INTER_WOFF2_BASE64}}') format('woff2-variations'),
       url('data:font/woff2;base64,{{DS_INTER_WOFF2_BASE64}}') format('woff2');
  font-named-instance: 'Regular';
}
```

- [ ] **Step 5: Verify files are in place**

Run:
```bash
ls -la shared/assets/fonts/ shared/styles/base/
```

Expected:
- `shared/assets/fonts/Inter-VariableFont.woff2` (binary, ~150-350 KB)
- `shared/assets/fonts/LICENSE-OFL.txt` (text, ~4 KB)
- `shared/assets/fonts/README.md` (text, ~1.5 KB)
- `shared/styles/base/fonts.css` (text, ~1.3 KB)

- [ ] **Step 6: Commit**

```bash
git add shared/assets/fonts/ shared/styles/base/
git commit -m "feat(ds): add Inter Variable font and base/fonts.css

Adds the Inter Variable woff2 font (SIL OFL 1.1, from rsms/inter)
to shared/assets/fonts/ and creates shared/styles/base/fonts.css
with an @font-face rule that uses a {{DS_INTER_WOFF2_BASE64}}
placeholder. At build time, ds_build_helpers.encode_font_woff2_base64
encodes the woff2 file and substitute_placeholders replaces the
placeholder with the base64 data URI.

License (LICENSE-OFL.txt) and README.md document provenance and
the rationale for embedding instead of using a CDN (offline/air-gap
requirements).

Font is DORMANT in Plan 1 — loaded by the browser but not applied
to any element. Nothing visible changes. Plan 2 will activate it
by introducing typography.css.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 8: Create minimal sprite.svg + icons README

**Files:**
- Create: `shared/assets/icons/sprite.svg`
- Create: `shared/assets/icons/README.md`

- [ ] **Step 1: Create minimal `shared/assets/icons/sprite.svg`**

For Plan 1 the sprite only needs to **exist** and be inlined into the HTML. Nothing references its symbols yet. We seed it with 3 icons that will be useful in Plans 2-3: a placeholder SGA mark, a menu icon, and a close icon. Content based on Heroicons Outline (MIT license).

```svg
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
  <!--
    Design System SGA — Icon Sprite
    ==============================
    Icons are referenced as <svg><use href="#icon-NAME"/></svg>.
    All icons use viewBox="0 0 24 24" and stroke="currentColor" so colour
    is inherited from the CSS context.

    Base: Heroicons Outline v2 (MIT License)
    https://heroicons.com/
    Copyright (c) Refactoring UI Inc.

    Plan 1 seeds this sprite with 3 icons to validate the pipeline.
    Plan 2 will expand it to ~20 icons. Plan 3 may add domain icons.
  -->

  <symbol id="icon-sga-mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <!-- Placeholder mark — a stylised "chevron-up" until the real SGA SVG is extracted in Plan 3 -->
    <title>SGA</title>
    <path d="M12 3 L4 15 L20 15 Z" />
    <path d="M8 20 L16 20" />
  </symbol>

  <symbol id="icon-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <title>Menu</title>
    <path d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
  </symbol>

  <symbol id="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <title>Fechar</title>
    <path d="M6 18 18 6M6 6l12 12" />
  </symbol>
</svg>
```

- [ ] **Step 2: Create `shared/assets/icons/README.md`**

```markdown
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
```

- [ ] **Step 3: Verify SVG is well-formed**

Run:
```bash
python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('shared/assets/icons/sprite.svg')
root = tree.getroot()
symbols = root.findall('.//{http://www.w3.org/2000/svg}symbol')
print(f'OK — {len(symbols)} symbols found')
for s in symbols:
    print(f'  - {s.get(\"id\")}')
"
```

Expected output:
```
OK — 3 symbols found
  - icon-sga-mark
  - icon-menu
  - icon-close
```

- [ ] **Step 4: Commit**

```bash
git add shared/assets/icons/
git commit -m "feat(ds): seed SVG icon sprite with 3 placeholder icons

Minimal sprite.svg containing icon-sga-mark, icon-menu, icon-close.
Uses Heroicons Outline conventions (viewBox 0 0 24 24, currentColor).
The sprite is injected at build time as the first child of <body>,
hidden with display:none + aria-hidden=true. Nothing references
these symbols yet in Plan 1 — they are dormant until Plan 2.

README.md documents conventions, base licence (MIT Heroicons), and
the rationale for inline sprite over icon fonts or CDNs.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 9: Create `portal.config.json` for both portals

**Files:**
- Create: `packages/portal-coe/portal.config.json`
- Create: `packages/portal-ssci/portal.config.json`

- [ ] **Step 1: Create `packages/portal-coe/portal.config.json`**

```json
{
  "_meta": {
    "comment": "Portal-level configuration for Portal COE. Per-portal identity, density, and feature flags. Read by build.py and injected via {{PORTAL.*}} placeholders. Overridable per-airport in config/airport-XXX.json under portals.portal-coe.",
    "schema_version": "1.0",
    "last_updated": "2026-04-11"
  },
  "id": "portal-coe",
  "name": "Portal COE",
  "name_short": "COE",
  "tagline": "Centro de Operações de Emergência",
  "role": "Coordenador do Centro de Operações de Emergência",
  "density": "compact",
  "ui": {
    "show_utc_clock": true,
    "show_emergency_stopwatch": true,
    "show_occurrence_pill": true
  }
}
```

- [ ] **Step 2: Create `packages/portal-ssci/portal.config.json`**

```json
{
  "_meta": {
    "comment": "Portal-level configuration for Portal SSCI. Per-portal identity, density, and feature flags. Read by build.py and injected via {{PORTAL.*}} placeholders.",
    "schema_version": "1.0",
    "last_updated": "2026-04-11"
  },
  "id": "portal-ssci",
  "name": "Portal SSCI",
  "name_short": "SSCI",
  "tagline": "Serviço de Salvamento e Combate a Incêndios",
  "role": "Chefe SSCI / Bombeiros",
  "density": "comfortable",
  "ui": {
    "show_utc_clock": true,
    "show_emergency_stopwatch": false,
    "show_occurrence_pill": false
  }
}
```

- [ ] **Step 3: Validate both JSON files parse correctly**

Run:
```bash
python -c "
import json
from pathlib import Path
for p in ['packages/portal-coe/portal.config.json', 'packages/portal-ssci/portal.config.json']:
    data = json.loads(Path(p).read_text(encoding='utf-8'))
    print(f'{p}: id={data[\"id\"]} density={data[\"density\"]}')
"
```

Expected:
```
packages/portal-coe/portal.config.json: id=portal-coe density=compact
packages/portal-ssci/portal.config.json: id=portal-ssci density=comfortable
```

- [ ] **Step 4: Commit**

```bash
git add packages/portal-coe/portal.config.json packages/portal-ssci/portal.config.json
git commit -m "feat(ds): add portal.config.json for COE and SSCI

Introduces per-portal configuration files separate from per-airport
config/airport-XXX.json. Each portal.config.json declares id, name,
name_short, tagline, role, density, and ui feature flags.

Density resolution per spec Section 6.3:
  airport override → portal.config.json → default 'compact'

COE = compact (mission control density)
SSCI = comfortable (document-oriented density)

Read by build.py via dsh.load_portal_config() and injected into the
source HTML as {{PORTAL.*}} placeholders via the existing
_flatten_dict mechanism.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 10: Update `packages/portal-coe/scripts/build.py` to consume new inputs

**Files:**
- Modify: `packages/portal-coe/scripts/build.py`

- [ ] **Step 1: Read the current build.py around the build() function**

Run: `python -c "print(open('packages/portal-coe/scripts/build.py').read())" | head -260 | tail -50`

Familiarise yourself with the existing `build()` signature (`source_path, config_path, output_path, validate`) and the `substitute_placeholders` call within it. Do NOT change the signature.

- [ ] **Step 2: Add `sys.path` manipulation and helper import at top of file**

Near the top of `packages/portal-coe/scripts/build.py`, after the existing imports block, add:

```python
# --- Design System helpers (Plan 1: Foundation Dormant) -------------------
# Import ds_build_helpers from scripts/ at the repo root. This is shared
# between portal-coe and portal-ssci builds.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import ds_build_helpers as dsh  # noqa: E402
```

This must appear AFTER `REPO_ROOT` is defined (around line 70-80 in current file).

- [ ] **Step 3: Extend `build()` function to compile DS payload**

**Real code context** — the existing `build()` in `packages/portal-coe/scripts/build.py` (around lines 234-302) uses these variable names, which this plan matches exactly:

- `source_html` — the raw HTML content (line 262)
- `config` — the parsed airport config dict (line 267)
- `context` — the substitution context dict (line 270)
- `output_html` — after `substitute_placeholders` (line 278)
- `build_date` — the datetime object (line 248), already formatted in `context["build_date"]` as ISO string

The DS payload preparation happens **between** reading `source_html` (line 262) and reading `config` (line 267), or equivalently between reading `config` and building `context`. Insert the following block **between the existing sections 2 and 3** (after `config = read_config(config_path)` on line 267, before `context = { ... }` on line 270):

```python
    # === Plan 1: Design System Foundation — dormant payload ==============
    # (1) Load the portal-level config (new in v2.1)
    portal_config_path = PACKAGE_ROOT / "portal.config.json"
    if not portal_config_path.exists():
        print(f"  [error] portal.config.json não encontrado em {portal_config_path}")
        return 1
    portal_config = dsh.load_portal_config(portal_config_path)

    # (2) Resolve density (airport override → portal default → fallback)
    density = dsh.resolve_density(config, portal_config, default="compact")
    print(f"  [ds] portal={portal_config['id']} density={density}")

    # (3) Compile the Design System CSS (tokens + base/fonts)
    shared_styles_root = SHARED_DIR / "styles"
    ds_css = dsh.compile_design_system_css(shared_styles_root, density=density)
    print(f"  [ds] compiled ds_css ({len(ds_css):,} chars)")

    # (4) Encode the Inter Variable font as base64
    inter_woff2_path = SHARED_DIR / "assets" / "fonts" / "Inter-VariableFont.woff2"
    if inter_woff2_path.exists():
        ds_inter_b64 = dsh.encode_font_woff2_base64(inter_woff2_path)
        print(f"  [ds] encoded Inter woff2 ({len(ds_inter_b64):,} base64 chars)")
    else:
        print(f"  [warn] Inter-VariableFont.woff2 não encontrado — base64 vazio")
        ds_inter_b64 = ""

    # (5) Read the icon sprite (inline SVG, already wrapped in <svg style="display:none">)
    sprite_path = SHARED_DIR / "assets" / "icons" / "sprite.svg"
    if sprite_path.exists():
        icon_sprite = sprite_path.read_text(encoding="utf-8")
    else:
        print(f"  [warn] sprite.svg não encontrado — sprite vazio")
        icon_sprite = '<svg style="display:none" aria-hidden="true"></svg>'

    # (6) Inject DS blobs into source_html via direct string replacement.
    # This is done BEFORE the existing substitute_placeholders call, using
    # the same manual-replace pattern as {{CONTACTS_JSON}} inside
    # substitute_placeholders itself. These placeholders hold large blobs
    # that bypass the _flatten_dict mechanism.
    source_html = source_html.replace("{{DS_CSS}}", ds_css)
    source_html = source_html.replace("{{DS_INTER_WOFF2_BASE64}}", ds_inter_b64)
    source_html = source_html.replace("{{ICON_SPRITE}}", icon_sprite)
    # Note: {{BUILD_DATE}} and {{BUILD_DATE_SHORT}} already exist in context and
    # are handled by substitute_placeholders — no need for a separate
    # {{BUILD_TIMESTAMP}} placeholder.
    # ======================================================================
```

This block uses the real variable names from the existing code (`source_html`, `config`) so it drops in without renaming anything. The DS blob replacements mutate `source_html` in place; the subsequent `substitute_placeholders(source_html, context)` call on line 278 then handles the remaining `{{VERSION}}`, `{{BUILD_DATE}}`, `{{AIRPORT.*}}`, `{{CONTACTS_JSON}}`, and the new `{{PORTAL.*}}` placeholders.

- [ ] **Step 4: Extend the existing `context` dict to include the portal config**

Find the existing `context = { ... }` block in `build()` (around line 270 in the current file):

```python
    # --- 3. Construir contexto de substituição ---
    context = {
        "version": version,
        "build_date": build_date.isoformat(timespec="seconds"),
        "build_date_short": build_date.strftime("%Y-%m-%d"),
        **config,
    }
```

Add one new key `"portal"` whose value is the portal config dict merged with the resolved density. Replace the block with:

```python
    # --- 3. Construir contexto de substituição ---
    context = {
        "version": version,
        "build_date": build_date.isoformat(timespec="seconds"),
        "build_date_short": build_date.strftime("%Y-%m-%d"),
        "portal": {**portal_config, "density": density},  # NEW: enables {{PORTAL.*}} placeholders
        **config,
    }
```

The existing `_flatten_dict` (line 160 of `build.py`) will recursively walk the `"portal"` key and generate uppercase flattened keys like `PORTAL.ID`, `PORTAL.NAME`, `PORTAL.NAME_SHORT`, `PORTAL.TAGLINE`, `PORTAL.ROLE`, `PORTAL.DENSITY`, `PORTAL.UI.SHOW_UTC_CLOCK`, etc. All of these become resolvable as `{{PORTAL.ID}}`, `{{PORTAL.NAME}}`, `{{PORTAL.DENSITY}}`, etc. in the source HTML. The `_` meta keys inside `portal.config.json` are ignored by `_flatten_dict` (line 170: `if k.startswith("_"): continue`).

**Note**: the `"portal"` key is intentionally placed BEFORE `**config` so that if an airport config ever defined a top-level `portal` key it would override the portal config (edge case — not expected, but deterministic).

- [ ] **Step 5: Run build for COE only**

Run: `python packages/portal-coe/scripts/build.py`
Expected output should include new `[ds]` log lines showing the density, compiled CSS size, and base64 length. Exit code 0.

- [ ] **Step 6: Inspect the output HTML for the new placeholders being resolved**

Run:
```bash
python -c "
html = open('packages/portal-coe/dist/Portal_COE_AWM.html', encoding='utf-8').read()
# Check that our placeholders are NO LONGER present (they were resolved)
placeholders = ['{{DS_CSS}}', '{{DS_INTER_WOFF2_BASE64}}', '{{ICON_SPRITE}}', '{{BUILD_TIMESTAMP}}', '{{PORTAL.NAME}}', '{{PORTAL.DENSITY}}']
for p in placeholders:
    assert p not in html, f'Placeholder {p} was NOT resolved!'
print('OK: all DS placeholders resolved in COE output')
# Also check for expected content
assert '--ds-blue-800: #004C7B' in html, 'primitive token not found'
assert 'Portal COE' in html, 'portal name not found'
print(f'File size: {len(html)} bytes')
"
```

**Important**: at this point the Step 6 check will fail because we have NOT yet added the `{{DS_CSS}}` and `{{ICON_SPRITE}}` markers to the source HTML. That is Task 12. This step will be validated fully at end of Task 12.

For now just verify the script ran without errors (exit 0).

- [ ] **Step 7: Commit**

```bash
git add packages/portal-coe/scripts/build.py
git commit -m "feat(coe): extend build.py to consume design system helpers

Imports scripts/ds_build_helpers.py via sys.path manipulation.
In build():
- Loads packages/portal-coe/portal.config.json via dsh.load_portal_config
- Resolves density via dsh.resolve_density (airport override chain)
- Compiles DS CSS via dsh.compile_design_system_css
- Encodes Inter woff2 via dsh.encode_font_woff2_base64
- Reads shared/assets/icons/sprite.svg
- Injects {{DS_CSS}}, {{DS_INTER_WOFF2_BASE64}}, {{ICON_SPRITE}},
  {{BUILD_TIMESTAMP}} via manual replace (same mechanism as
  existing {{CONTACTS_JSON}})
- Merges portal_config into context dict under key 'portal' so
  {{PORTAL.ID}}, {{PORTAL.NAME}}, {{PORTAL.DENSITY}} etc. are
  resolved by _flatten_dict automatically

The function signature (source_path, config_path, output_path,
validate) is preserved to keep build-all.py compatibility.

Source HTML does not yet contain the new placeholder markers —
they are added in Task 12. This commit establishes the pipeline
without yet activating it.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 11: Update `packages/portal-ssci/scripts/build.py` with the same changes

**Files:**
- Modify: `packages/portal-ssci/scripts/build.py`

- [ ] **Step 1: Apply the same changes as Task 10 to portal-ssci**

The changes to `packages/portal-ssci/scripts/build.py` are **structurally identical** to the ones applied to `packages/portal-coe/scripts/build.py`, because both files share the same `build()` skeleton and the same variable names (`source_html`, `config`, `context`, `output_html`, `build_date`).

Apply the same three changes:

1. Add `sys.path.insert(0, str(REPO_ROOT / "scripts"))` and `import ds_build_helpers as dsh` after the existing imports
2. Inside `build()`, insert the same DS payload preparation block between `config = read_config(config_path)` and the `context = { ... }` construction
3. Extend the existing `context` dict to add `"portal": {**portal_config, "density": density}`

**Minor asymmetry to be aware of** (does NOT affect this task, but worth knowing): the two `build.py` files have a small divergence in the signature of `validate_inline_scripts()` — `portal-coe` calls `validate_inline_scripts(output_html, output_path)` (takes the output path for nicer error messages), while `portal-ssci` calls `validate_inline_scripts(output_html)` (one argument only). This is pre-existing drift and is NOT part of Plan 1's scope — do not touch it. The DS changes don't interact with `validate_inline_scripts`.

**PACKAGE_ROOT and SHARED_DIR are already defined** at the top of each `build.py` (COE: lines ~65-75, SSCI: same structure). Your DS insertion block can reference them directly without redefinition.

- [ ] **Step 2: Run build for SSCI only**

Run: `python packages/portal-ssci/scripts/build.py`
Expected: new `[ds]` log lines with `portal=portal-ssci density=comfortable`. Exit 0.

- [ ] **Step 3: Run full build-all**

Run: `python scripts/build-all.py`
Expected: both portals build OK.

- [ ] **Step 4: Commit**

```bash
git add packages/portal-ssci/scripts/build.py
git commit -m "feat(ssci): extend build.py to consume design system helpers

Mirrors the changes in Task 10's portal-coe/scripts/build.py.
Same helper import, same DS payload compilation, same placeholder
replacements, same context extension. The only difference is that
portal-ssci resolves to density=comfortable via its
portal.config.json.

Both builds now load the DS helpers and prepare the payload, even
though the source HTMLs do not yet contain placeholder markers
(Task 12 adds them).

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 12: Add placeholder markers to both source HTMLs

**Files:**
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`

Both portal source HTMLs need **three minimal edits** that add the DS payload insertion points while leaving everything else untouched.

- [ ] **Step 1: Edit COE `<html>` opening tag — add `data-density` attribute**

In `packages/portal-coe/src/Portal_COE_AWM.source.html`, find line 2:

```html
<html lang="pt-PT">
```

Replace with:

```html
<html lang="pt-PT" data-density="{{PORTAL.DENSITY}}">
```

- [ ] **Step 2: Edit COE `<head>` — insert DS style block as first `<style>`**

In the same file, find the first `<style>` tag (currently around line 10, right after the closing `</meta>` block). Insert a new `<style>` BEFORE the existing one. The new block should look like:

```html
    <style>{{DS_CSS}}</style>
    <style>
        :root {
            --dark-blue: #004C7B;
            ... (existing legacy tokens continue unchanged)
```

Concretely, the lines around the current `<style>` go from:

```html
    <meta http-equiv="Expires" content="0">
    <title>Portal COE — {{AIRPORT.NAME}}</title>
    <style>
        :root {
            --dark-blue: #004C7B;
```

to:

```html
    <meta http-equiv="Expires" content="0">
    <title>Portal COE — {{AIRPORT.NAME}}</title>
    <!-- Design System SGA — dormant foundation (Plan 1 of DS migration) -->
    <style>{{DS_CSS}}</style>
    <style>
        :root {
            --dark-blue: #004C7B;
```

The new `<style>` block has nothing inside it but the placeholder; `build.py` replaces the placeholder with the compiled DS CSS at build time.

- [ ] **Step 3: Edit COE `<body>` — insert hidden icon sprite as first child**

Find the line with `<body>` or `<body class="...">` (search for `<body`). Insert the sprite placeholder on the next line, before any existing body content:

Before:
```html
<body>
    <header>
```

After:
```html
<body>
    <!-- Design System SGA — icon sprite (hidden, referenced via <use href="#icon-X"/>) -->
    {{ICON_SPRITE}}
    <header>
```

Note: we do NOT wrap `{{ICON_SPRITE}}` in an extra `<svg>` tag — the `sprite.svg` file already contains its own `<svg style="display:none" aria-hidden="true">` root element.

- [ ] **Step 4: Apply equivalent changes to SSCI source HTML**

In `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`:

1. **`<html>` tag** — change `<html lang="pt-PT">` → `<html lang="pt-PT" data-density="{{PORTAL.DENSITY}}">` (identical to COE)

2. **`<head>` DS style insertion** — the SSCI source header is simpler than COE (no `<meta Expires>`, no `<meta Pragma>`). The anchor is still "before the existing `<style>` block". Concretely, current state:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal PSCI — SSCI {{AIRPORT.NAME}}</title>
    <style>
        :root {
            --dark-blue: #004C7B;
```

After insertion:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal PSCI — SSCI {{AIRPORT.NAME}}</title>
    <!-- Design System SGA — dormant foundation (Plan 1 of DS migration) -->
    <style>{{DS_CSS}}</style>
    <style>
        :root {
            --dark-blue: #004C7B;
```

3. **`<body>` sprite insertion** — same as COE, insert `{{ICON_SPRITE}}` (preceded by a comment marker) as the first child of `<body>`. The SSCI body opening tag may have attributes (check the current source) — preserve them.

- [ ] **Step 5: Run the full build**

Run: `python scripts/build-all.py`
Expected: both portals build OK with `[ds]` log lines, exit 0.

- [ ] **Step 6: Verify all DS placeholders are resolved in both outputs**

Run:
```bash
python -c "
from pathlib import Path
for portal_name, path in [
    ('COE', 'packages/portal-coe/dist/Portal_COE_AWM.html'),
    ('SSCI', 'packages/portal-ssci/dist/Portal_PSCI_AWM.html'),
]:
    html = Path(path).read_text(encoding='utf-8')
    unresolved = []
    for p in ['{{DS_CSS}}', '{{DS_INTER_WOFF2_BASE64}}', '{{ICON_SPRITE}}', '{{BUILD_TIMESTAMP}}', '{{PORTAL.NAME}}', '{{PORTAL.DENSITY}}', '{{PORTAL.ID}}', '{{PORTAL.TAGLINE}}']:
        if p in html:
            unresolved.append(p)
    if unresolved:
        print(f'{portal_name}: UNRESOLVED {unresolved}')
    else:
        print(f'{portal_name}: all DS placeholders resolved')
    # Sanity check: DS tokens are in the output
    assert '--ds-blue-800: #004C7B' in html, f'{portal_name}: primitive tokens missing'
    assert 'data-density=\"compact\"' in html or 'data-density=\"comfortable\"' in html, f'{portal_name}: data-density attribute missing'
    assert 'icon-sga-mark' in html, f'{portal_name}: icon sprite not embedded'
    print(f'{portal_name}: file size {len(html):,} bytes ({len(html)/1024:.0f} KB)')
"
```

Expected output:
```
COE: all DS placeholders resolved
COE: file size 4,XXX,XXX bytes (~4XXX KB)
SSCI: all DS placeholders resolved
SSCI: file size 1,XXX,XXX bytes (~1XXX KB)
```

**Important**: Record both file sizes — these are compared against baseline in Task 13.

- [ ] **Step 7: Commit**

```bash
git add packages/portal-coe/src/Portal_COE_AWM.source.html packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "feat(ds): inject DS placeholder markers into both portal sources

Three minimal edits per portal source HTML:
1. <html lang=\"pt-PT\" data-density=\"{{PORTAL.DENSITY}}\"> adds
   the density attribute that scopes :root[data-density='X'] tokens
2. New <style>{{DS_CSS}}</style> block inserted as the FIRST <style>
   in <head>, before the existing legacy <style>. This ensures the
   legacy block wins specificity ties, preserving behaviour of
   not-yet-migrated components.
3. {{ICON_SPRITE}} placeholder inserted as first child of <body>.
   Replaced at build time with shared/assets/icons/sprite.svg
   content, which includes its own display:none aria-hidden=true
   wrapping <svg>.

With these edits, both portals render visually identical to the
previous build (all DS content is dormant: tokens not consumed,
font declared but not applied, sprite hidden). But the foundation
is now live in both HTMLs, ready for Plan 2 to start consuming it.

Part of Plan 1 (Design System Foundation Dormant)."
```

---

## Task 13: Validate file size deltas

**Files:** none (verification only)

- [ ] **Step 1: Compute size deltas from baseline**

Using the baseline sizes captured in Task 0 Step 5 and the new sizes from Task 12 Step 6:

```
COE baseline:   ~4,0XX KB
COE after DS:   ~4,2XX KB      delta: ~+250 KB
SSCI baseline:  ~1,5XX KB
SSCI after DS:  ~1,7XX KB      delta: ~+250 KB
```

Expected delta range per spec Section 7.5 (Plan 1 intentional delta):
- +200 KB (Inter font base64 encoded — ~150 KB woff2 × ~1.33 base64 overhead = ~200 KB)
- + ~15 KB (sprite SVG + DS CSS tokens)
- Total expected: between `+200 KB` and `+280 KB` per portal

- [ ] **Step 2: Verify delta is within acceptable range**

Read the baseline file captured in Task 0 Step 5 and compare with the current dist sizes:

```bash
python -c "
import json
from pathlib import Path

baseline = json.loads(Path('.plan1-baseline.json').read_text())
current = {
    'portal-coe':  Path('packages/portal-coe/dist/Portal_COE_AWM.html').stat().st_size,
    'portal-ssci': Path('packages/portal-ssci/dist/Portal_PSCI_AWM.html').stat().st_size,
}

# Acceptable Plan 1 delta (spec Section 7.5): +200KB min, +300KB max
MIN_DELTA = 200_000
MAX_DELTA = 300_000

all_ok = True
for portal in ['portal-coe', 'portal-ssci']:
    delta = current[portal] - baseline[portal]
    delta_kb = delta / 1024
    name = portal.replace('portal-', '').upper()
    within = MIN_DELTA <= delta <= MAX_DELTA
    tag = 'OK' if within else 'FAIL'
    print(f'  [{tag}] {name}: baseline {baseline[portal]:>10,} → current {current[portal]:>10,}  delta {delta:+>9,} bytes ({delta_kb:+.0f} KB)')
    if not within:
        all_ok = False

if not all_ok:
    print(f'\\n  Expected delta range per portal: +{MIN_DELTA/1024:.0f} KB to +{MAX_DELTA/1024:.0f} KB')
    import sys
    sys.exit(1)
print('\\n  All deltas within acceptable Plan 1 range.')
"
```

If both portals are within range, proceed. If either is out of range:
- **Delta too small (~0 KB)**: placeholders not being resolved; the source HTML edits from Task 12 may have regressed, or the build helper functions are returning empty strings. Re-run `python scripts/build-all.py` and re-check.
- **Delta too large (>500 KB)**: an unexpectedly large payload — probably Inter woff2 is larger than expected (check `ls -l shared/assets/fonts/Inter-VariableFont.woff2`) or the sprite file grew unexpectedly.

- [ ] **Step 3: No commit** (this task is verification only)

---

## Task 14: Visual smoke test — verify zero visual regression

**Files:** none (manual verification)

- [ ] **Step 1: Open `dist/Portal_COE_AWM.html` in Chrome**

Open: `file:///d:/VSCode_Claude/03-Resende/Portal_DREA-ds/packages/portal-coe/dist/Portal_COE_AWM.html`

- [ ] **Step 2: Login and navigate the same sections as the baseline screenshots (Task 0 Step 6)**

For each of: Dashboard, Ocorrência, Contactos, Verificação Mensal, Mapas Quadrícula, Fluxogramas, Configurações:
- Open the section
- Compare visually with the baseline screenshot in `d:/tmp/plan1-baseline/`
- Note any differences — there should be NONE

If you see any visual difference (colour shift, layout change, font change, spacing change), STOP and investigate. Root causes to check:
- Did the new `<style>` block include something other than `{{DS_CSS}}`?
- Did the `<body>` insertion accidentally break existing CSS selectors that depended on `<header>` being the first child?
- Is the sprite SVG somehow affecting layout (check with DevTools that it has `display:none`)?

- [ ] **Step 3: Open DevTools → Elements → `<html>` — confirm `data-density="compact"` attribute is present**

- [ ] **Step 4: DevTools → Elements → `<head>` — confirm two `<style>` blocks exist, the first containing `--ds-*` tokens**

The first `<style>` (new) should contain `--ds-blue-800: #004C7B;` and related tokens. The second `<style>` (legacy) should have the original `--dark-blue: #004C7B;` etc.

- [ ] **Step 5: DevTools → Elements → `<body>` — confirm hidden sprite SVG is the first child**

Should see: `<svg style="display:none" aria-hidden="true">...<symbol id="icon-sga-mark">...</svg>` as the first child of `<body>`.

- [ ] **Step 6: DevTools → Network → Font tab — confirm Inter is loaded**

Reload the page. Check the Font tab — Inter should appear as a loaded font (embedded as data: URL).

- [ ] **Step 7: Console → run `getComputedStyle(document.body).getPropertyValue('--ds-blue-800')`**

Expected output: `" #004C7B"` (leading space is CSS normalisation). Confirms tokens are live and cascading.

Also run: `getComputedStyle(document.body).fontFamily` — expected to still be `"Segoe UI", ...` (the legacy font family), proving the Inter font is loaded but NOT applied. This is the invariant of "dormant".

- [ ] **Step 8: Repeat Steps 1-7 for SSCI**

Open `dist/Portal_PSCI_AWM.html`, navigate its sections (Dashboard, Registo, Inspecções, Checklists, Estoque, etc.), compare against baseline screenshots, check DevTools.

SSCI should show `data-density="comfortable"` and have the same dormant foundation active.

- [ ] **Step 9: Cross-browser spot check**

Open both HTMLs in Edge (pre-installed on Windows). Quick navigation — no deep smoke test needed, just verify they load and render without JS errors.

Firefox optional but recommended (focus trap behaviour historically the most fragile across browsers, but this Plan does not touch focus trap).

- [ ] **Step 10: No commit** (verification only)

If all steps pass, Plan 1 is functionally complete. Proceed to Task 15.

---

## Task 15: Final integration — run full test suite + build-all + commit plan marker

**Files:**
- Create: `docs/superpowers/plans/2026-04-11-design-system-plan-1-foundation.md` (add COMPLETED marker)

- [ ] **Step 1: Run the full pytest suite one more time**

Run: `python -m pytest tests/ -v`
Expected: all tests pass (~15 tests total across Tasks 1-6).

- [ ] **Step 2: Run build-all one more time**

Run: `python scripts/build-all.py`
Expected: both portals build OK, `[ds]` log lines visible, exit 0.

- [ ] **Step 3: Git log summary**

Run: `git log --oneline feat/design-system ^main`
Expected: roughly 13-15 commits from Tasks 1-12 (one per task approximately, possibly grouped).

- [ ] **Step 4: Update the plan document to mark Plan 1 as complete**

Edit `docs/superpowers/plans/2026-04-11-design-system-plan-1-foundation.md` — add a section at the very top, right after the title:

```markdown
> **Status:** ✅ Completed YYYY-MM-DD (replace with today's date)
> **Commits:** see `git log feat/design-system ^main`
> **Next plan:** [Plan 2 — COE Component Migration](./2026-04-11-design-system-plan-2-coe-components.md) (to be written when ready to proceed)
```

- [ ] **Step 5: Commit the completion marker**

```bash
git add docs/superpowers/plans/2026-04-11-design-system-plan-1-foundation.md
git commit -m "docs(ds): mark Plan 1 (Foundation Dormant) as complete

All 14 tasks executed successfully:
- Token layer (primitive, semantic, density compact/comfortable) created
- ds_build_helpers.py with 4 helpers (load_portal_config, resolve_density,
  compile_design_system_css, encode_font_woff2_base64) fully tested
- Inter Variable font embedded in both portal HTMLs as base64
- Minimal SVG icon sprite seeded with 3 icons
- portal.config.json added for both COE and SSCI
- Both build.py scripts extended to compile and inject DS payload
- Source HTMLs edited with minimal placeholder markers

Invariant preserved: both dist/*.html render visually identical to
the v2.0.0-beta.1 baseline. Foundation is DORMANT — tokens defined,
font loaded, sprite embedded, but nothing consumed yet. File size
grew by ~250 KB per portal (Inter + sprite + tokens).

Ready for Plan 2 to begin activating components.

Part of Plan 1 (Design System Foundation Dormant)."
```

- [ ] **Step 6: Summary to the user**

Report to the user:
1. Plan 1 complete, N commits on `feat/design-system` branch
2. File size deltas (COE +X KB, SSCI +X KB)
3. Visual diff result (zero regressions)
4. Test suite: N tests passing
5. Worktree remains at `../Portal_DREA-ds` for Plan 2 to reuse
6. `main` unchanged at `v2.0.0-beta.1`

---

## Verification Checklist (Plan 1 Definition of Done)

- [ ] `python -m pytest tests/ -v` → all tests pass
- [ ] `python scripts/build-all.py` → exit 0 for both portals
- [ ] Both `dist/*.html` open without console errors in Chrome, Edge, Firefox
- [ ] Visual diff against baseline: zero regressions in dashboard, forms, tables, contacts
- [ ] DevTools shows `<html data-density="...">` attribute present
- [ ] DevTools shows two `<style>` blocks (new DS first, legacy second)
- [ ] DevTools shows hidden `<svg>` sprite as first child of `<body>`
- [ ] DevTools Network → Inter woff2 loaded as data: URL
- [ ] Console `getComputedStyle(body).getPropertyValue('--ds-blue-800')` returns `" #004C7B"`
- [ ] Console `getComputedStyle(body).fontFamily` returns legacy font family (Segoe UI / system), NOT Inter
- [ ] File size delta per portal: +200 to +300 KB (intentional Plan 1 delta)
- [ ] `main` branch remains at `v2.0.0-beta.1` (worktree isolation preserved)
- [ ] `feat/design-system` branch has ~14 atomic commits, one per task

---

## Rollback Plan

If anything goes wrong at any point during Plan 1:

- **Single-task failure**: `git reset --hard <sha-before-task>` inside the worktree
- **Whole-plan failure**: delete the worktree via `git worktree remove ../Portal_DREA-ds` and start over. `main` is untouched, no data lost.
- **Partial completion with working baseline**: commit what works, document the blocker in a new section of this plan, ask the user for guidance.
