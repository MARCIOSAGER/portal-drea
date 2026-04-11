# Design System SGA — Plan 3: COE Component Migration (Implementation Plan)

> **Status:** 📝 Draft ready for execution (Plan 3 of 6 in the DS SGA migration sequence).
> **Prerequisite:** Plan 1 ✅ merged at `f81d6db` (Foundation Dormant) and Plan 2 ✅ merged at `9dcd9ef` (Style Block Consolidation). `main` must be clean and at `bc11d89` or later before starting.
> **Next plan after this one:** Plan 4 — COE Chrome Migration (shell bar, sidebar, splash, print).

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Each component migration is one task, one commit, one bisectable unit.

**Goal:** Extract individual CSS components from the COE consolidated legacy block 1 (created by Plan 2) into dedicated files under `shared/styles/components/*.css`, re-tokenized against the `--ds-*` semantic tokens from Plan 1. The `compile_design_system_css()` helper in `scripts/ds_build_helpers.py` is extended to include `components/*.css` in its deterministic cascade order after `base/fonts.css`. Each migration is one component → one file → one commit → visually verified. The SSCI portal and the Chrome layer are **out of scope** for Plan 3 — they are handled by Plans 5 and 4 respectively.

**Architecture:** Plan 2 left each portal source with a single consolidated `<style>` block (COE block 1 after `{{DS_CSS}}`, 100,006 chars). Plan 3 rewrites the COE source HTML to remove one component's CSS rules from that block at a time, while adding the equivalent tokenized CSS as a new file under `shared/styles/components/`. The Plan 1 `{{DS_CSS}}` payload is injected **before** the legacy block, so on each migration step the cascade order is preserved: DS components CSS (from the first `<style>`) provides the only declaration for the migrated selector — the legacy block no longer has it. Plans 2's `verify_consolidation.py` CLI is no longer byte-identity true after each task, but remains a regression fence for **non-migrated** selectors: its expected-concatenation CLI will continue to pass when the removed rules are excluded from the baseline indices. Visual equivalence (not byte-identity) becomes the invariant for migrated rules.

**Tech Stack:** Python 3.8+ (`ds_build_helpers.py` extended via TDD, existing `build.py` scripts unchanged — they already call the helper), pytest (growing the existing 33-test suite), vanilla CSS (new component files targeting `--ds-*` tokens), git atomic commits per component, worktree isolation.

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) v1.1 — Sections 3 (Foundation), 5 (Components inventory), 6.2 (Cascade order), 7.3 (Migration strategy Fase 2).

**Reference plans:** [Plan 1](./2026-04-11-design-system-plan-1-foundation.md), [Plan 2](./2026-04-11-design-system-plan-2-style-consolidation.md).

**Invariant this plan must preserve:** After every task commit, **both** portal dist HTMLs must build cleanly AND the COE portal must be **visually equivalent** to the pre-Plan-3 baseline when opened in Chrome/Edge. "Visually equivalent" means: no perceptible change in layout, colour, spacing, typography, hover/focus behaviour, or modal/toast/save-badge behaviour. Because re-tokenisation replaces legacy `var(--dark-blue)` with `var(--ds-brand-primary)` (both resolve to `#004C7B`), and because DS `--ds-*` tokens were proven at Plan 1 to resolve to identical computed values as their legacy counterparts, visual equivalence is **achievable** — it is not optimistic. The verification is a combination of (a) programmatic: `build-all.py` exits 0, full pytest green, `verify_consolidation.py` still passes for non-migrated selectors, no `<script>` or console errors; (b) human eyeball: open the dist HTML, exercise the affected component in the affected sections, compare side-by-side to the baseline capture taken in Task 0.

## Key fact sheet (verified by inspection on 2026-04-11 against COE consolidated block 1 post-Plan-2)

### The consolidated block to mine

- **File**: `packages/portal-coe/src/Portal_COE_AWM.source.html`
- **Block 1** = position `517`..`~100k chars` inside that file (immediately after the `{{DS_CSS}}` placeholder `<style>`)
- **Size**: ~100,006 chars of real CSS + Plan 2 consolidation banners
- **Total `<style>` blocks in file after Plan 2**: 8 (0=DS placeholder, 1=consolidated legacy, 2+3+4+8+10+14=JS-embedded CSS literals for PDF export; indices here refer to DOM order in the **current** post-Plan-2 source)

### Real selectors present in block 1 — verified inspection

Every row below is a grep hit against the live consolidated block 1. **There is no grep-guessing in this plan.**

| Component group | Selectors verified present | Notes |
|---|---|---|
| **button (legacy variants)** | `.btn-print-card`, `.btn-print-card:hover`, `.btn-export`, `.btn-export:hover`, `.btn-clear`, `.btn-clear:hover`, `.btn-export-all`, `.btn-export-all:hover`, `.btn-timeline`, `.btn-start`, `.btn-start:hover`, `.btn-stop`, `.btn-stop:hover`, `.btn-reset`, `.btn-reset:hover`, `.btn-uf-print`, `.btn-uf-export`, `.btn-uf-clear`, `.btn-print-single`, `.btn-print-pack` | **There is NO base `.btn {}` selector** in this source — every button is defined via a variant class. The `.btn` token appears only inside a `@media print` `display:none` rule (`.btn, button, .timer-display, ...`). Plan 3 introduces a shared `.btn` base class + DS variants; however re-mapping HTML markup from `.btn-print-card` → `.btn .btn--secondary` is NOT in scope. Plan 3 keeps the legacy variant class names and re-tokenises their property values only. Any new markup using `.btn .btn--primary` is introduced incrementally by future plans if needed. |
| **badge / chip** | `.cr-chip`, `.cr-chip b`, `.cr-chips` (flex container) | No `.badge` selector exists in COE legacy. `.cr-chip` is the only chip-style element in block 1 (used inside contact fichas). Plan 3's `components/badge.css` defines `.badge` + status variants **AND** re-tokenises `.cr-chip` so the existing fichas keep working. |
| **form-group / input / select / textarea** | `.form-group`, `.form-group label`, `.form-group input`, `.form-group textarea`, `.form-group select`, `.form-group input:focus`, `.form-group textarea:focus`, `.form-group select:focus`, `.form-group textarea` (resize), `.form-full-width`, `.form-actions` | Entire form block lives in a ~50-line region near the top of block 1 (starting at original line ~520). `var(--dark-blue)`, `var(--medium-blue)` both present. Note: `#bombaFormBlock input[type=text]...` and `#emgFormBlock input[type=text]...` rules are domain-specific overrides inside `bombaFormBlock` / `emgFormBlock` sections and are **left in the consolidated block** (they are domain-layered rules, not generic form-group rules). Migrating them is Plan 6 scope. |
| **contact-card** | `.contact-card`, `.contact-card-header`, `.contact-card-header.internal`, `.contact-card-header.external`, `.contact-card-header.authority`, `.contact-card-body`, `.alarm-card-header`, `.alarm-card-header.alarm-red`, `.alarm-card-header.alarm-amber`, `.alarm-card-body` | Contact card and alarm card are genuine card patterns. There is NO generic `.card` selector. Plan 3's `components/card.css` introduces a `.card` base + variants and re-tokenises `contact-card` and `alarm-card` to consume the new tokens (class name preserved — these names are referenced by JS at lines 14557, 14611, 3389, 3396). |
| **stat-card** | **Not present** — no `.stat-card` in COE legacy. | `components/stat-card.css` is introduced as a **new** file with zero legacy removal. It is new scaffolding that the COE UI does not yet consume; later plans refit dashboard tiles onto it. Plan 3 ships the file so Plan 4/5/6 can use it; no visual change on Plan 3. |
| **table** | Generic: `table {}`, `th, td {}`, `th {}` in block 1. Domain: `.contacts-table`, `.contacts-table th`, `.timeline-log table`, `#verif-contactos table.vc-table`, `#verif-contactos table.vc-table th`, `#verif-contactos table.vc-table td`, `.vc-table-wrap`, `.vc-cat-row`, `.vc-num`, `.vc-name`, `.vc-func`, `.vc-tel`, etc. | Plan 3's `components/table.css` migrates ONLY the **generic** `table {}`/`th, td {}`/`th {}` rules. The `#verif-contactos` `.vc-*` selectors are domain components (spec §5.4) and stay in the consolidated block, but they reference DS tokens after migration. Plan 3 does NOT move `vc-*` to `components/` — they are a portal-domain concern. |
| **tabs** | `.tab-content {}`, `.tab-content.active {}` | Minimal surface: 2 rules. Plan 3's `components/tabs.css` re-tokenises these. Note: `.tab-header` and `.tab-btn` appear to not exist as selectors in the consolidated block (grep finds only `.tab-header` inside a `@media print` hide rule). This is a surface we formalise in Plan 4 when chrome is migrated; Plan 3's tabs component file is a minimal version that covers only what exists today. |
| **dropdown / menu** | **Not present as CSS**. Grep for `dropdown`/`.menu`/`menu-item` returns only a JS comment reference. | `components/dropdown.css` is introduced as **new scaffolding**, zero legacy removal. Same approach as stat-card — creates the file so later plans can consume it. |
| **awm-modal** | `.awm-modal-overlay`, `.awm-modal`, `.awm-modal-header`, `.awm-modal-icon`, `.awm-modal.question .awm-modal-icon`, `.awm-modal.warning .awm-modal-icon`, `.awm-modal.danger .awm-modal-icon`, `.awm-modal-title`, `.awm-modal-body`, `.awm-modal-footer`, `.awm-modal-btn`, `.awm-modal-btn:active`, `.awm-modal-btn.cancel`, `.awm-modal-btn.cancel:hover`, `.awm-modal-btn.primary`, `.awm-modal-btn.primary:hover`, `.awm-modal-btn.danger`, `.awm-modal-btn.danger:hover`, plus `@media print` hide rule | 50+ selector occurrences. **JS references** confirmed at line 5067 (`overlay.className = 'awm-modal-overlay'`) and in many other places. Class names are **load-bearing** — preserve verbatim. Task migrates CSS only. |
| **awm-toast** | `.awm-toast`, `.awm-toast.success`, `.awm-toast.warning`, `.awm-toast.error`, `.awm-toast.info`, `.awm-toast-icon`, `.awm-toast.success .awm-toast-icon`, `.awm-toast.warning .awm-toast-icon`, `.awm-toast.error .awm-toast-icon`, `.awm-toast.info .awm-toast-icon`, `.awm-toast-body`, `.awm-toast-title`, `.awm-toast-msg`, `.awm-toast-close`, `.awm-toast-close:hover`, `.awm-toast-progress`, `.awm-toast.success .awm-toast-progress`, `.awm-toast.warning .awm-toast-progress`, `.awm-toast.error .awm-toast-progress`, `.awm-toast.info .awm-toast-progress` | 30+ occurrences. Same preservation rules as `awm-modal`. |
| **save-badge** | `.uxp-savebadge`, `.uxp-savebadge.visible`, `.uxp-savebadge.saving`, `.uxp-savebadge.saved`, `.uxp-savebadge.error`, `.uxp-savebadge .dot`, `.uxp-savebadge.saving .dot`, `.uxp-savebadge.saved .dot`, `.uxp-savebadge.error .dot`, plus `@keyframes uxp-pulse` | **Class name is `.uxp-savebadge`, NOT `.awm-save-badge`** — spec §5.3 mentions the semantic `awm-save-badge` component but the real class in the COE source is `uxp-savebadge` (lines 12944, 12952 reference it in JS). Task 11 preserves `.uxp-savebadge` verbatim. |
| **skeleton** | **Not present** — no `.skeleton`/`shimmer` anywhere. | **New scaffolding**, zero removal. Respects `prefers-reduced-motion`. |
| **empty-state** | **Not present** — no `.empty-state` anywhere. | **New scaffolding**, zero removal. |

### Important constraints discovered by inspection

1. **There is no generic `.btn` base class in COE legacy.** Plan 3's `components/button.css` **introduces** a `.btn` base class (following spec §5.1) plus the existing `.btn-*` variant classes re-tokenised. This preserves existing HTML markup (the `<button class="btn-export">` buttons still work because the variant classes are kept) while providing a proper base for future HTML to use `.btn .btn--primary`.

2. **`.vc-*` table and form selectors stay in the consolidated block.** Domain-layered rules (prefixed with `#verif-contactos`, `#bombaFormBlock`, `#emgFormBlock`) are tier-4 domain components per spec §5.4. Migrating them is Plan 6 scope. Plan 3's `components/table.css`, `components/form-group.css`, `components/input.css` handle only the **generic** unprefixed rules.

3. **Class names inside `awm-*` and `uxp-*` are JS-load-bearing.** grep confirms 50+ references from `<script>` blocks. Plan 3 re-tokenises their **property values** only — selector names stay verbatim.

4. **No dropdown/stat-card/skeleton/empty-state CSS exists in legacy.** Four of the twelve Plan 3 component tasks are pure additions (new scaffolding files) with zero legacy removal. They have reduced risk because there is no "cascade race" to get right.

5. **Cascade order after Task 1** will be:
   ```
   <style>{{DS_CSS}}</style>     ← primitive + semantic + density + fonts + components/*.css (alphabetical)
   <style> [consolidated block 1 minus the migrated rules] </style>
   [6 JS-embedded <style> literals, untouched]
   ```

   For every migrated selector, the ONLY declaration remaining is in `{{DS_CSS}}`. For every non-migrated selector, the ONLY declaration remains in block 1. No dual definitions.

6. **`verify_consolidation.py` still runs but with shrinking baseline indices.** Plan 3 does NOT invalidate Plan 2's byte-identity check for the rules that remain unmigrated; it simply narrows which bytes participate. After Plan 3 completes, `verify_consolidation.py` can still run with `--block-indices 1` to confirm that block 1's remaining content is still a verbatim subset of the original block 1 from Plan 2's baseline — with the migrated selectors removed. We formalise this as "block 1 minus migrated rules == Plan 2 baseline block 1 minus the same rules" at the end of Plan 3 (Task 13).

---

## Why this plan exists

Plan 2 consolidated the legacy CSS into one place per portal. Plan 3 splits that one place into ~12 new maintainable component files consumed by the DS cascade. After Plan 3:

- `components/button.css` is the **only** source of truth for button styling across the DS.
- The COE portal still works visually identically because the tokens `--ds-brand-primary` and `--dark-blue` resolve to the same hex value.
- Future portals (SSCI in Plan 5, SOA/AVSEC later) consume `components/button.css` for free.
- Legacy block 1 shrinks monotonically with each commit. By the end of Plan 3 it contains only: domain rules (`.vc-*`, `#bombaFormBlock`, `#emgFormBlock`, `#fichas-seg`), chrome rules (`header`, `.sidebar`), and the legacy `:root { --dark-blue, --medium-blue, ... }` variable aliases (those go in Plan 6).

This plan is **the first plan where visual output can visibly change** if a rule is lost. The invariant therefore shifts from byte-identity (Plan 2) to visual equivalence (Plan 3+). See "Why visual equivalence is the right invariant" at the end.

---

## Out of scope for Plan 3 (explicit)

- ❌ **SSCI component migration** — Plan 5 applies the Plan 3 pattern to the SSCI portal.
- ❌ **COE chrome migration** — `header`, `.sidebar`, splash screen, print header are Plan 4. Plan 3 does NOT touch block 1's `header {}`, `.sidebar {}`, or `@media print` rules.
- ❌ **`base/reset.css`, `base/typography.css`, `base/global.css`** — these interact with chrome and are Plan 4 scope. Plan 3 only extends the cascade with `components/`; it does NOT add new files under `base/`.
- ❌ **`--ds-*` → `--*` namespace rename** — Plan 6 scope. During Plan 3 the new component files reference `var(--ds-brand-primary)` explicitly. The rename is global and cross-plan.
- ❌ **Removal of legacy `:root { --dark-blue, --medium-blue, ... }` from block 1** — Plan 6 scope. During Plan 3 those variable aliases remain in the consolidated block so that any un-migrated domain rule that references `var(--dark-blue)` still resolves.
- ❌ **Domain components** — `.vc-*` (verif-contactos table), `.ficha-unified-form *` (fichas-seg), `#bombaFormBlock *`, `#emgFormBlock *`, `.occ-*` cards, `.timeline-log *`, `.alarm-card-*`, `.flow-node *`, `.cronómetro / .timeline-clock *`. These stay in the portal and are re-tokenised **in place** by Plan 6 (the "remove namespace + legacy tokens" plan).
- ❌ **Expanding the SVG sprite** beyond the 3-icon seed. If a component (e.g., skeleton, empty-state) needs a new icon, add it minimally. No bulk expansion.
- ❌ **Rewriting HTML markup in the COE source.** Plan 3 changes CSS rules only. No `<button class="btn-export">` → `<button class="btn btn--secondary">` renames. Those are Plan 6/7 markup modernisation.
- ❌ **Playwright smoke tests.** Proposed in Task 13 as deferred (see that task for the rationale).

---

## File structure (Plan 3 scope)

### Files to create (13)

```
Portal_DREA/
├── shared/
│   └── styles/
│       └── components/                       NEW directory
│           ├── button.css                    NEW — Task 2
│           ├── badge.css                     NEW — Task 3
│           ├── form-group.css                NEW — Task 4 (contains input/select/textarea rules)
│           ├── card.css                      NEW — Task 5
│           ├── stat-card.css                 NEW — Task 5 (new scaffolding, no legacy removal)
│           ├── table.css                     NEW — Task 6
│           ├── tabs.css                      NEW — Task 7
│           ├── dropdown.css                  NEW — Task 8 (new scaffolding)
│           ├── awm-modal.css                 NEW — Task 9
│           ├── awm-toast.css                 NEW — Task 10
│           ├── uxp-savebadge.css             NEW — Task 11 (class name matches real legacy — NOT "awm-save-badge")
│           ├── skeleton.css                  NEW — Task 12 (new scaffolding)
│           └── empty-state.css               NEW — Task 12 (new scaffolding)
```

### Files to modify (3)

```
scripts/ds_build_helpers.py                           MODIFY — Task 1 (extend compile_design_system_css)
tests/test_ds_build_helpers.py                        MODIFY — Task 1 (new tests for components/ cascade)
packages/portal-coe/src/Portal_COE_AWM.source.html    MODIFY — Tasks 2-12 (remove migrated rules from block 1)
```

### Files NOT touched (hold the line)

Everything else in `packages/` (all of portal-ssci, portal-coe/scripts, portal-coe/dist), `shared/styles/tokens/`, `shared/styles/base/`, `shared/assets/`, `config/`, `scripts/build-all.py`, `scripts/verify_consolidation.py`, `tests/test_verify_consolidation.py`, `docs/`, `VERSION`. In particular, **both `build.py` scripts are NOT modified** — they already call `compile_design_system_css()` and will pick up the new components automatically.

---

## Execution invariant (run after every component migration task)

Every task from Task 2 through Task 12 inclusive is a "migrate one component" task and MUST end green on all four checks:

1. **Build** — `python scripts/build-all.py` exits 0 for both portals. Neither portal dist HTML is broken. SSCI is untouched by Plan 3 and must still build identically to Plan 2.
2. **Tests** — `python -m pytest tests/ -q` — all tests pass. Plan 3 should end with at least 33 + (new tests introduced by Task 1 + Task 13) ≥ 38 tests passing.
3. **Visual smoke** — Open `packages/portal-coe/dist/Portal_COE_AWM.html` in Chrome. Exercise the affected component in its real UI context. Compare side-by-side (two tabs) against `d:/tmp/plan3-baseline/coe.html`. No perceptible difference.
4. **Partial byte-identity diagnostic** — `python scripts/verify_consolidation.py --source packages/portal-coe/src/Portal_COE_AWM.source.html --baseline d:/tmp/plan3-baseline-source/portal-coe.source.html --block-indices 1 --consolidated-index 1` **is EXPECTED to fail** for every task from Task 2 onwards (the current block 1 is shrinking as rules are migrated out). The helper CLI is still run as a diagnostic. Its failure message must show ONLY the migrated rules as the diff — never any unrelated content. If the diff surfaces an unrelated change, that is a bug. Note the `--block-indices 1` is correct for Plan 3: the Plan 3 baseline is the **post-Plan-2** source which has 8 blocks with block 1 already consolidated; we are comparing current block 1 against baseline block 1, not reconstructing from 11 sub-blocks as in Plan 2.

Additionally, at fixed checkpoints (after Tasks 5, 9, 12, 13):

5. **Cross-browser** — Open the dist in Edge. Verify modal/toast/save-badge focus trap still works. Firefox is nice-to-have, Edge is mandatory because it is the SGA operator's default browser.

---

## Task 0: Prerequisites — worktree setup + baseline capture

**Files:** none (infrastructure)

- [ ] **Step 1: Verify main is clean and at a post-Plan-2 commit**

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA && git status --short && git log --oneline -5
```

Expected: empty working tree, HEAD at `bc11d89` (release beta.1) or later — but MUST be at a commit that includes `9dcd9ef` (Plan 2 merge). If Plan 2 is not yet merged, STOP — Plan 3 depends on the consolidated block existing.

- [ ] **Step 2: Create worktree for Plan 3**

Using the `superpowers:using-git-worktrees` skill, create a fresh worktree:

```bash
git worktree add ../Portal_DREA-ds-components -b feat/ds-coe-components
git worktree list
```

Expected: two worktrees listed (main + the new one).

- [ ] **Step 3: Switch working directory and verify baseline build**

```bash
cd ../Portal_DREA-ds-components
python scripts/build-all.py
python -m pytest tests/ -q
```

Expected: both portals build OK, **33 tests passing** (20 Plan 1 + 13 Plan 2), zero regressions.

- [ ] **Step 4: Capture pre-Plan-3 dist HTML baseline for visual comparison**

Critical: Plan 3's invariant is visual equivalence, not byte-identity. We still want SHA-256 of the pre-Plan-3 dist HTMLs as a "this is what we started from" reference, plus a copy of the HTMLs themselves for side-by-side browser comparison.

```bash
python << 'PYEOF'
import hashlib, shutil, json
from pathlib import Path

baseline_dir = Path("d:/tmp/plan3-baseline")
baseline_dir.mkdir(parents=True, exist_ok=True)

results = {}
for name, rel in [
    ("coe", "packages/portal-coe/dist/Portal_COE_AWM.html"),
    ("ssci", "packages/portal-ssci/dist/Portal_PSCI_AWM.html"),
]:
    src = Path(rel)
    content = src.read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    dst = baseline_dir / f"{name}.html"
    dst.write_bytes(content)
    results[name] = {"size": len(content), "sha256": sha, "baseline_path": str(dst)}
    print(f"{name}: {len(content):,} bytes  sha256={sha[:16]}...  -> {dst}")

(baseline_dir / "manifest.json").write_text(json.dumps(results, indent=2))
print(f"\nManifest written to {baseline_dir / 'manifest.json'}")
PYEOF
```

Expected: two files copied. Record the SHA256 hashes in the task log — any time a task claims "SSCI unchanged", we can re-verify SSCI sha256 still matches this baseline.

- [ ] **Step 5: Capture the pre-Plan-3 source HTMLs as a text baseline for diff helpers**

```bash
python << 'PYEOF'
import hashlib, shutil
from pathlib import Path

baseline_dir = Path("d:/tmp/plan3-baseline-source")
baseline_dir.mkdir(parents=True, exist_ok=True)

for name, rel in [
    ("portal-coe",  "packages/portal-coe/src/Portal_COE_AWM.source.html"),
    ("portal-ssci", "packages/portal-ssci/src/Portal_PSCI_AWM.source.html"),
]:
    src = Path(rel)
    dst = baseline_dir / f"{name}.source.html"
    shutil.copyfile(src, dst)
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    print(f"{name}: sha256={sha[:16]}... -> {dst}")
PYEOF
```

Expected: two files copied to `d:/tmp/plan3-baseline-source/`. Used by task-level diagnostics later.

- [ ] **Step 6: Confirm the consolidated block 1 matches Plan 2 expectations**

```bash
python << 'PYEOF'
import re
from pathlib import Path

for portal, path, expected_blocks, expected_min_len in [
    ("COE",  "packages/portal-coe/src/Portal_COE_AWM.source.html",  8, 95000),
    ("SSCI", "packages/portal-ssci/src/Portal_PSCI_AWM.source.html", 5, 20000),
]:
    src = Path(path).read_text(encoding="utf-8")
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", src, re.DOTALL)
    print(f"{portal}: {len(blocks)} style blocks (expected {expected_blocks})")
    if len(blocks) >= 2:
        print(f"  block 1 length: {len(blocks[1]):,} chars (expected >= {expected_min_len:,})")
    assert len(blocks) == expected_blocks, f"{portal}: drift detected"
    assert "PLAN 2 CONSOLIDATION" in blocks[1], f"{portal}: Plan 2 banner missing from block 1"
PYEOF
```

Expected: COE 8 blocks, SSCI 5 blocks, both contain the Plan 2 banner in block 1. If mismatch, STOP — the baseline has drifted.

- [ ] **Step 7: No commit** (infrastructure only)

---

## Task 1: Extend `compile_design_system_css()` to include `components/*.css` in cascade order

**Files:**
- Modify: `scripts/ds_build_helpers.py`
- Modify: `tests/test_ds_build_helpers.py`
- Create: `shared/styles/components/` (empty directory, `.gitkeep` optional)

This task is **pure TDD**. Write the failing test first, then extend the helper. No real component files are added yet — the helper must handle the case where `components/` exists but is empty (zero files), and the case where `components/` contains one or more `*.css` files. Task 2 onwards will add real files.

- [ ] **Step 1: Add failing tests to `tests/test_ds_build_helpers.py`**

Append a new test class inside `TestCompileDesignSystemCss` (the existing class in `tests/test_ds_build_helpers.py`):

```python
    def test_components_dir_absent_is_ok(self, tmp_path: Path):
        """Plan 1 world: no components/ directory — compile must still succeed."""
        self._setup_fake_styles(tmp_path)
        # components/ intentionally not created
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* primitive */" in result  # still works
        # No component banners appear
        assert "components/" not in result

    def test_components_dir_empty_is_ok(self, tmp_path: Path):
        """Plan 3 Task 1 world: components/ exists but is empty — compile succeeds, no content added."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "components").mkdir()
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* primitive */" in result
        assert "components/" not in result

    def test_components_single_css_file_included_after_base(self, tmp_path: Path):
        """Plan 3 Task 2+ world: components/button.css must appear AFTER base/fonts.css."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "components").mkdir()
        (tmp_path / "components" / "button.css").write_text(
            "/* button */\n.btn { color: red; }\n", encoding="utf-8"
        )
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* button */" in result
        assert ".btn { color: red; }" in result
        # Ordering: fonts comes before button
        assert result.index("/* fonts */") < result.index("/* button */")

    def test_components_multiple_css_files_alphabetical_order(self, tmp_path: Path):
        """Multiple components/*.css concatenated in alphabetical filename order."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "components").mkdir()
        # Write in reverse alphabetical order to prove the helper sorts.
        (tmp_path / "components" / "zebra.css").write_text(
            "/* zebra */\n.zebra {}\n", encoding="utf-8"
        )
        (tmp_path / "components" / "button.css").write_text(
            "/* button */\n.btn {}\n", encoding="utf-8"
        )
        (tmp_path / "components" / "card.css").write_text(
            "/* card */\n.card {}\n", encoding="utf-8"
        )
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        # Order: button < card < zebra (alphabetical)
        assert result.index("/* button */") < result.index("/* card */")
        assert result.index("/* card */") < result.index("/* zebra */")

    def test_components_non_css_files_ignored(self, tmp_path: Path):
        """Only files matching *.css are concatenated. README.md etc. ignored."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "components").mkdir()
        (tmp_path / "components" / "button.css").write_text(
            "/* button */\n.btn {}\n", encoding="utf-8"
        )
        (tmp_path / "components" / "README.md").write_text(
            "Do not include me", encoding="utf-8"
        )
        (tmp_path / "components" / "button.css.bak").write_text(
            "/* backup */\nbad-css {}\n", encoding="utf-8"
        )
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* button */" in result
        assert "Do not include me" not in result
        assert "/* backup */" not in result
```

- [ ] **Step 2: Run the tests — expect all 5 new tests to FAIL**

```bash
python -m pytest tests/test_ds_build_helpers.py::TestCompileDesignSystemCss -v
```

Expected: the 5 new tests fail with assertion errors or pass trivially on the "absent dir" case (existing helper doesn't look at components/, so it returns without components/ content, which makes some tests pass accidentally). Read the output carefully — at minimum `test_components_single_css_file_included_after_base`, `test_components_multiple_css_files_alphabetical_order`, `test_components_non_css_files_ignored` MUST fail.

- [ ] **Step 3: Extend `compile_design_system_css()` in `scripts/ds_build_helpers.py`**

Modify the function to add a component-discovery phase after the optional `base/fonts.css` handling. The new code block:

```python
    # NEW (Plan 3): discover components/*.css in alphabetical order.
    # Non-CSS files and subdirectories are ignored.
    components_dir = styles_root / "components"
    component_files: list[Path] = []
    if components_dir.is_dir():
        component_files = sorted(
            p for p in components_dir.iterdir()
            if p.is_file() and p.suffix == ".css"
        )

    pieces: list[str] = []
    for f in required_files + optional_files + component_files:
        if not f.exists():
            continue  # optional file, skip
        rel_path = f.relative_to(styles_root.parent).as_posix()
        banner = f"/* ---------- {rel_path} ---------- */"
        pieces.append(banner)
        pieces.append(f.read_text(encoding="utf-8").rstrip())
        pieces.append("")  # blank line separator

    return "\n".join(pieces)
```

Replace the current `pieces` loop (which only iterates `required_files + optional_files`) with the above. Update the docstring to document the new behaviour — the docstring's "Current cascade" section must be updated to list:

```
      1. tokens/primitive.css     (required)
      2. tokens/semantic.css      (required)
      3. tokens/density-<X>.css   (required, where X = density param)
      4. base/fonts.css           (optional — OK if missing)
      5. components/*.css         (optional, alphabetical, Plan 3)

    Plans 4+ will extend this by adding base/reset.css, base/typography.css,
    base/global.css, chrome/*.css, print/print.css.
```

Also update the "NOT YET" note in the docstring to explicitly exclude `base/reset.css`, `base/typography.css`, `base/global.css`, `chrome/`, `print/` — these are Plan 4+.

- [ ] **Step 4: Re-run tests — expect all to pass**

```bash
python -m pytest tests/test_ds_build_helpers.py::TestCompileDesignSystemCss -v
```

Expected: all tests pass, including the 5 new ones. Total for this class: 11 tests (6 existing + 5 new).

- [ ] **Step 5: Create the real `shared/styles/components/` directory with a `.gitkeep`**

```bash
mkdir -p shared/styles/components
touch shared/styles/components/.gitkeep
```

The `.gitkeep` is a no-content placeholder so git stages the directory (git does not track empty dirs). The helper's filter `p.is_file() and p.suffix == ".css"` ignores `.gitkeep` automatically. At this point the directory has no CSS files, so the compile output is unchanged. Verify:

```bash
python scripts/build-all.py
```

Expected: both portals build OK with zero delta vs Task 0 baseline (because `components/` is empty, the helper produces the same output as before).

Programmatic verification:

```bash
python << 'PYEOF'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path("d:/tmp/plan3-baseline/manifest.json").read_text())
for name, rel in [
    ("coe", "packages/portal-coe/dist/Portal_COE_AWM.html"),
    ("ssci", "packages/portal-ssci/dist/Portal_PSCI_AWM.html"),
]:
    cur = Path(rel).read_bytes()
    cur_sha = hashlib.sha256(cur).hexdigest()
    match = "OK" if cur_sha == manifest[name]["sha256"] else "DRIFT"
    print(f"{name}: {match}  sha256={cur_sha[:16]}... (baseline {manifest[name]['sha256'][:16]}...)")
PYEOF
```

Expected: both portals OK (byte-identical to baseline). If not, the helper change introduced drift — debug before proceeding.

- [ ] **Step 6: Run full test suite for regressions**

```bash
python -m pytest tests/ -q
```

Expected: **38 tests passing** (33 from Plans 1+2, 5 new from Task 1). If the number is different, recount: the 5 new tests are the ones added in Step 1.

- [ ] **Step 7: Commit Task 1**

```bash
git add scripts/ds_build_helpers.py tests/test_ds_build_helpers.py shared/styles/components/.gitkeep
git commit -m "feat(ds): extend compile_design_system_css() to include components/*.css

scripts/ds_build_helpers.py: compile_design_system_css() now scans
shared/styles/components/ for *.css files and appends them (in
alphabetical filename order) to the cascade after base/fonts.css.
Non-CSS files and subdirectories are ignored. Missing or empty
components/ directory is a valid no-op (backwards compatible with
Plans 1 and 2).

tests/test_ds_build_helpers.py: adds 5 unit tests covering the
new behaviour — absent dir, empty dir, single file, alphabetical
ordering with 3 files, non-CSS file filtering.

shared/styles/components/: created (empty) to receive component
files from Plan 3 Tasks 2-12.

Both portal dist HTMLs remain byte-identical to the Plan 2 baseline
because components/ is empty at this point.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 2: Migrate the button component

**Files:**
- Create: `shared/styles/components/button.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html` (remove migrated rules from block 1)

**Component scope:** all `.btn-*` variant classes currently in block 1 — `.btn-print-card`, `.btn-print-card:hover`, `.btn-export`, `.btn-export:hover`, `.btn-clear`, `.btn-clear:hover`, `.btn-export-all`, `.btn-export-all:hover`, `.btn-timeline`, `.btn-start`, `.btn-start:hover`, `.btn-stop`, `.btn-stop:hover`, `.btn-reset`, `.btn-reset:hover`, `.btn-uf-print`, `.btn-uf-export`, `.btn-uf-clear`, `.btn-print-single`, `.btn-print-pack`. The `@media print` hide rule (`.btn, button, .timer-display, ...`) is **NOT** migrated — it lives in the print stylesheet which is Plan 4 scope. It can stay in block 1 for Plan 3.

Also introduce a new `.btn` base class and semantic modifier variants (`.btn--primary`, `.btn--secondary`, `.btn--danger`, `.btn--success`, `.btn--ghost`) per spec §5.1 so future HTML can adopt the new pattern without breaking existing markup.

- [ ] **Step 1: Read the existing button CSS from block 1**

Use grep to locate and Read the specific lines (roughly 567..696 and 2091..2156 in the consolidated block) to capture the verbatim legacy CSS for all `.btn-*` variants. Copy these rules to a working buffer for the next step.

- [ ] **Step 2: Write `shared/styles/components/button.css`**

Create the file with the following structure (structure is prescriptive; exact values inherited verbatim from legacy rules found in Step 1, only the `color:` / `background:` / `var(--dark-blue)` etc. are re-tokenised):

```css
/* =========================================================================
 * Design System SGA — Component: Button (Plan 3 Task 2)
 * =========================================================================
 * Introduces .btn base class + semantic modifier variants AND re-tokenises
 * every legacy .btn-* variant class that existed in the COE consolidated
 * block 1 (Plan 2). Selector names of legacy variants are preserved verbatim
 * so existing HTML markup continues to work without modification.
 *
 * Spec: §5.1 (Tier 1 core primitives), §3 (Foundation tokens).
 * =========================================================================
 */

/* ---------- Base .btn class (new in Plan 3) ---------- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--ds-space-2);
  min-height: var(--ds-input-height);
  padding: var(--ds-space-3) var(--ds-space-5);
  border: 1px solid transparent;
  border-radius: var(--ds-radius-md);
  background: var(--ds-neutral-surface);
  color: var(--ds-neutral-fg);
  font-family: inherit;
  font-size: var(--ds-text-base);
  font-weight: 500;
  line-height: 1;
  cursor: pointer;
  transition: background-color var(--ds-transition-fast),
              border-color var(--ds-transition-fast),
              color var(--ds-transition-fast);
}

.btn:focus-visible {
  outline: 2px solid var(--ds-brand-secondary-text);
  outline-offset: 2px;
}

.btn:disabled,
.btn[aria-disabled="true"] {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ---------- Semantic modifier variants ---------- */
.btn--primary {
  background: var(--ds-brand-primary);
  color: var(--ds-neutral-surface);
  border-color: var(--ds-brand-primary);
}
.btn--primary:hover:not(:disabled) {
  background: var(--ds-brand-primary-hover);
  border-color: var(--ds-brand-primary-hover);
}

.btn--secondary {
  background: var(--ds-brand-secondary-fill);
  color: var(--ds-neutral-surface);
  border-color: var(--ds-brand-secondary-fill);
}
.btn--secondary:hover:not(:disabled) {
  background: var(--ds-brand-primary);
  border-color: var(--ds-brand-primary);
}

.btn--danger {
  background: var(--ds-status-alert-emphasis);
  color: var(--ds-status-alert-on-emphasis);
  border-color: var(--ds-status-alert-emphasis);
}
.btn--danger:hover:not(:disabled) {
  background: var(--ds-status-emergency-emphasis);
}

.btn--success {
  background: var(--ds-status-success-emphasis);
  color: var(--ds-status-success-on-emphasis);
  border-color: var(--ds-status-success-emphasis);
}
.btn--success:hover:not(:disabled) {
  filter: brightness(0.92);
}

.btn--ghost {
  background: transparent;
  color: var(--ds-brand-primary);
  border-color: transparent;
}
.btn--ghost:hover:not(:disabled) {
  background: var(--ds-neutral-subtle);
}

/* ---------- Legacy variant classes (re-tokenised verbatim) ---------- */
.btn-print-card {
  background-color: var(--ds-brand-secondary-fill);
  color: var(--ds-neutral-surface);
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}
.btn-print-card:hover { background-color: var(--ds-brand-primary); }

.btn-export {
  background-color: var(--ds-status-success-emphasis);
  color: var(--ds-neutral-surface);
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}
.btn-export:hover { background-color: var(--ds-status-success-border); }

.btn-clear {
  background-color: var(--ds-neutral-fg-subtle);
  color: var(--ds-neutral-surface);
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}
.btn-clear:hover { background-color: var(--ds-neutral-fg-muted); }

.btn-export-all {
  background-color: var(--ds-brand-primary);
  color: var(--ds-neutral-surface);
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 1.5rem;
  transition: background-color 0.3s;
}
.btn-export-all:hover { background-color: var(--ds-brand-secondary-fill); }

/* Timeline / cronómetro buttons (keep the exact legacy look) */
.btn-timeline { /* copy verbatim from block 1 legacy lines ~676 but replace
                   var(--dark-blue) / var(--medium-blue) / var(--success-green)
                   with --ds-brand-primary / --ds-brand-secondary-fill /
                   --ds-status-success-emphasis */ }
.btn-start  { background-color: var(--ds-status-success-emphasis); color: var(--ds-neutral-surface); }
.btn-start:hover { background-color: var(--ds-status-success-border); }
.btn-stop   { background-color: var(--ds-status-alert-emphasis); color: var(--ds-neutral-surface); }
.btn-stop:hover  { background-color: var(--ds-status-emergency-emphasis); }
.btn-reset  { background-color: var(--ds-neutral-fg-subtle); color: var(--ds-neutral-surface); }
.btn-reset:hover { background-color: var(--ds-neutral-fg-muted); }

.btn-uf-print  { background: var(--ds-brand-secondary-fill); color: var(--ds-neutral-surface); }
.btn-uf-export { background: var(--ds-status-success-emphasis); color: var(--ds-neutral-surface); }
.btn-uf-clear  { background: var(--ds-neutral-fg-subtle); color: var(--ds-neutral-surface); }

.btn-print-single { background: var(--ds-brand-secondary-fill); color: var(--ds-neutral-surface); }
.btn-print-pack   { background: var(--ds-brand-primary); color: var(--ds-neutral-surface); }
```

**Critical note for the executor:** the placeholders above (`/* copy verbatim from block 1 ... */`) exist because I could not exhaustively read every property of every legacy rule without inflating this plan. The executor MUST use Read or grep to fetch the verbatim legacy properties from block 1 line ranges (~676..696, 2091..2093, 2152..2153), then translate `var(--dark-blue)` → `var(--ds-brand-primary)`, `var(--medium-blue)` → `var(--ds-brand-secondary-fill)`, `var(--success-green)` → `var(--ds-status-success-emphasis)`, `var(--warning-red)` → `var(--ds-status-alert-emphasis)`, and any hard-coded hex like `#1b5e20` / `#b71c1c` / `#666` / `#999` verbatim (they already map to `--ds-status-success-border` / `--ds-status-emergency-emphasis` / `--ds-neutral-fg-muted` / `--ds-neutral-fg-subtle` approximately — use the exact DS token if available in `shared/styles/tokens/semantic.css`, otherwise preserve the hex and flag it for Plan 6 cleanup with a `/* TODO(ds): tokenise */` comment).

- [ ] **Step 3: Remove the migrated legacy rules from block 1**

Using the Edit tool on `packages/portal-coe/src/Portal_COE_AWM.source.html`:

For each legacy rule just moved to `components/button.css`, find it in block 1 and DELETE it. Use specific context (the full rule including preceding whitespace and trailing `}`) as the `old_string`, and replace with empty string. Do NOT leave comment stubs — the source should simply no longer contain the rule. After all button rules are removed, insert a single HTML comment marker immediately before the `/* Timeline / Cronómetro Styles */` section that read:

```css
/* ---------- Button component migrated to shared/styles/components/button.css (Plan 3 Task 2) ---------- */
```

as a single-line CSS comment. This is a trail marker, not a stub.

- [ ] **Step 4: Build and verify**

```bash
python scripts/build-all.py
```

Expected: both portals build OK.

**Critical note on SSCI byte identity:** once Task 2 lands `button.css` under `shared/styles/components/`, **both** portal builds will pick it up via `compile_design_system_css()`. This means the SSCI dist HTML is NO LONGER byte-identical to the Task 0 baseline starting at Task 2 — it grows by the size of `button.css` (~3 kB). This is **expected and desired**: the SSCI portal inherits the DS components for free. SSCI visual rendering MUST remain unchanged (no HTML in SSCI references `.btn`/`.btn--primary`/`.btn-export` classes until Plan 5 migration), but the byte delta is not a regression.

Verification:

```bash
python << 'PYEOF'
import json
from pathlib import Path
m = json.loads(Path("d:/tmp/plan3-baseline/manifest.json").read_text())

coe_cur_size = Path("packages/portal-coe/dist/Portal_COE_AWM.html").stat().st_size
ssci_cur_size = Path("packages/portal-ssci/dist/Portal_PSCI_AWM.html").stat().st_size
coe_delta = coe_cur_size - m["coe"]["size"]
ssci_delta = ssci_cur_size - m["ssci"]["size"]
print(f"COE  delta: {coe_delta:+,} bytes (expected near zero — button CSS moved, not added)")
print(f"SSCI delta: {ssci_delta:+,} bytes (expected +2000..+5000 — DS components now propagate to SSCI)")

# COE: legacy button rules removed from block 1, new tokenised rules added to DS.
# Delta is near zero modulo banner/boilerplate overhead.
assert -5000 < coe_delta < 5000, f"COE delta too large: {coe_delta}"
# SSCI: pure addition of DS component CSS. Growing is expected.
assert 0 < ssci_delta < 10000, f"SSCI delta outside expected growth range: {ssci_delta}"
print("OK")
PYEOF
```

Expected: both deltas within their expected ranges.

- [ ] **Step 5: Run pytest and `verify_consolidation.py` as diagnostics**

```bash
python -m pytest tests/ -q
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan3-baseline-source/portal-coe.source.html \
  --block-indices 1 \
  --consolidated-index 1
```

Expected: pytest passes. `verify_consolidation.py` will **FAIL** (current block 1 is now shorter than the baseline block 1 by ~1500 chars — the removed button rules). Read the failure output carefully — the diff must show ONLY the removed button rules, nothing else. If it shows an unrelated change (e.g., a random hex value shifted somewhere), abort and investigate. Note: `--block-indices 1` is correct — the Plan 3 baseline already has block 1 consolidated by Plan 2, so we compare block-to-block directly.

- [ ] **Step 6: Visual smoke test**

Open `packages/portal-coe/dist/Portal_COE_AWM.html` and `d:/tmp/plan3-baseline/coe.html` side-by-side in Chrome. Navigate to:
1. Dashboard → check print buttons on dashboard cards
2. Verif Mensal → check print-single, print-pack, export buttons
3. Timeline → check start/stop/reset buttons
4. Configurações / export — check export-all button

For each: no visual difference should be perceptible. Focus ring on tab-through is allowed to differ slightly (new `outline` rule on `.btn:focus-visible` is a visual **addition**, not a regression). If any button looks wrong (wrong colour, different padding, layout shift), STOP and fix before committing.

- [ ] **Step 7: Commit Task 2**

```bash
git add shared/styles/components/button.css packages/portal-coe/src/Portal_COE_AWM.source.html
git commit -m "feat(ds): migrate button component to shared/styles/components/button.css

Extracts all .btn-* variant classes from the COE consolidated legacy
block 1 into a new file shared/styles/components/button.css. The
legacy variant class names (.btn-print-card, .btn-export, .btn-clear,
.btn-export-all, .btn-timeline, .btn-start/stop/reset, .btn-uf-*,
.btn-print-single/pack) are preserved verbatim so existing HTML markup
in the COE source continues to work without modification. Legacy CSS
token references (--dark-blue, --medium-blue, --success-green, etc.)
are re-mapped to DS semantic tokens (--ds-brand-primary,
--ds-brand-secondary-fill, --ds-status-success-emphasis, etc.).

Additionally introduces a new .btn base class and semantic modifier
variants (.btn--primary, .btn--secondary, .btn--danger, .btn--success,
.btn--ghost) per spec §5.1 so future HTML can adopt the modern pattern
without touching the legacy variant classes.

Visual equivalence verified against Plan 3 Task 0 baseline in Chrome:
buttons in Dashboard, Verif Mensal, Timeline, and Configurações all
render identically. Focus ring is new (visual addition, not regression).

SSCI dist remains byte-identical to baseline — Plan 3 touches COE only.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 3: Migrate the badge component (including `.cr-chip`)

**Files:**
- Create: `shared/styles/components/badge.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope:** `.cr-chip`, `.cr-chip b`, `.cr-chips` (the flex wrapper). Additionally, the new file introduces a `.badge` base class + status variants (`.badge--info`, `.badge--success`, `.badge--warning`, `.badge--alert`, `.badge--emergency`) + category variants (`.badge--cat-avsec`, `.badge--cat-sga`, `.badge--cat-enna`, `.badge--cat-seg-ordem`, `.badge--cat-ext-emg`, `.badge--cat-operadores`) per spec §5.1 and §3.2 category table.

- [ ] **Step 1: Read `.cr-chip*` rules from block 1** (roughly lines 951..953 in the original block, but since block 1 was consolidated by Plan 2, use grep to find the real positions).

- [ ] **Step 2: Create `shared/styles/components/badge.css`**

Write `.badge` base + variants + the re-tokenised `.cr-chip*` rules. Use `var(--ds-radius-pill)`, `var(--ds-text-xs)`, `var(--ds-space-1)`, `var(--ds-space-3)` for the base. Preserve `.cr-chip` class name and its exact padding/font-size values (`0.15rem 0.5rem`, `0.72rem`) verbatim so the fichas-seg contact chips render identically.

- [ ] **Step 3: Remove `.cr-chip*` rules from block 1** and add a CSS comment marker `/* ---------- Badge component migrated to shared/styles/components/badge.css (Plan 3 Task 3) ---------- */`.

- [ ] **Step 4: Build, run pytest, verify SSCI unchanged, run `verify_consolidation.py`** (expected failure showing only the removed chip rules).

- [ ] **Step 5: Visual smoke test**

Navigate to Contactos → a ficha → check the `.cr-chip` labels inside contact fichas. They must render identically: same light-grey background, same 1px border, same size. Dashboard cr-chips in fichas PDF preview also checked.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(ds): migrate badge component (.cr-chip + new .badge variants)

Creates shared/styles/components/badge.css with:
- .cr-chip, .cr-chip b, .cr-chips — re-tokenised from block 1, class
  names preserved verbatim (referenced in PATCH v18 JS at lines 14733+
  which query document.querySelectorAll('.cr-chip[data-awm-contact]'))
- .badge base class + status variants (info/success/warning/alert/
  emergency) + 6 category variants per spec §5.1 and §3.2

Legacy .cr-chip rules removed from COE consolidated block 1. Visual
equivalence verified against Plan 3 Task 0 baseline in Contactos and
fichas PDF preview.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 4: Migrate the form-group + input + select + textarea component (bundled with checkbox/radio scaffolding)

**Files:**
- Create: `shared/styles/components/form-group.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope (migration from legacy):** `.form-group`, `.form-group label`, `.form-group input`, `.form-group textarea`, `.form-group select`, `.form-group input:focus`, `.form-group textarea:focus`, `.form-group select:focus`, `.form-group textarea` (resize), `.form-full-width`, `.form-actions`. One commit bundles them because they are a tightly-coupled form composition.

**Component scope (new scaffolding, bundled in the same file per user brief):** checkbox and radio styling. The COE legacy source has NO `.checkbox`/`.radio`/`input[type=checkbox]`/`input[type=radio]` custom styling — native widgets are used everywhere. Task 4 adds fresh `.checkbox`, `.checkbox__input`, `.checkbox__label`, `.radio`, `.radio__input`, `.radio__label` rules per spec §5.1, using `--ds-brand-primary` for checked state, `--ds-neutral-muted` for unchecked border, and the standard focus ring. These are cold CSS — no legacy removal, no visual effect on existing forms which continue to use native `<input type=checkbox>` without custom classes. Note: spec §6.1 proposes separate `checkbox-radio.css` file; the user brief bundles it into the form-group migration, so we follow the brief.

**Explicitly NOT in scope for this task:** `#bombaFormBlock input[type=text]`, `#bombaFormBlock textarea`, `#bombaFormBlock select`, `#emgFormBlock *` — these are domain-prefixed overrides that stay in the consolidated block. Same for `.ficha-unified-form *` rules. They continue to work because their specificity is higher than the generic `.form-group input` rules in `components/form-group.css`, so they override correctly.

- [ ] **Step 1: Read the form-group block** from ~520..565 of legacy block 1 (use grep to find real position in consolidated block 1).

- [ ] **Step 2: Create `shared/styles/components/form-group.css`** with:
  - `.form-group` container (flex column, consuming `var(--ds-space-4)` gap)
  - `.form-group label` with `color: var(--ds-brand-primary)`, `font-weight: 600`, `font-size: var(--ds-text-sm)`, `margin-bottom: var(--ds-space-2)`
  - `.form-group input`, `textarea`, `select` with `padding: var(--ds-space-3)`, `border: 1px solid var(--ds-neutral-muted)`, `border-radius: var(--ds-radius-sm)`, `font-family: inherit`, `font-size: var(--ds-text-base)`, `transition: border-color var(--ds-transition-fast)`
  - `:focus` variants with `border-color: var(--ds-brand-secondary-fill)`, `outline: 2px solid var(--ds-brand-secondary-text)`, `outline-offset: 2px` (new — replaces the legacy `box-shadow` focus ring for a11y)
  - `.form-group textarea { resize: vertical; min-height: 80px; }`
  - `.form-full-width { grid-column: 1 / -1; }`
  - `.form-actions { display: flex; gap: var(--ds-space-4); margin-top: var(--ds-space-5); flex-wrap: wrap; }`
  - **New scaffolding (bundled):** `.checkbox`, `.checkbox__input`, `.checkbox__label`, `.checkbox input[type="checkbox"]`, `.radio`, `.radio__input`, `.radio__label`, `.radio input[type="radio"]`. Use `--ds-brand-primary` for the checked accent, `--ds-neutral-muted` for the unchecked border, `--ds-space-2` for gap between input and label. Cold CSS — no legacy to remove.

- [ ] **Step 3: Remove the migrated rules from block 1** and add a marker comment.

- [ ] **Step 4: Build, test, verify, smoke test** — exercise forms in: add contact, edit contact, edit EFB (note: EFB has its own `#emgFormBlock *` overrides that remain in block 1 and must still render the form — specifically check that `.form-group input` in an EFB context does NOT visually change, because `#emgFormBlock input[type=text]` has higher specificity).

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(ds): migrate form-group component + checkbox/radio scaffolding

Creates shared/styles/components/form-group.css. Generic
.form-group scope extracted from COE consolidated block 1 and
re-tokenised against --ds-brand-primary, --ds-brand-secondary-fill,
--ds-neutral-muted, --ds-space-*, --ds-text-*.

Bundles new checkbox and radio scaffolding (per user task brief)
inside the same file: .checkbox, .checkbox__input, .checkbox__label,
.radio, .radio__input, .radio__label. Cold CSS — the COE source
has no custom checkbox/radio styling to migrate. Spec §6.1 proposes
checkbox-radio.css as a separate file; we follow the user brief's
bundled layout to minimise file proliferation.

Domain overrides (#bombaFormBlock, #emgFormBlock, .ficha-unified-form)
remain in the consolidated block because their higher specificity is
required to preserve existing domain-specific form behaviour; those
will be re-tokenised in place by Plan 6.

Focus ring upgraded from box-shadow to outline+outline-offset per
spec §3.6 (a11y improvement, visually similar).

Part of Plan 3 (COE Component Migration)."
```

---

## Task 5: Migrate card + stat-card components

**Files:**
- Create: `shared/styles/components/card.css`
- Create: `shared/styles/components/stat-card.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope (card.css):** `.contact-card`, `.contact-card-header`, `.contact-card-header.internal`, `.contact-card-header.external`, `.contact-card-header.authority`, `.contact-card-body`, `.alarm-card-header`, `.alarm-card-header.alarm-red`, `.alarm-card-header.alarm-amber`, `.alarm-card-body` — class names preserved verbatim (JS-load-bearing in `contact-card-header` at lines 14557, 14611 and `alarm-card-*` at 3389, 3396). The new file also introduces a generic `.card` base class + `.card--with-header`, `.card--with-footer`, `.card--with-status-stripe`, `.card--interactive` modifier variants per spec §5.2.

**Component scope (stat-card.css):** **pure new scaffolding.** No legacy removal. Creates the file with `.stat-card`, `.stat-card__value`, `.stat-card__label`, `.stat-card--trend-up`, `.stat-card--trend-down` per spec §5.2 — ready for future dashboard use.

- [ ] **Step 1: Read contact-card + alarm-card CSS from block 1**
- [ ] **Step 2: Create `shared/styles/components/card.css`** with base `.card` + re-tokenised `.contact-card*` and `.alarm-card*` rules.
- [ ] **Step 3: Create `shared/styles/components/stat-card.css`** with new scaffolding only. No modification to source HTML for stat-card (zero legacy removal).
- [ ] **Step 4: Remove migrated card rules from block 1** (not stat-card) and add marker.
- [ ] **Step 5: Build, test, verify, smoke test** — exercise Contactos cards (internal/external/authority colours), alarm-card rendering on Dashboard (alarm-red, alarm-amber).
- [ ] **Step 6: Commit**

```bash
git commit -m "feat(ds): migrate card component + add stat-card scaffolding

Creates shared/styles/components/card.css with the existing legacy
contact-card and alarm-card patterns re-tokenised, plus a generic
.card base class and 4 modifier variants per spec §5.2. Class names
.contact-card*, .alarm-card* preserved verbatim for JS compatibility
(referenced in the COE source at lines 14557, 14611, 3389, 3396).

Creates shared/styles/components/stat-card.css as new scaffolding —
no legacy rules to migrate, ready for future dashboard tile use.

Visual equivalence verified in Contactos (internal/external/authority
card headers) and Dashboard (alarm-red, alarm-amber cards).

Part of Plan 3 (COE Component Migration)."
```

---

## Task 6: Migrate the table component (generic only)

**Files:**
- Create: `shared/styles/components/table.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope (generic only):** `table {}`, `th, td {}`, `th {}`, plus a new `.table` class + `.table--sticky-header`, `.table--zebra`, `.table--row-hover` variants per spec §5.2.

**Explicitly NOT in scope:** `#verif-contactos table.vc-table`, `.vc-cat-row`, `.vc-num`, `.vc-name`, `.vc-func`, `.vc-tel`, `.vc-table-wrap`, `.contacts-table`, `.timeline-log table`, and all other ID- or class-prefixed table variants. These stay in the consolidated block as domain components and are re-tokenised in place by Plan 6.

- [ ] **Step 1: Read the generic `table {}`, `th, td {}`, `th {}` rules from block 1** (these exist at roughly lines 338, 351, 357 of the original block).
- [ ] **Step 2: Create `shared/styles/components/table.css`** with `.table` base + variants + re-tokenised generic element rules.
- [ ] **Step 3: Remove generic table rules from block 1**. Preserve all domain-specific table rules verbatim.
- [ ] **Step 4: Build, test, verify, smoke test** — exercise Verif Mensal (huge table with 26 entities), Timeline log table, dashboard tables. Critical: visually scan a long table row to make sure nothing regressed.
- [ ] **Step 5: Commit**

```bash
git commit -m "feat(ds): migrate generic table component to shared/styles/components/table.css

Extracts the generic table {}, th/td, th rules from the COE
consolidated block 1 and re-tokenises them against --ds-neutral-muted,
--ds-neutral-fg, --ds-row-height, --ds-space-*. Adds a .table base
class and three modifier variants (--sticky-header, --zebra,
--row-hover) per spec §5.2.

Domain table variants (.vc-*, .contacts-table, .timeline-log table)
are left in the consolidated block — they are Plan 6 domain scope.

Visual equivalence verified in Verif Mensal (26 rows), Timeline log,
and dashboard tables.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 7: Migrate the tabs component

**Files:**
- Create: `shared/styles/components/tabs.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope:** `.tab-content {}`, `.tab-content.active {}` — the minimal surface that exists in block 1. Also introduces new `.tabs`, `.tab-list`, `.tab-btn`, `.tab-btn[aria-selected="true"]`, `.tab-btn:hover`, `.tab-panel` per spec §5.2 for future use. The legacy `.tab-content` class name is preserved verbatim (referenced at lines 4958 and 13097 in JS).

- [ ] **Step 1..5**: same pattern as previous tasks.
- [ ] **Step 6: Commit** `feat(ds): migrate tabs component to shared/styles/components/tabs.css`.

---

## Task 8: Create dropdown component (new scaffolding)

**Files:**
- Create: `shared/styles/components/dropdown.css`

**Component scope:** **pure new scaffolding** — no CSS exists in block 1 for `dropdown`/`.menu`/`menu-item`. Creates `.dropdown`, `.dropdown__trigger`, `.dropdown__menu`, `.dropdown__item`, `.dropdown__item--danger`, `.dropdown__divider`, `.dropdown__section-heading` per spec §5.2 ready for future use. No legacy removal, no source HTML modification.

- [ ] **Step 1: Create `shared/styles/components/dropdown.css`**
- [ ] **Step 2: Build** — should produce zero size delta on the COE dist (the new file adds ~1kb of CSS, but it's cold — no HTML currently references it).
- [ ] **Step 3: Commit**

```bash
git add shared/styles/components/dropdown.css
git commit -m "feat(ds): add dropdown component scaffolding (no legacy to migrate)

No dropdown or menu CSS exists in the COE consolidated block 1.
Creates shared/styles/components/dropdown.css with .dropdown,
.dropdown__trigger, .dropdown__menu, .dropdown__item (+ --danger,
--divider, --section-heading variants) per spec §5.2.

Zero source HTML changes — this is pure scaffolding for future
dropdown UI. COE dist HTML grows by ~1 kB to include the new rules.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 9: Migrate awm-modal component

**Files:**
- Create: `shared/styles/components/awm-modal.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope:** all 20+ `.awm-modal*` selectors from block 1 (verified at grep hits lines 1625..1713 + print hide rule at 2530). **Every class name MUST be preserved verbatim** — the `<script>` code creates and removes these classes dynamically and any rename will break the modal system.

**Highest risk task in Plan 3** because:
1. Modal focus trap is historically fragile.
2. ESC handling has been regression-tested multiple times.
3. Any layout shift (z-index, position fixed/absolute, overlay opacity) would be catastrophically visible.

**Risk mitigation:**
- The task is 100% re-tokenisation. No structural CSS changes. No `display`, `position`, `z-index`, `overflow`, `transform` value changes. Only colour-ish properties (`background`, `color`, `border`, `box-shadow`) are re-tokenised.
- After the task, perform extended smoke testing: open modal from at least 3 different triggers (confirm delete, warning, danger variants), close via ESC, close via cancel button, close via overlay click. Each should behave identically.

- [ ] **Step 1: Grep and Read** every `.awm-modal*` rule from block 1. Copy the block verbatim.
- [ ] **Step 2: Create `shared/styles/components/awm-modal.css`** with the verbatim rules, replacing ONLY `var(--dark-blue)` → `var(--ds-brand-primary)`, `var(--medium-blue)` → `var(--ds-brand-secondary-fill)`, and any hard-coded hex like `#0094CF`, `#f57f17`, `#d32f2f`, `#007aa8`, `#b71c1c`, `#d0d0d0` with the closest DS semantic token. Add a top-of-file banner:

```css
/* =========================================================================
 * Design System SGA — Component: awm-modal (Plan 3 Task 9)
 * =========================================================================
 * Preserves all legacy .awm-modal* class names verbatim. JS code at
 * src line 5067 and elsewhere creates these class names dynamically.
 * DO NOT rename any selector in this file.
 *
 * Re-tokenises legacy var(--dark-blue)/var(--medium-blue) and hard-coded
 * hex colour values to DS semantic tokens. Structural CSS (position,
 * z-index, transform, display, animation) is preserved verbatim.
 *
 * Spec: §5.3 (Feedback / Overlays — awm-* extends).
 * =========================================================================
 */
```

- [ ] **Step 3: Remove all `.awm-modal*` rules from block 1** (but NOT the `@media print` hide rule at line 2530 — that is chrome/print scope for Plan 4). Use Edit with specific `old_string` for each rule, or replace a single contiguous range if the rules are all adjacent.

- [ ] **Step 4: Build, test, verify**

- [ ] **Step 5: EXTENDED visual smoke test for modal (mandatory checkpoint)**

Open `dist/Portal_COE_AWM.html` in Chrome. Execute:
1. Trigger a confirm-delete modal (e.g., delete a contact from Contactos). Expected: overlay appears with correct backdrop opacity, modal is centred, title uses brand primary colour, buttons rendered in the three variants.
2. Press ESC — modal closes.
3. Re-trigger. Click the cancel button — modal closes.
4. Re-trigger. Click the overlay backdrop (outside the modal) — modal closes.
5. Re-trigger. Tab into the modal and verify focus trap (tab cycles between focusable elements inside the modal, does not escape).
6. Re-trigger a warning modal (different source — e.g., export-all without data). Verify the warning icon is amber/yellow.
7. Re-trigger a danger modal (delete-all variant). Verify the icon is red.
8. Repeat all 7 steps in Edge.

If ANY step fails, the task is blocked and must be debugged before commit.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(ds): migrate awm-modal component to shared/styles/components/awm-modal.css

Extracts all 20+ .awm-modal* selectors from the COE consolidated
block 1 into a new component file. Class names preserved verbatim
— modal JS code (src line 5067+) creates these classes dynamically
and any rename would break the modal system.

Re-tokenisation: var(--dark-blue) → var(--ds-brand-primary),
var(--medium-blue) → var(--ds-brand-secondary-fill), hard-coded hex
values mapped to closest DS semantic token where safe. Structural
CSS (position, z-index, transform, animation) preserved verbatim —
this is the highest-risk component in Plan 3 and we minimised the
delta accordingly.

Extended visual smoke test passed in Chrome AND Edge: confirm,
warning, danger variants all render identically; ESC, cancel button,
overlay click all dismiss correctly; focus trap works.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 10: Migrate awm-toast component

**Files:**
- Create: `shared/styles/components/awm-toast.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope:** all `.awm-toast*` selectors (verified lines 1529..1607). Class names preserved verbatim (JS-load-bearing).

Same pattern as Task 9 but lower risk — toasts have no focus trap and no backdrop.

- [ ] **Step 1: Grep, Read** all `.awm-toast*` rules.
- [ ] **Step 2: Create `shared/styles/components/awm-toast.css`** with verbatim rules + re-tokenisation (`#2e7d32` → `var(--ds-status-success-emphasis)`, `#f57f17` → `var(--ds-status-warning-emphasis)`, `#d32f2f` → `var(--ds-status-alert-emphasis)`, `#0094CF` → `var(--ds-brand-secondary-fill)`).
- [ ] **Step 3: Remove rules from block 1.**
- [ ] **Step 4: Build, test, verify.**
- [ ] **Step 5: Visual smoke test** — trigger a success toast (save contact OK), a warning toast (export no data), an error toast (fail backup), an info toast. Verify each has correct left-border colour and icon. Dismiss via the close button.
- [ ] **Step 6: Commit** `feat(ds): migrate awm-toast component to shared/styles/components/awm-toast.css`.

---

## Task 11: Migrate uxp-savebadge component

**Files:**
- Create: `shared/styles/components/uxp-savebadge.css`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

**Component scope:** `.uxp-savebadge`, `.uxp-savebadge.visible`, `.uxp-savebadge.saving`, `.uxp-savebadge.saved`, `.uxp-savebadge.error`, `.uxp-savebadge .dot`, `.uxp-savebadge.saving .dot`, `.uxp-savebadge.saved .dot`, `.uxp-savebadge.error .dot`, plus `@keyframes uxp-pulse`. Class name is `uxp-savebadge` (NOT `awm-save-badge` as the spec §5.3 lists — the real legacy class is `uxp-*`, verified at src line 12944 JS reference).

The file is named `uxp-savebadge.css` to match the real class name (alphabetical sort behaviour in the helper will place it after `tabs.css` and after `stat-card.css`, still determinstic and correct).

- [ ] **Step 1..4**: standard pattern.
- [ ] **Step 5: Visual smoke test** — edit a contact, click save. Save badge appears in corner with "saving" state (amber dot), transitions to "saved" state (green dot), fades out. Then force an error (e.g., block localStorage) — badge goes red.
- [ ] **Step 6: Commit**:

```bash
git commit -m "feat(ds): migrate uxp-savebadge component (note: class is uxp-*, not awm-*)

Creates shared/styles/components/uxp-savebadge.css with the .uxp-savebadge
rules and @keyframes uxp-pulse re-tokenised from COE block 1.

The spec §5.3 generically refers to this as 'awm-save-badge' but the
actual legacy class name in the COE source is .uxp-savebadge (created
by JS at src line 12944). The file is named to match the real class
name to avoid confusion; Plan 6's namespace cleanup may rename it to
.save-badge across all portals.

Visual equivalence verified: saving→saved→idle transition in Contactos
edit form, error state on localStorage failure.

Part of Plan 3 (COE Component Migration)."
```

---

## Task 12: Create skeleton + empty-state components (new scaffolding)

**Files:**
- Create: `shared/styles/components/skeleton.css`
- Create: `shared/styles/components/empty-state.css`

**Component scope:** **pure new scaffolding.** Neither component exists in block 1. Create one commit with both files.

**`skeleton.css` contents:**

```css
/* =========================================================================
 * Design System SGA — Component: Skeleton (Plan 3 Task 12)
 * =========================================================================
 * Loading placeholder. Animated shimmer. Respects prefers-reduced-motion.
 * Spec: §5.3.
 * =========================================================================
 */
.skeleton {
  display: block;
  background: var(--ds-neutral-subtle);
  border-radius: var(--ds-radius-sm);
  position: relative;
  overflow: hidden;
}
.skeleton::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.6) 50%,
    transparent 100%
  );
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}
@keyframes skeleton-shimmer {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton::after { animation: none; }
}
.skeleton--text       { height: 1em; margin-bottom: var(--ds-space-2); }
.skeleton--title      { height: 1.5em; margin-bottom: var(--ds-space-4); }
.skeleton--avatar     { width: 32px; height: 32px; border-radius: 50%; }
.skeleton--card       { height: 120px; }
```

**`empty-state.css` contents:**

```css
/* =========================================================================
 * Design System SGA — Component: Empty State (Plan 3 Task 12)
 * =========================================================================
 * Illustration + title + description + optional CTA.
 * Spec: §5.3.
 * =========================================================================
 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--ds-space-7);
  text-align: center;
  color: var(--ds-neutral-fg-muted);
}
.empty-state__illustration {
  width: 96px;
  height: 96px;
  margin-bottom: var(--ds-space-5);
  color: var(--ds-neutral-fg-subtle);
}
.empty-state__title {
  font-size: var(--ds-text-lg);
  font-weight: 600;
  color: var(--ds-neutral-fg);
  margin: 0 0 var(--ds-space-3);
}
.empty-state__description {
  font-size: var(--ds-text-sm);
  color: var(--ds-neutral-fg-muted);
  max-width: 48ch;
  margin: 0 0 var(--ds-space-5);
}
.empty-state__cta {
  /* Uses .btn from components/button.css — no duplication. */
}
```

- [ ] **Step 1: Create both files.**
- [ ] **Step 2: Build** — expected size delta +2 kB on COE dist, +2 kB on SSCI dist (both portals receive the new files via DS compilation).

  Note: by this point SSCI has already grown continuously since Task 2 (button.css) — every Plan 3 component migration propagates to the SSCI build via `compile_design_system_css()`. This is EXPECTED and desired: the SSCI portal inherits the DS components for free. The SSCI dist has NOT been byte-identical to the Plan 3 Task 0 baseline since Task 2; what it MUST be is **visually identical**, because SSCI HTML does not use any of the new classes until Plan 5 migrates it. Cold CSS in SSCI is harmless.

- [ ] **Step 3: Build, test, verify both portals still render**

Visual check: open both dist HTMLs in Chrome. They must look identical to their Task 0 baselines (no HTML uses `.skeleton` or `.empty-state` yet, so cold CSS has no visible effect).

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(ds): add skeleton + empty-state components (new scaffolding)

Creates shared/styles/components/skeleton.css and empty-state.css.
Neither component exists in the legacy COE source — pure new
scaffolding per spec §5.3.

skeleton.css: .skeleton base with shimmer animation (respects
prefers-reduced-motion), 4 shape modifier variants (text, title,
avatar, card).

empty-state.css: .empty-state centred layout with __illustration,
__title, __description, __cta slots. CTA slot consumes .btn from
components/button.css (no duplication).

Both portal dist HTMLs grow by ~2 kB (cold CSS — no HTML uses
these classes yet). Visual output unchanged in both portals.

SSCI dist has grown monotonically since Task 2 (button.css) via
compile_design_system_css() propagation; Task 12 continues that
pattern. SSCI visual rendering is unchanged (no SSCI HTML uses
Plan 3 classes — cold CSS).

Part of Plan 3 (COE Component Migration)."
```

---

## Task 13: Final integration — full verification + visual checklist + Playwright consideration

**Files:** none (verification only)

- [ ] **Step 1: Full pytest run**

```bash
python -m pytest tests/ -v
```

Expected: **38+ tests passing** (33 Plans 1+2 + 5 new from Task 1, plus any tests the executor added along the way in Tasks 2-12 — not mandatory but encouraged when a component has complex behaviour).

- [ ] **Step 2: Full build**

```bash
python scripts/build-all.py
```

Expected: both portals build OK.

- [ ] **Step 3: Count `<style>` blocks in COE source** — verify Plan 2's 8-block structure is preserved

```bash
python -c "
import re
from pathlib import Path
src = Path('packages/portal-coe/src/Portal_COE_AWM.source.html').read_text(encoding='utf-8')
blocks = re.findall(r'<style[^>]*>', src)
print(f'COE source: {len(blocks)} <style> blocks')
assert len(blocks) == 8, f'Expected 8, got {len(blocks)} — Plan 2 structure broken'
"
```

Expected: 8 blocks. If not, something got removed that should not have been.

- [ ] **Step 4: List components files**

```bash
python -c "
from pathlib import Path
p = Path('shared/styles/components')
files = sorted(f.name for f in p.iterdir() if f.suffix == '.css')
print(f'{len(files)} component files:')
for f in files: print(f'  {f}')
assert len(files) >= 13, f'Expected >=13 components, got {len(files)}'
"
```

Expected: at least 13 component files: button, badge, form-group, card, stat-card, table, tabs, dropdown, awm-modal, awm-toast, uxp-savebadge, skeleton, empty-state.

- [ ] **Step 5: SSCI visual integrity check**

Open `packages/portal-ssci/dist/Portal_PSCI_AWM.html` in Chrome. Navigate through every section. Nothing should look different from the Task 0 SSCI baseline. The DS components CSS is now injected into SSCI but SSCI HTML uses none of the new classes, so visually SSCI is unchanged. Byte size delta is expected (+~10 kB for the new components CSS).

- [ ] **Step 6: COE full-system smoke test**

Open `packages/portal-coe/dist/Portal_COE_AWM.html`. Execute the following walkthrough and tick each item:

- [ ] Dashboard loads with all cards (contact card colours, alarm-red/amber, stat tiles) rendered identically to baseline
- [ ] Ocorrência section: cronómetro buttons (start/stop/reset) work and look the same
- [ ] Contactos: fichas with `.cr-chip` render, add/edit contact form works, save badge appears and dismisses
- [ ] Verif Mensal: the 26-row table renders correctly, sticky header works, row hover works
- [ ] Fichas-seg: one-column layout preserved, chip groups correct
- [ ] Modal: confirm-delete, warning, danger variants all work, ESC closes, focus trap works
- [ ] Toast: success, warning, error, info all trigger and dismiss
- [ ] Print preview (Chrome Save-as-PDF): header/sidebar hidden, content visible

Any deviation = blocker. Fix before concluding.

- [ ] **Step 7: Playwright smoke test — DEFERRED**

A Playwright smoke test that opens the dist HTML and executes a navigation + modal open/close flow would be ideal for regression-catching in future component plans. Two reasons to defer:
1. Playwright requires Node + browser binaries → conflicts with the "offline, Python-only" pipeline requirement from the project README.
2. A single Python + Selenium smoke test would add ~300 lines of infrastructure to the test suite; disproportional for the invariant being protected.

Recommendation: Plan 5 or Plan 6 should add a minimal `python scripts/smoke_test_coe.py` that uses `playwright` (or `selenium` if already installed) to open the dist HTML and assert that the DOM contains specific known markers (e.g., `document.querySelector('.btn-export')` is clickable, modal overlay appears on trigger). Marked as "deferred to Plan 5+" explicitly — not a Plan 3 deliverable.

- [ ] **Step 8: Update VERSION (no — deferred to Plan 6)**

VERSION bump is Plan 6 scope (final release `v2.1.0-alpha.1`). Plan 3 commits land on the feature branch without a version change.

- [ ] **Step 9: Mark plan as complete**

Edit the top of this plan document and add after the status line:

```markdown
> **Status:** ✅ Completed YYYY-MM-DD (replace with today's date)
> **Commits:** see `git log feat/ds-coe-components ^main`
> **Next plan:** Plan 4 — COE Chrome Migration
```

- [ ] **Step 10: Commit the completion marker**

```bash
git add docs/superpowers/plans/2026-04-11-design-system-plan-3-coe-components.md
git commit -m "docs(ds): mark Plan 3 (COE Component Migration) as complete

All 13 tasks executed successfully:

Task 1: compile_design_system_css() extended to include
components/*.css in alphabetical cascade order, with 5 new unit tests.

Tasks 2-7: button, badge, form-group, card + stat-card, table, tabs
components migrated from COE consolidated block 1 into
shared/styles/components/*.css. Class names preserved verbatim where
JS-load-bearing.

Task 8: dropdown scaffolding added (new, no legacy removal).

Tasks 9-11: awm-modal, awm-toast, uxp-savebadge components
re-tokenised. Class names preserved verbatim — modal focus trap,
ESC handling, toast dismissal, save-badge state transitions all
verified in Chrome and Edge.

Task 12: skeleton + empty-state scaffolding added (new, no legacy).

Task 13: full integration — pytest green, both portals build,
visual smoke test clean, SSCI unchanged, COE block 1 still at 8
blocks (Plan 2 structure preserved).

Visual equivalence invariant held throughout. Byte-identity is no
longer the invariant (rules are moving, tokens are being remapped)
but verify_consolidation.py continues to serve as a regression
diagnostic for non-migrated selectors.

Plan 4 (COE Chrome Migration) is next.

Part of Plan 3 (COE Component Migration)."
```

---

## Verification Checklist (Plan 3 Definition of Done)

- [ ] `python -m pytest tests/ -v` → ≥38 passing (33 Plans 1+2 + 5 new from Task 1)
- [ ] `python scripts/build-all.py` → both portals exit 0
- [ ] `shared/styles/components/` contains at least 13 *.css files
- [ ] COE source: still 8 `<style>` blocks (Plan 2 structure preserved)
- [ ] SSCI source: still 5 `<style>` blocks, no modifications
- [ ] SSCI dist built successfully (byte size delta of +~10 kB from new DS components is expected and acceptable; visual output unchanged)
- [ ] COE dist visual smoke test passed in Chrome AND Edge: Dashboard, Ocorrência cronómetro, Contactos fichas+cards+cr-chips, Verif Mensal table, Fichas-seg, Modal (3 variants + ESC + focus trap), Toast (4 variants), Save-badge (3 states)
- [ ] `python scripts/verify_consolidation.py --source packages/portal-coe/src/Portal_COE_AWM.source.html --baseline d:/tmp/plan3-baseline-source/portal-coe.source.html --block-indices 1 --consolidated-index 1` is expected to fail (block 1 shrinking), but the diff shows ONLY the removed (migrated) rules — never any unrelated content
- [ ] `python scripts/validate_plan1_extended.py` still passes (the Plan 1 dormant foundation invariants still hold)
- [ ] `main` branch untouched at `bc11d89`+
- [ ] `feat/ds-coe-components` branch has ~13 atomic commits (one per task)

---

## Rollback Plan

- **Single component migration fails (visual regression spotted)**: `git reset --hard <prev-sha>` inside the worktree — revert to the previous atomic commit. The component file under `shared/styles/components/` is deleted and block 1 is restored. Debug in isolation.
- **awm-modal (Task 9) fails catastrophically (focus trap broken)**: this is the highest-risk task. If it fails after commit and a subsequent task is stacked on top, use `git revert <task-9-sha>` — it will restore the legacy `.awm-modal*` rules in block 1 AND delete `shared/styles/components/awm-modal.css`. Downstream tasks do not depend on awm-modal so a revert in the middle is safe.
- **`compile_design_system_css()` change (Task 1) is buggy**: `git revert <task-1-sha>` — this restores the Plan 2 helper and deletes `shared/styles/components/`. All downstream component tasks become invalid and must be re-done. Worst-case rollback — cost is 1-2 hours to re-apply downstream commits.
- **Whole-plan failure**: `git worktree remove --force ../Portal_DREA-ds-components` — `main` unaffected.
- **Visual regression discovered after merge to main**: each commit is a single component, so `git revert <specific-component-sha>` restores that component's legacy CSS to block 1 and drops the component file. History stays clean.

---

## Why visual equivalence is the right invariant (the shift from Plan 2)

Plan 2's invariant was **byte-identity** of the dist HTML modulo Plan 2 banner comments. That was the strongest possible invariant for a textual-only move: if the bytes match, no rule was dropped, reordered, or modified.

Plan 3 cannot preserve byte-identity because:

1. **Tokens are being renamed at the point of use.** `var(--dark-blue)` → `var(--ds-brand-primary)` changes the literal bytes in the source, even though both resolve to `#004C7B` at browser runtime.
2. **New rules are added (the `.btn` base class, `.badge` base class, variants, scaffolding components).** These are net-new bytes that have no pre-image in the baseline.
3. **Structural reorganisation is intentional.** Moving CSS from block 1 of the consolidated source to a new `shared/styles/components/button.css` file that is then concatenated by the helper into the `{{DS_CSS}}` section of the dist HTML produces a different byte sequence even if every rule is preserved. Banners, file paths, concatenation order, and file boundaries all change.

The correct invariant is **visual equivalence**: the portal renders the same (or better — new focus rings from `:focus-visible` are an accessibility upgrade, not a regression) when loaded in a modern browser. Verification has three layers:

1. **Token equivalence audit** — done once at plan start, recorded in the Key fact sheet above: every DS token used in the migration resolves to the same computed value as the legacy token it replaces. `--ds-brand-primary` = `#004C7B` = `--dark-blue`. `--ds-brand-secondary-fill` = `#0094CF` = `--medium-blue`. Same hex value, byte-for-byte. This means the CSS **cascades** to the same computed value as before, even though the source bytes changed.
2. **Programmatic regression diagnostics** — `verify_consolidation.py` continues to run as a regression fence for non-migrated rules. It cannot prove absence of regression (because migrated rules are expected to differ) but it can catch accidental corruption of unrelated rules.
3. **Human smoke test** — a fast walkthrough of each affected UI surface after every task. This catches layout and visual artefacts that the programmatic layer cannot (e.g., a typo that makes a padding value 0 instead of 8px — compiles, passes tests, but visually catastrophic).

The three layers together give confidence equivalent to byte-identity for the purpose of "no visible regression", with the benefit that Plan 3 can make real progress toward a modern component architecture rather than being stuck in textual-move purgatory.
