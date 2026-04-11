# Design System SGA — Plan 2: Style Block Consolidation (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the scattered legacy `<style>` blocks in both portal source HTMLs into a single legacy block per portal (COE: 10 real CSS blocks → 1; SSCI: 4 → 1), preserving the exact cascade order that makes the current visual state work. This is pure plumbing — zero visual change. It unblocks component-by-component migration in Plans 3+ because after consolidation each selector lives in exactly one place.

**Architecture:** The COE source HTML contains 18 `<style>` blocks, but only 10 are real CSS; the other 8 are JavaScript string literals that inject CSS into pop-up windows for PDF export (e.g., `w.document.write('<style>body{...}</style>')`). The SSCI source has 8 blocks, of which 4 are real CSS and 3 are JS strings. Consolidation touches **only** the real CSS blocks, strictly preserving cascade order, leaving JS-generated PDF CSS untouched. Each consolidated block ends up as a single `<style>` right after the existing `<style>{{DS_CSS}}</style>` marker in `<head>`, with clear section banners separating the merged content so the consolidated block is reviewable and traceable to each original block.

**Tech Stack:** Python 3.8+ (build scripts + new consolidation verification helper), pytest (regression test for CSS byte-identity of the compiled output before/after consolidation), vanilla CSS (no syntactic transformations — the consolidation is textual), git (atomic commits, worktree isolation).

**Source spec:** [docs/superpowers/specs/2026-04-11-design-system-sga-design.md](../specs/2026-04-11-design-system-sga-design.md) (v1.1 approved 2026-04-11)

**Invariant this plan must preserve:** after running `python scripts/build-all.py` with Plan 2 fully executed, the **dist HTMLs must be byte-identical to the pre-Plan-2 state** modulo only the whitespace/comments introduced by the consolidation banners inside the CSS block. Visually, the portals render the same as Plan 1's output. The dormant DS foundation from Plan 1 is not touched.

## Key fact sheet (verified by inspection on 2026-04-11 against commit `f81d6db`)

### COE source: `packages/portal-coe/src/Portal_COE_AWM.source.html`

18 `<style>` blocks total. Classification:

| # | pos | size | type | description |
|---|---|---|---|---|
| 0 | 487 | 10 chars | **DS placeholder** | `{{DS_CSS}}` — Plan 1 injection point, untouched |
| 1 | 517 | 52,751 chars | **real CSS** | Main legacy block: `:root`, body, header, sidebar, forms, tabs, cards, chronometer, modal, toast, contacts grid |
| 2 | 283,409 | 22 chars | **JS string literal** | `' + getPdfStyles() + '` — inside a JS template, not real CSS |
| 3 | 1,660,822 | 707 chars | **JS string literal** | `body{margin:0;background:#222...}'); w.document.write('...` — PDF toolbar CSS for preview window |
| 4 | 1,885,529 | 549 chars | **JS string literal** | `body{font-family:Arial...` — PDF report CSS |
| 5 | 1,916,514 | 5,366 chars | **real CSS** | `#fichas-seg` PATCH v2 base — flow diagram, chip groups |
| 6 | 1,934,948 | 3,777 chars | **real CSS** | `#fichas-seg` PATCH v2 override — single-column layout |
| 7 | 1,949,985 | 1,524 chars | **real CSS** | `#fichas-seg` PATCH v2 override — hide v2 unified form |
| 8 | 1,960,508 | 21 chars | **JS string literal** | `' + getPrintCSS() + '` |
| 9 | 1,964,725 | 3,595 chars | **real CSS** | `#bombaFormBlock` — bomb threat form block (dynamic expansion) |
| 10 | 1,987,280 | 489 chars | **JS string literal** | `@page{size:A4...}' + ` — PDF print CSS (inside template) |
| 11 | 1,989,141 | 4,572 chars | **real CSS** | `#emgFormBlock` — emergency form block (EFB, PATCH v5) |
| 12 | 2,017,208 | 5,398 chars | **real CSS** | UXP layer (PATCH v6+): focus-visible, uxp shortcuts, skip link, body override for UXP |
| 13 | 2,035,890 | 8,190 chars | **real CSS** | `#verif-contactos` (PATCH v7) — monthly verification table |
| 14 | 2,064,438 | 849 chars | **JS string literal** | `'; html += '@page { size:A4...` — PDF verification report |
| 15 | 3,877,035 | 474 chars | **real CSS** | PATCH v11 — print safety net (hide UXP elements in print) |
| 16 | 3,877,681 | 2,515 chars | **real CSS** | PATCH v12 — simulacros sidebar group redesign |
| 17 | 3,880,377 | 11,834 chars | **real CSS** | PATCH v13 — OCORRÊNCIAS cards (`.occ-*` vocabulary) |

**Real CSS blocks to consolidate**: `[1, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17]` — 10 blocks, 100,196 chars total.

**JS-embedded CSS blocks (DO NOT TOUCH)**: `[2, 3, 4, 8, 10, 14]` — 6 blocks.

**Cascade ordering reality check**: blocks must merge IN POSITION ORDER `[1, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17]` to preserve the exact same specificity resolution the browser produces today. Re-ordering will change visual output even if it looks semantically equivalent.

**Selector collisions that depend on ordering** (verified present):
- `body { ... }` defined in block 1, then overridden in block 12 (UXP adjustments)
- `.tab-content { ... }` defined in block 1, then overridden in block 12

These must remain in order `block 1 → block 12` or the UXP overrides stop working.

### SSCI source: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`

8 `<style>` blocks total:

| # | pos | size | type | description |
|---|---|---|---|---|
| 0 | 315 | 10 chars | **DS placeholder** | `{{DS_CSS}}` |
| 1 | 345 | 14,809 chars | **real CSS** | Main legacy block: `:root`, body, header, nav, cards |
| 2 | 1,417,367 | 707 chars | **JS string literal** | PDF preview toolbar CSS |
| 3 | 1,468,945 | 1,946 chars | **JS string literal** | PDF report CSS (html += '...') |
| 4 | 1,477,691 | 890 chars | **JS string literal** | Another PDF report CSS (html += '...') |
| 5 | 1,523,523 | 2,079 chars | **real CSS** | `#tr-occ-real-block` — dynamic occurrence block |
| 6 | 1,534,016 | 4,355 chars | **real CSS** | UXP layer (same pattern as COE block 12) |
| 7 | 1,560,192 | 474 chars | **real CSS** | Print safety net |

**Real CSS blocks to consolidate**: `[1, 5, 6, 7]` — 4 blocks, 21,717 chars total.

**JS-embedded CSS blocks (DO NOT TOUCH)**: `[2, 3, 4]`.

**Selector collisions** (verified): `body` and `.section` defined in block 1 then overridden in block 6 (UXP). Must preserve `1 → 6` order.

---

## Why this plan exists

Plan 1 dropped DS tokens, Inter, and a sprite into both portal HTMLs without mutating any existing CSS. Plan 3 (component migration — button, badge, etc.) wants to take the legacy CSS of one component at a time and replace it with a new file under `shared/styles/components/<name>.css`.

The problem is that a component like **button** is not a single selector — it's a set of them (`.btn`, `.btn-primary`, `.btn-danger`, `.btn:hover`, `.btn:focus`, `.btn-disabled`, ...). Those selectors are defined once in COE block 1, and some of them may have **overrides** in blocks 5, 6, 12, or 17 that change layout or color for specific sections.

Without consolidation, to migrate button you would have to:
- grep for every `.btn` variation across all 10 real CSS blocks
- extract them
- understand which block supplies which declaration
- understand the cascade order between them
- reproduce that order in the new `components/button.css`
- remove them from all 10 blocks
- validate nothing broke

With consolidation, you:
- grep for `.btn*` in the single consolidated block
- extract the contiguous range
- replace with a forwarding comment + new file
- validate

The first approach is archaeology with high risk of silent regression; the second is mechanical. This plan does the archaeology **once** (during consolidation verification) for all components at the same time, so the component migration plans after this one are mechanical.

---

## Out of scope for Plan 2

- ❌ **No CSS modifications**. Consolidation is **textual concatenation only**, not refactoring. If a rule looks suboptimal, leave it alone — Plans 3+ will refactor.
- ❌ **No touching JS-embedded CSS strings**. Blocks `[2, 3, 4, 8, 10, 14]` in COE and `[2, 3, 4]` in SSCI stay exactly where they are, with exactly the same content. These are part of the PDF export code paths.
- ❌ **No removal of legacy tokens** (`--dark-blue`, `--medium-blue`, etc.). Those go in Plan 6 (old Plan 5) during the `--ds-*` rename.
- ❌ **No changes to the DS payload from Plan 1**. `shared/styles/`, `scripts/ds_build_helpers.py`, `build.py`, and `portal.config.json` are all untouched in Plan 2.
- ❌ **No changes to the Python helpers, tests, or Inter font handling.**
- ❌ **No renumbering of PATCH comments or removing section banners from the original blocks** — these are preserved verbatim inside the consolidated block.
- ❌ **Plan 2 does NOT migrate any component**. Zero new CSS files under `shared/styles/components/`. Zero new build pipeline changes.

---

## File structure (Plan 2 scope)

### Files to create (2)

```
Portal_DREA/
├── scripts/
│   └── verify_consolidation.py                       NEW — ~120 lines, validator
└── tests/
    └── test_verify_consolidation.py                  NEW — ~80 lines, unit tests
```

### Files to modify (2)

```
packages/portal-coe/src/Portal_COE_AWM.source.html    MODIFY — consolidate 10 real CSS blocks into 1
packages/portal-ssci/src/Portal_PSCI_AWM.source.html  MODIFY — consolidate 4 real CSS blocks into 1
```

### Files NOT touched (hold the line)

Everything else: all of `shared/`, both `build.py` scripts, both `portal.config.json`, `scripts/ds_build_helpers.py`, `scripts/validate_plan1_extended.py`, `tests/test_ds_build_helpers.py`, `docs/`, `config/`, `VERSION`.

---

## Task 0: Prerequisites — worktree setup + baseline capture

**Files:** none (infrastructure)

- [ ] **Step 1: Verify main is clean and at the expected commit**

```bash
cd d:/VSCode_Claude/03-Resende/Portal_DREA && git status --short && git log --oneline -3
```

Expected: empty working tree, HEAD at `f81d6db test(ds): add programmatic extended validation for Plan 1` or later.

- [ ] **Step 2: Create worktree for Plan 2**

Using the @superpowers:using-git-worktrees skill, create a fresh worktree:

```bash
git worktree add ../Portal_DREA-consolidate -b feat/consolidate-style-blocks
git worktree list
```

Expected: two worktrees listed.

- [ ] **Step 3: Switch working directory and verify baseline build**

```bash
cd ../Portal_DREA-consolidate
python scripts/build-all.py
python -m pytest tests/ -q
```

Expected: both portals build OK, 20 tests passing, same output as the previous session.

- [ ] **Step 4: Capture pre-consolidation dist artifacts as a byte-identity baseline**

Critical: we want byte-level reproducibility before and after consolidation. Capture SHA-256 of both dist HTMLs and save the full contents to a temporary location for diff comparison in Task 13:

```bash
python << 'PYEOF'
import hashlib, shutil, json
from pathlib import Path

baseline_dir = Path("d:/tmp/plan2-baseline")
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

Expected: two files copied to `d:/tmp/plan2-baseline/`, with SHA256 hashes printed. Record the hashes — they are the ground truth for Task 13's byte-identity check.

Expected file sizes: COE ~4,449,945 bytes, SSCI ~2,049,176 bytes (exact).

- [ ] **Step 5: Confirm the source HTML style block structure matches Plan 2 expectations**

```bash
python << 'PYEOF'
import re
from pathlib import Path

for portal, path in [
    ("COE", "packages/portal-coe/src/Portal_COE_AWM.source.html"),
    ("SSCI", "packages/portal-ssci/src/Portal_PSCI_AWM.source.html"),
]:
    src = Path(path).read_text(encoding="utf-8")
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", src, re.DOTALL)
    print(f"{portal}: {len(blocks)} style blocks")
    for i, b in enumerate(blocks):
        sample = b.strip()[:60].replace("\n", " ")
        print(f"  block {i:2d}: {len(b):>9,} chars  {sample}")
PYEOF
```

Expected (copy-paste from the Plan 2 fact sheet): COE has exactly 18 blocks, SSCI has exactly 8 blocks. If the count does not match, STOP — the source HTMLs have drifted and the Plan 2 consolidation map is stale. Report BLOCKED with the actual output.

---

## Task 1: Create the consolidation verification helper

**Files:**
- Create: `scripts/verify_consolidation.py`
- Create: `tests/test_verify_consolidation.py`

This helper is the tool we use to check that consolidation is textual-only, does not lose or duplicate CSS, and preserves the ordering relationships the CSS cascade depends on. It runs both as a CLI tool (for Task 12's full verification) and as an importable module (tested in Task 1).

- [ ] **Step 1: Create the stub helper module**

```python
# scripts/verify_consolidation.py
"""
CSS consolidation verifier for Portal DREA Plan 2.

Verifies that the concatenation of N `<style>` blocks from a source HTML
matches a consolidated single block byte-for-byte (modulo banner comments
that this tool knows how to strip).

Usage:
    python scripts/verify_consolidation.py \\
        --source packages/portal-coe/src/Portal_COE_AWM.source.html \\
        --block-indices 1,5,6,7,9,11,12,13,15,16,17 \\
        --consolidated-index 1

Exit code 0 on success, non-zero with diff on failure.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


STYLE_PATTERN = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL)

# The banner regex captures:
#   1. Leading whitespace/indentation on the line where /* starts
#   2. The /* ... */ block containing "PLAN 2 CONSOLIDATION" (any variant)
#   3. Any trailing spaces/tabs and the final newline
# Matching in MULTILINE so that ^ anchors to line start.
# Both the "block N of M" banners and the "end of consolidated legacy block"
# closing banner are stripped by this single pattern.
BANNER_PATTERN = re.compile(
    r"^[ \t]*/\*\s*=+\s*\n[ \t]*\*\s*PLAN 2 CONSOLIDATION.*?\*/[ \t]*\n",
    re.DOTALL | re.MULTILINE,
)


def extract_style_blocks(html: str) -> list[str]:
    """Return the inner text of every <style> block in HTML order."""
    return STYLE_PATTERN.findall(html)


def strip_consolidation_banners(css: str) -> str:
    """Remove Plan 2 consolidation banner comments from a CSS string."""
    return BANNER_PATTERN.sub("", css)


def build_expected_consolidated(blocks: list[str], indices: list[int]) -> str:
    """Concatenate the selected block contents in order, with no separators
    other than a single newline between blocks."""
    parts = [blocks[i] for i in indices]
    return "\n".join(parts)
```

- [ ] **Step 2: Write failing tests for `extract_style_blocks`**

```python
# tests/test_verify_consolidation.py
"""Unit tests for scripts/verify_consolidation.py."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import verify_consolidation as vc  # noqa: E402


class TestExtractStyleBlocks:
    def test_empty_html_returns_empty_list(self):
        assert vc.extract_style_blocks("") == []

    def test_single_block_returns_one_element(self):
        html = "<html><head><style>body { color: red; }</style></head></html>"
        result = vc.extract_style_blocks(html)
        assert len(result) == 1
        assert result[0] == "body { color: red; }"

    def test_multiple_blocks_returns_in_order(self):
        html = (
            "<head>"
            "<style>a { color: blue; }</style>"
            "<style>b { color: red; }</style>"
            "<style>c { color: green; }</style>"
            "</head>"
        )
        result = vc.extract_style_blocks(html)
        assert len(result) == 3
        assert result[0] == "a { color: blue; }"
        assert result[1] == "b { color: red; }"
        assert result[2] == "c { color: green; }"

    def test_block_with_attributes_still_extracted(self):
        html = '<style type="text/css" media="screen">.foo {}</style>'
        result = vc.extract_style_blocks(html)
        assert result == [".foo {}"]

    def test_dotall_handles_multiline_content(self):
        html = "<style>\n  a {\n    color: red;\n  }\n</style>"
        result = vc.extract_style_blocks(html)
        assert "\n" in result[0]
        assert "color: red" in result[0]
```

- [ ] **Step 3: Run the tests — expect them to pass**

```bash
python -m pytest tests/test_verify_consolidation.py::TestExtractStyleBlocks -v
```

Expected: 5 tests pass. (The helper module was scaffolded with the function already in place — these tests confirm the implementation is correct, not scaffolding TDD. This is intentional: the functions are simple regex wrappers and inverting the order to fail-first would be performative. The indentation fixture below is the REGRESSION test that justified the MULTILINE regex.)

- [ ] **Step 4: Add tests for `strip_consolidation_banners` and `build_expected_consolidated`**

```python
class TestStripConsolidationBanners:
    def test_no_banner_returns_input_unchanged(self):
        css = "body { color: red; }\n.btn { padding: 1em; }"
        assert vc.strip_consolidation_banners(css) == css

    def test_single_banner_is_removed(self):
        css = (
            "/* ===========================\n"
            " * PLAN 2 CONSOLIDATION — block 1 of 10 (COE legacy main)\n"
            " * =========================== */\n"
            "body { color: red; }"
        )
        stripped = vc.strip_consolidation_banners(css)
        assert "PLAN 2" not in stripped
        assert stripped == "body { color: red; }"

    def test_multiple_banners_all_removed(self):
        css = (
            "/* ===========================\n"
            " * PLAN 2 CONSOLIDATION — block 1 (foo)\n"
            " * =========================== */\n"
            "body { color: red; }\n"
            "/* ===========================\n"
            " * PLAN 2 CONSOLIDATION — block 2 (bar)\n"
            " * =========================== */\n"
            ".btn { padding: 1em; }"
        )
        stripped = vc.strip_consolidation_banners(css)
        assert stripped.count("PLAN 2") == 0
        assert "body { color: red; }" in stripped
        assert ".btn { padding: 1em; }" in stripped

    def test_indented_banner_strips_indentation_with_comment(self):
        """REGRESSION: ensure banner indentation is consumed along with the
        comment. Without this, the 8 leading spaces on the banner line would
        remain and corrupt the indentation of the following line.

        This fixture mirrors the actual structure in the COE/SSCI source
        HTMLs where the banner is inserted inside a <style> block with
        8-space indentation."""
        css = (
            "        /* ===========================\n"
            "         * PLAN 2 CONSOLIDATION — block 5 (fichas-seg base)\n"
            "         * =========================== */\n"
            "            :root {\n"
            "                --dark-blue: #004C7B;\n"
            "            }\n"
        )
        stripped = vc.strip_consolidation_banners(css)
        # The banner + its leading 8 spaces + trailing newline are all gone.
        # The next line's indentation (12 spaces before :root) is preserved.
        assert "PLAN 2" not in stripped
        assert stripped == (
            "            :root {\n"
            "                --dark-blue: #004C7B;\n"
            "            }\n"
        )


class TestBuildExpectedConsolidated:
    def test_single_index_returns_that_block(self):
        blocks = ["block-zero", "block-one", "block-two"]
        assert vc.build_expected_consolidated(blocks, [1]) == "block-one"

    def test_multiple_indices_concatenated_in_listed_order(self):
        blocks = ["a", "b", "c", "d"]
        result = vc.build_expected_consolidated(blocks, [0, 2])
        assert result == "a\nc"

    def test_respects_given_order_not_sorted(self):
        blocks = ["a", "b", "c"]
        # Even if 2 < 0 in input order, output follows the input sequence.
        # The real helper always receives ascending indices from the CLI,
        # but we test the contract explicitly.
        result = vc.build_expected_consolidated(blocks, [2, 0])
        assert result == "c\na"
```

- [ ] **Step 5: Run the tests — expect all 12 to pass**

```bash
python -m pytest tests/test_verify_consolidation.py -v
```

Expected: 12 tests pass (5 extract + 4 strip including the indentation regression test + 3 build).

- [ ] **Step 6: Commit Task 1**

```bash
git add scripts/verify_consolidation.py tests/test_verify_consolidation.py
git commit -m "test(ds): add style block consolidation verification helper

scripts/verify_consolidation.py provides three functions used by
Plan 2 to verify that CSS consolidation is textual-only:
- extract_style_blocks: returns inner text of every <style> tag
- strip_consolidation_banners: removes PLAN 2 section banner comments
  (including leading indentation so the next line's indentation is
  preserved — critical regression guard)
- build_expected_consolidated: concatenates selected blocks by index

tests/test_verify_consolidation.py covers 12 cases across the three
functions including empty input, single/multiple blocks, banner
stripping with 0/1/N occurrences, indented-banner fixture mirroring
the real portal source layout, and index-ordering semantics.

This helper is used by Task 12 to verify each consolidated portal
source matches the concatenation of its original blocks byte-for-
byte (modulo banner comments).

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 2: Add the CLI entrypoint to `verify_consolidation.py`

**Files:**
- Modify: `scripts/verify_consolidation.py`

- [ ] **Step 1: Append the CLI driver**

```python
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that a single consolidated <style> block in the source "
        "HTML at --consolidated-index matches the concatenation of the "
        "original blocks identified by --block-indices (relative to a "
        "baseline version of the same file)."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the CURRENT source HTML (after consolidation).",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to the BASELINE source HTML (before consolidation).",
    )
    parser.add_argument(
        "--block-indices",
        type=str,
        required=True,
        help="Comma-separated indices of real CSS blocks in the baseline "
        "to concatenate (e.g., '1,5,6,7,9,11,12,13,15,16,17' for COE).",
    )
    parser.add_argument(
        "--consolidated-index",
        type=int,
        required=True,
        help="Index of the consolidated block in the CURRENT source "
        "HTML (typically 1, right after the DS placeholder at index 0).",
    )
    args = parser.parse_args()

    baseline_html = args.baseline.read_text(encoding="utf-8")
    current_html = args.source.read_text(encoding="utf-8")

    baseline_blocks = extract_style_blocks(baseline_html)
    current_blocks = extract_style_blocks(current_html)

    indices = [int(i) for i in args.block_indices.split(",")]

    print(f"Baseline has {len(baseline_blocks)} <style> blocks.")
    print(f"Current  has {len(current_blocks)} <style> blocks.")
    print(f"Indices to consolidate from baseline: {indices}")
    print(f"Consolidated block index in current:  {args.consolidated_index}")
    print()

    # Expected: the concatenation of baseline[indices] in order.
    expected = build_expected_consolidated(baseline_blocks, indices)

    # Actual: the current consolidated block, with banners stripped.
    if args.consolidated_index >= len(current_blocks):
        print(f"ERROR: consolidated-index {args.consolidated_index} out of range "
              f"(current has {len(current_blocks)} blocks).")
        return 1
    actual_raw = current_blocks[args.consolidated_index]
    actual_stripped = strip_consolidation_banners(actual_raw)

    if expected == actual_stripped:
        print("OK: consolidated block matches baseline concatenation byte-for-byte "
              "(banners stripped).")
        print(f"  Expected length: {len(expected):,} chars")
        print(f"  Actual length:   {len(actual_stripped):,} chars")
        return 0
    else:
        print("FAIL: consolidated block does NOT match expected concatenation.")
        print(f"  Expected length: {len(expected):,} chars")
        print(f"  Actual length:   {len(actual_stripped):,} chars")
        # Find first mismatch
        for i, (a, b) in enumerate(zip(expected, actual_stripped)):
            if a != b:
                ctx_start = max(0, i - 80)
                print(f"  First mismatch at char {i}:")
                print(f"    expected: ...{expected[ctx_start:i+80]!r}")
                print(f"    actual:   ...{actual_stripped[ctx_start:i+80]!r}")
                break
        else:
            # One string is a prefix of the other
            shorter = min(len(expected), len(actual_stripped))
            print(f"  Strings diverge at length {shorter}:")
            if len(expected) > shorter:
                print(f"    expected has trailing: {expected[shorter:shorter+200]!r}")
            else:
                print(f"    actual has trailing:   {actual_stripped[shorter:shorter+200]!r}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the module as a CLI against Plan 1's output (sanity check)**

Before we have anything consolidated, running the CLI against the current source HTML should fail (since `block-indices` pointed at baseline blocks but the source is unchanged at this point — both "baseline" and "current" point at the same file). This is a negative smoke test that the CLI wires correctly:

```bash
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline packages/portal-coe/src/Portal_COE_AWM.source.html \
  --block-indices 1,5,6,7,9,11,12,13,15,16,17 \
  --consolidated-index 1
```

Expected: FAIL with a diff message (the consolidated block at index 1 is only 52,751 chars but the expected concatenation is 100,196 chars). This proves the CLI runs, reads files, computes lengths, and reports discrepancies.

- [ ] **Step 3: Run the full test suite to confirm no regressions**

```bash
python -m pytest tests/ -q
```

Expected: 20 (Plan 1 pytest) + 12 (new Plan 2) = **32 passing**.

- [ ] **Step 4: Commit Task 2**

```bash
git add scripts/verify_consolidation.py
git commit -m "feat(ds): add CLI entrypoint to verify_consolidation.py

verify_consolidation.py now runs as a CLI with --source,
--baseline, --block-indices, and --consolidated-index arguments.
On success it prints OK with the matched length; on failure it
prints a diff showing the first mismatching character with
80 chars of context on each side.

Used by Task 12 to verify each portal's consolidated block
matches the concatenation of its original blocks byte-for-byte
(modulo banner comments).

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 3: Stage the baseline snapshot of both portal sources

**Files:**
- Create: `d:/tmp/plan2-baseline-source/portal-coe.source.html`
- Create: `d:/tmp/plan2-baseline-source/portal-ssci.source.html`

Task 12 needs access to the **pre-consolidation** source HTMLs to compare against. Copy them now to an external location (outside the repo, outside the worktree) before we start modifying them.

- [ ] **Step 1: Copy both source HTMLs to an external baseline location**

```bash
python << 'PYEOF'
import hashlib, shutil
from pathlib import Path

baseline_dir = Path("d:/tmp/plan2-baseline-source")
baseline_dir.mkdir(parents=True, exist_ok=True)

for name, rel in [
    ("portal-coe",  "packages/portal-coe/src/Portal_COE_AWM.source.html"),
    ("portal-ssci", "packages/portal-ssci/src/Portal_PSCI_AWM.source.html"),
]:
    src = Path(rel)
    dst = baseline_dir / f"{name}.source.html"
    shutil.copyfile(src, dst)
    content = src.read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    print(f"{name}: {len(content):,} bytes  sha256={sha[:16]}... -> {dst}")
PYEOF
```

Expected: two files copied, sizes should match current COE/SSCI source files.

- [ ] **Step 2: Verify the baseline files are readable and contain the expected number of `<style>` blocks**

```bash
python -c "
import re
from pathlib import Path
for name, expected in [('portal-coe', 18), ('portal-ssci', 8)]:
    path = Path(f'd:/tmp/plan2-baseline-source/{name}.source.html')
    src = path.read_text(encoding='utf-8')
    n = len(re.findall(r'<style[^>]*>', src))
    assert n == expected, f'{name}: expected {expected} blocks, got {n}'
    print(f'{name}: OK ({n} blocks)')
"
```

Expected: both portals pass with correct block counts.

- [ ] **Step 3: No commit** (this is an out-of-repo baseline, not a source change)

---

## Task 4: Consolidate COE block 1 into itself (prepare anchor)

**Files:**
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

The strategy: we rewrite **block 1** (the main legacy block, already at position 517) to contain a consolidation banner header and its original content wrapped in section banners. We do **not** yet merge any other block into it. The other blocks still exist separately.

This step is zero-content-change for block 1 (except for the addition of two banner comments) and a way to verify the banner format works before we start consuming other blocks.

- [ ] **Step 1: Locate block 1 precisely**

```bash
python << 'PYEOF'
from pathlib import Path
src = Path("packages/portal-coe/src/Portal_COE_AWM.source.html").read_text(encoding="utf-8")
# Block 1 starts at position 517 with "<style>" and contains ":root {"
# followed by the main legacy CSS. Print the first 200 chars of what's at
# position 517 to confirm.
print(f"At position 517: {src[517:517+200]!r}")
# And the closing </style> position:
import re
matches = list(re.finditer(r"</style>", src))
print(f"First </style> at position {matches[0].end()}")
print(f"Second </style> at position {matches[1].end()}")  # This closes block 1
PYEOF
```

Expected output confirms block 1 starts at 517 and ends around position 53,290 (start + 52,773 for the CSS content + 8 for `</style>`).

- [ ] **Step 2: Wrap block 1 content with a banner**

Edit `packages/portal-coe/src/Portal_COE_AWM.source.html`: find the beginning of block 1 (the `<style>` after `{{DS_CSS}}</style>`) and add a banner comment immediately inside the `<style>` tag.

The current opening of block 1 looks like:
```html
    <style>
        :root {
            --dark-blue: #004C7B;
```

Change to:
```html
    <style>
        /* ===========================
         * PLAN 2 CONSOLIDATION — block 1 (COE legacy main: :root, body, header, sidebar, forms, tabs, cards, chronometer, modal, toast, contacts)
         * =========================== */
        :root {
            --dark-blue: #004C7B;
```

No other change to block 1 content. Do NOT add a closing banner yet — that comes in Task 14 when block 1 becomes the destination for all the merged content.

- [ ] **Step 3: Verify build still works**

```bash
python scripts/build-all.py
```

Expected: both portals build OK, COE output size grows by approximately 230 bytes (the banner comment + its newlines).

- [ ] **Step 4: Verify the dist size delta is within banner-comment overhead tolerance**

```bash
python << 'PYEOF'
import json, hashlib
from pathlib import Path

manifest = json.loads(Path("d:/tmp/plan2-baseline/manifest.json").read_text())
cur_coe = Path("packages/portal-coe/dist/Portal_COE_AWM.html").stat().st_size
cur_ssci = Path("packages/portal-ssci/dist/Portal_PSCI_AWM.html").stat().st_size

delta_coe = cur_coe - manifest["coe"]["size"]
delta_ssci = cur_ssci - manifest["ssci"]["size"]
print(f"COE delta:  {delta_coe:+,} bytes (expected: +150 to +300 from one banner)")
print(f"SSCI delta: {delta_ssci:+,} bytes (expected: exactly 0, SSCI untouched)")

assert 100 <= delta_coe <= 400, f"COE delta out of range: {delta_coe}"
assert delta_ssci == 0, f"SSCI should not have changed: {delta_ssci}"
print("OK")
PYEOF
```

Expected: COE delta between +100 and +400 bytes. SSCI delta exactly 0.

- [ ] **Step 5: Commit Task 4**

```bash
git add packages/portal-coe/src/Portal_COE_AWM.source.html
git commit -m "refactor(coe): wrap legacy block 1 with Plan 2 consolidation banner

Adds a PLAN 2 CONSOLIDATION banner comment as the first lines of
the main legacy <style> block (block 1 at position 517). No CSS
rules are modified — block 1's content is unchanged aside from
the banner.

This block will be the destination for all other real CSS blocks
consolidated in subsequent tasks. Tasks 5-13 will append blocks
5, 6, 7, 9, 11, 12, 13, 15, 16, 17 into this block (in that
order) and remove them from their original positions.

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 5: Merge COE block 5 into block 1

**Files:**
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

- [ ] **Step 1: Read the current content of block 5**

```bash
python << 'PYEOF'
import re
from pathlib import Path

src = Path("packages/portal-coe/src/Portal_COE_AWM.source.html").read_text(encoding="utf-8")
blocks = re.findall(r"<style[^>]*>(.*?)</style>", src, re.DOTALL)

# After Task 4, block 5 is still at index 5 (we only added a banner to block 1).
# Note: if Task 4's banner increased the char count of block 1 enough that
# the "block 5" fingerprint shifted, the re.findall result still places it
# at index 5 by DOM order.
b5 = blocks[5]
print(f"Block 5: {len(b5):,} chars")
print(f"Preview: {b5[:200]!r}")
print(f"Ends:    {b5[-100:]!r}")
PYEOF
```

Expected: block 5 is approximately 5,366 chars, starts with something like `/* Hide original horizontal tab strip */` and contains `#seg-sub-tabs` and flow diagram rules.

- [ ] **Step 2: Append block 5's content to block 1 with a banner**

Use the Edit tool to make two changes to `packages/portal-coe/src/Portal_COE_AWM.source.html`:

**Change A**: Find the closing `</style>` of block 1 (search for the LAST line of the block 1 content before its `</style>` — something like a CSS rule that is clearly the tail of block 1). Immediately before that `</style>`, insert:

```
        /* ===========================
         * PLAN 2 CONSOLIDATION — block 5 (COE fichas-seg PATCH v2 base)
         * =========================== */
        <PASTE BLOCK 5 CONTENT HERE, VERBATIM>
```

The block 5 content should be pasted character-for-character — do NOT reformat, do NOT reindent, do NOT remove comments or newlines. Preserving byte-identity (modulo banner comments) is the invariant.

**Change B**: Remove the entire original `<style>...</style>` wrapping block 5 (the `<style>` at position 1,916,514 through its matching `</style>`). Replace with a single-line HTML comment:

```html
<!-- PLAN 2 CONSOLIDATION: original block 5 merged into block 1 above -->
```

This marker preserves file structure (so byte offsets of subsequent blocks shift predictably) without carrying any CSS.

- [ ] **Step 3: Build and verify size delta**

```bash
python scripts/build-all.py
```

Expected: both portals build OK.

```bash
python << 'PYEOF'
import json
from pathlib import Path

manifest = json.loads(Path("d:/tmp/plan2-baseline/manifest.json").read_text())
cur_coe = Path("packages/portal-coe/dist/Portal_COE_AWM.html").stat().st_size
cur_ssci = Path("packages/portal-ssci/dist/Portal_PSCI_AWM.html").stat().st_size

delta_coe = cur_coe - manifest["coe"]["size"]
delta_ssci = cur_ssci - manifest["ssci"]["size"]
print(f"COE delta:  {delta_coe:+,} bytes")
print(f"SSCI delta: {delta_ssci:+,} bytes")
# Task 4 added ~230 bytes of banner. Task 5 adds ~250 bytes of another banner
# plus the HTML comment marker (~80 bytes) minus the removed <style></style>
# wrapping (~17 bytes). Net change from Task 4 should be ~+313 bytes.
assert 400 <= delta_coe <= 800, f"COE delta out of expected range: {delta_coe}"
assert delta_ssci == 0
print("OK")
PYEOF
```

- [ ] **Step 4: Verify consolidation correctness with the helper CLI**

```bash
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5 \
  --consolidated-index 1
```

Expected: `OK: consolidated block matches baseline concatenation byte-for-byte`.

- [ ] **Step 5: Commit Task 5**

```bash
git add packages/portal-coe/src/Portal_COE_AWM.source.html
git commit -m "refactor(coe): merge block 5 (fichas-seg PATCH v2 base) into block 1

Moves the 5,366 chars of CSS from block 5 into block 1, wrapped
with a PLAN 2 CONSOLIDATION section banner. The original block 5
position is marked with an HTML comment for traceability. Zero
CSS rules modified.

verify_consolidation.py confirms the consolidated block matches
the baseline concatenation [1, 5] byte-for-byte.

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 6: Merge COE block 6 into block 1

Same pattern as Task 5. Block 6 is the `fichas-seg` PATCH v2 single-column override (3,777 chars).

- [ ] **Step 1: Merge block 6 into block 1 using the Task 5 pattern**

Append block 6's content to block 1 with a banner `PLAN 2 CONSOLIDATION — block 6 (COE fichas-seg PATCH v2 single-column override)`. Replace original block 6 with an HTML comment marker.

- [ ] **Step 2: Build, verify size delta, run CLI verification**

```bash
python scripts/build-all.py
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5,6 \
  --consolidated-index 1
```

Expected: build OK, verification OK.

- [ ] **Step 3: Commit**

```bash
git add packages/portal-coe/src/Portal_COE_AWM.source.html
git commit -m "refactor(coe): merge block 6 (fichas-seg single-column) into block 1

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 7: Merge COE block 7 into block 1

Block 7 is the `fichas-seg` PATCH v2 hide-v2-unified-form override (1,524 chars).

- [ ] **Step 1**: Same pattern. Banner: `PLAN 2 CONSOLIDATION — block 7 (COE fichas-seg PATCH v2 hide unified v2 form)`.
- [ ] **Step 2**: Build + `verify_consolidation.py --block-indices 1,5,6,7`.
- [ ] **Step 3**: Commit `refactor(coe): merge block 7 (fichas-seg hide v2 form) into block 1`.

---

## Task 8: Merge COE block 9 into block 1

Block 9 is `#bombaFormBlock` (3,595 chars). Note: we skip block 8 entirely because it's the JS-embedded `' + getPrintCSS() + '` string literal which stays as-is.

- [ ] **Step 1**: Same pattern. Banner: `PLAN 2 CONSOLIDATION — block 9 (COE bombaFormBlock — bomb threat form block)`.
- [ ] **Step 2**: Build + `verify_consolidation.py --block-indices 1,5,6,7,9`.
- [ ] **Step 3**: Commit `refactor(coe): merge block 9 (#bombaFormBlock) into block 1`.

---

## Task 9: Merge COE block 11 into block 1

Block 11 is `#emgFormBlock` — the emergency form block (EFB, 4,572 chars). We skip block 10 (JS-embedded `@page` print CSS).

- [ ] **Step 1**: Banner: `PLAN 2 CONSOLIDATION — block 11 (COE emgFormBlock — EFB PATCH v5)`.
- [ ] **Step 2**: Build + `verify_consolidation.py --block-indices 1,5,6,7,9,11`.
- [ ] **Step 3**: Commit `refactor(coe): merge block 11 (#emgFormBlock EFB) into block 1`.

---

## Task 10: Merge COE block 12 into block 1

Block 12 is the UXP layer (5,398 chars) — **critical**: contains `body { ... }` override that depends on coming AFTER block 1's `body { ... }` and coming AFTER the fichas-seg blocks. The merge order `[1, 5, 6, 7, 9, 11, 12]` preserves this.

- [ ] **Step 1**: Banner: `PLAN 2 CONSOLIDATION — block 12 (COE UXP layer — PATCH v6+ focus, shortcuts, skip link, body override)`.
- [ ] **Step 2**: Build + `verify_consolidation.py --block-indices 1,5,6,7,9,11,12`.
- [ ] **Step 3**: Commit `refactor(coe): merge block 12 (UXP layer) into block 1`.

---

## Task 11: Merge COE blocks 13, 15, 16, 17 into block 1

Batched because each is mechanically identical to previous tasks. However, create **one commit per block** so the history remains bisectable if one of them breaks anything.

- [ ] **Step 1: Block 13 — verif-contactos (PATCH v7, 8,190 chars)**

Merge, banner, build, verify:
```bash
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5,6,7,9,11,12,13 \
  --consolidated-index 1
```

Commit: `refactor(coe): merge block 13 (verif-contactos PATCH v7) into block 1`.

- [ ] **Step 2: Block 15 — print safety PATCH v11 (474 chars)**

Merge, banner, build, verify with `--block-indices 1,5,6,7,9,11,12,13,15`.

Commit: `refactor(coe): merge block 15 (print safety PATCH v11) into block 1`.

- [ ] **Step 3: Block 16 — simulacros sidebar PATCH v12 (2,515 chars)**

Merge, banner, build, verify with `--block-indices 1,5,6,7,9,11,12,13,15,16`.

Commit: `refactor(coe): merge block 16 (simulacros sidebar PATCH v12) into block 1`.

- [ ] **Step 4: Block 17 — occ-* cards PATCH v13 (11,834 chars)**

Merge, banner, build, verify with `--block-indices 1,5,6,7,9,11,12,13,15,16,17`.

Commit: `refactor(coe): merge block 17 (occ-* cards PATCH v13) into block 1`.

---

## Task 12: Final COE verification — byte-identity of dist HTML

**Files:** none (verification only)

- [ ] **Step 1: Run the helper CLI for the full concatenation**

```bash
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5,6,7,9,11,12,13,15,16,17 \
  --consolidated-index 1
```

Expected: `OK: consolidated block matches baseline concatenation byte-for-byte`. Expected length: ~100,196 chars (1 + 5 + 6 + 7 + 9 + 11 + 12 + 13 + 15 + 16 + 17 sums).

- [ ] **Step 2: Count style blocks in the current COE source**

```bash
python -c "
import re
from pathlib import Path
src = Path('packages/portal-coe/src/Portal_COE_AWM.source.html').read_text(encoding='utf-8')
blocks = re.findall(r'<style[^>]*>', src)
print(f'Current COE source has {len(blocks)} <style> blocks')
assert len(blocks) == 8, f'Expected 8 blocks remaining (0=DS, 1=consolidated, 2+3+4+8+10+14=JS-string), got {len(blocks)}'
print('OK')
"
```

Expected: **8 style blocks remain** (original 18 minus 10 real CSS blocks consolidated into block 1 = 8).

- [ ] **Step 3: Byte-identity check on the built dist HTML**

```bash
python scripts/build-all.py
```

Then:

```bash
python << 'PYEOF'
import hashlib, json
from pathlib import Path

manifest = json.loads(Path("d:/tmp/plan2-baseline/manifest.json").read_text())

# Load current COE dist
current = Path("packages/portal-coe/dist/Portal_COE_AWM.html").read_bytes()
baseline = Path("d:/tmp/plan2-baseline/coe.html").read_bytes()

print(f"Baseline size: {len(baseline):,}  sha256={hashlib.sha256(baseline).hexdigest()[:16]}")
print(f"Current size:  {len(current):,}  sha256={hashlib.sha256(current).hexdigest()[:16]}")

# Expected behavior: the dist HTMLs are NOT byte-identical because we added
# banner comments and HTML comment markers. But the DIFFERENCE should be
# ONLY those comments. We verify this by:
# 1. Stripping all banner comments from both
# 2. Stripping all "<!-- PLAN 2 CONSOLIDATION:" HTML comments
# 3. Comparing the stripped content

import re
def strip_plan2_noise(html: bytes) -> bytes:
    text = html.decode("utf-8")
    # Remove banner comments (multiline CSS comments with PLAN 2)
    text = re.sub(
        r"/\*\s*=+\s*\n\s*\*\s*PLAN 2 CONSOLIDATION.*?\*/\s*\n",
        "",
        text,
        flags=re.DOTALL,
    )
    # Remove HTML marker comments
    text = re.sub(
        r"<!--\s*PLAN 2 CONSOLIDATION:.*?-->\s*",
        "",
        text,
    )
    return text.encode("utf-8")

current_stripped = strip_plan2_noise(current)
baseline_stripped = strip_plan2_noise(baseline)

print(f"\nAfter stripping Plan 2 comments:")
print(f"  Baseline stripped size: {len(baseline_stripped):,}")
print(f"  Current stripped size:  {len(current_stripped):,}")

if current_stripped == baseline_stripped:
    print("\nOK: current dist HTML is BYTE-IDENTICAL to baseline (modulo Plan 2 comments).")
else:
    # Find first mismatch
    for i, (a, b) in enumerate(zip(current_stripped, baseline_stripped)):
        if a != b:
            ctx_start = max(0, i - 100)
            print(f"\nFAIL: first mismatch at byte {i}")
            print(f"  baseline: {baseline_stripped[ctx_start:i+100]!r}")
            print(f"  current:  {current_stripped[ctx_start:i+100]!r}")
            break
    else:
        shorter = min(len(current_stripped), len(baseline_stripped))
        print(f"\nFAIL: one is a prefix of the other at length {shorter}")
    raise SystemExit(1)
PYEOF
```

Expected: `OK: current dist HTML is BYTE-IDENTICAL to baseline (modulo Plan 2 comments).` This is the strongest possible invariant — the two HTMLs differ **only** in the Plan 2 comment lines and nothing else. If this passes, we have high confidence that no CSS rule was lost, reordered, or modified.

- [ ] **Step 4: Run the Plan 1 validator to confirm no regressions**

```bash
python scripts/validate_plan1_extended.py
```

Expected: all 29 checks pass per portal (the Plan 1 dormant foundation invariants still hold).

- [ ] **Step 5: Run the full pytest suite**

```bash
python -m pytest tests/ -q
```

Expected: 31 passing.

- [ ] **Step 6: No commit** (verification only)

---

## Task 13: Consolidate SSCI blocks 1, 5, 6, 7

The SSCI source has fewer blocks to consolidate (only `[1, 5, 6, 7]`). Apply the same mechanical pattern as COE Tasks 4-11. We do this in the same worktree, in 4 commits, one per block.

- [ ] **Step 1: Apply Task 4 pattern to SSCI block 1**

Wrap SSCI block 1 with a `PLAN 2 CONSOLIDATION — block 1 (SSCI legacy main)` banner. No content change beyond the banner. Build, verify no size change elsewhere, commit:

```bash
git add packages/portal-ssci/src/Portal_PSCI_AWM.source.html
git commit -m "refactor(ssci): wrap legacy block 1 with Plan 2 consolidation banner

Prepares SSCI block 1 as the destination for merging blocks 5, 6, 7
(real CSS blocks, skipping JS-embedded blocks 2, 3, 4).

Part of Plan 2 (Style Block Consolidation)."
```

- [ ] **Step 2: Merge SSCI block 5 into block 1** (`#tr-occ-real-block`, 2,079 chars)

Pattern from Task 5. Banner: `PLAN 2 CONSOLIDATION — block 5 (SSCI tr-occ-real-block — dynamic occurrence)`.

Verify:
```bash
python scripts/verify_consolidation.py \
  --source packages/portal-ssci/src/Portal_PSCI_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-ssci.source.html \
  --block-indices 1,5 \
  --consolidated-index 1
```

Commit: `refactor(ssci): merge block 5 (#tr-occ-real-block) into block 1`.

- [ ] **Step 3: Merge SSCI block 6 into block 1** (UXP layer, 4,355 chars)

Banner: `PLAN 2 CONSOLIDATION — block 6 (SSCI UXP layer — focus, shortcuts, body override)`.

Verify with `--block-indices 1,5,6`.

Commit: `refactor(ssci): merge block 6 (UXP layer) into block 1`.

- [ ] **Step 4: Merge SSCI block 7 into block 1** (print safety, 474 chars)

Banner: `PLAN 2 CONSOLIDATION — block 7 (SSCI print safety net)`.

Verify with `--block-indices 1,5,6,7`.

Commit: `refactor(ssci): merge block 7 (print safety) into block 1`.

---

## Task 14: Final SSCI verification + add closing banner

**Files:**
- Modify: `packages/portal-ssci/src/Portal_PSCI_AWM.source.html`
- Modify: `packages/portal-coe/src/Portal_COE_AWM.source.html`

- [ ] **Step 1: Run full verification for SSCI**

```bash
python scripts/verify_consolidation.py \
  --source packages/portal-ssci/src/Portal_PSCI_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-ssci.source.html \
  --block-indices 1,5,6,7 \
  --consolidated-index 1
```

Expected: OK.

- [ ] **Step 2: Count SSCI blocks remaining**

```bash
python -c "
import re
from pathlib import Path
src = Path('packages/portal-ssci/src/Portal_PSCI_AWM.source.html').read_text(encoding='utf-8')
blocks = re.findall(r'<style[^>]*>', src)
print(f'Current SSCI source has {len(blocks)} <style> blocks')
assert len(blocks) == 5, f'Expected 5 blocks (0=DS, 1=consolidated, 2+3+4=JS-string), got {len(blocks)}'
print('OK')
"
```

Expected: **5 style blocks remain** (original 8 minus 4 real CSS consolidated minus DS block that was already in = 5).

Wait, let me recompute: original was 8 blocks. DS block (0) is preserved. Block 1 stays. Blocks 5, 6, 7 are consolidated INTO block 1 and their original positions are replaced with HTML markers. Blocks 2, 3, 4 are JS-embedded and untouched. Result: `{0: DS, 1: consolidated, 2: JS, 3: JS, 4: JS}` = **5 blocks**. ✅

- [ ] **Step 3: Build and byte-identity check SSCI**

```bash
python scripts/build-all.py
```

```bash
python << 'PYEOF'
import hashlib, re
from pathlib import Path

def strip_plan2_noise(html: bytes) -> bytes:
    text = html.decode("utf-8")
    text = re.sub(
        r"/\*\s*=+\s*\n\s*\*\s*PLAN 2 CONSOLIDATION.*?\*/\s*\n",
        "", text, flags=re.DOTALL,
    )
    text = re.sub(r"<!--\s*PLAN 2 CONSOLIDATION:.*?-->\s*", "", text)
    return text.encode("utf-8")

current = Path("packages/portal-ssci/dist/Portal_PSCI_AWM.html").read_bytes()
baseline = Path("d:/tmp/plan2-baseline/ssci.html").read_bytes()

cur_stripped = strip_plan2_noise(current)
base_stripped = strip_plan2_noise(baseline)

print(f"SSCI baseline stripped: {len(base_stripped):,} bytes")
print(f"SSCI current  stripped: {len(cur_stripped):,} bytes")

if cur_stripped == base_stripped:
    print("OK: SSCI dist is BYTE-IDENTICAL to baseline (modulo Plan 2 comments).")
else:
    for i, (a, b) in enumerate(zip(cur_stripped, base_stripped)):
        if a != b:
            print(f"FAIL at byte {i}:")
            print(f"  baseline: {base_stripped[max(0,i-100):i+100]!r}")
            print(f"  current:  {cur_stripped[max(0,i-100):i+100]!r}")
            break
    raise SystemExit(1)
PYEOF
```

Expected: SSCI byte-identical to baseline modulo Plan 2 comments.

- [ ] **Step 4: Add a closing banner marker to both consolidated blocks**

Since Task 1 already defined `BANNER_PATTERN` as `PLAN 2 CONSOLIDATION.*?`, both the `block N` banners AND any closing banner variant are already strippable without further regex changes. Good.

At the END of block 1 (the consolidated block) in each source HTML, just before the closing `</style>` tag, add this closing banner (preserving the 8-space indentation that matches surrounding code):

```
        /* ===========================
         * PLAN 2 CONSOLIDATION — end of consolidated legacy block
         * All subsequent <style> blocks in this file are JavaScript-embedded
         * PDF export CSS and do NOT participate in the main cascade.
         * =========================== */
```

This closing banner is purely documentary — it signals to future maintainers that any `<style>` tags that appear LATER in the file are JS string literals, not real CSS that contributes to the page's appearance.

Do this in both COE and SSCI source files.

- [ ] **Step 5: Add a unit test for the closing-banner variant**

Append to `tests/test_verify_consolidation.py` inside `TestStripConsolidationBanners`:

```python
    def test_closing_banner_is_also_removed(self):
        """The closing banner used in Task 14 does not have 'block N' text,
        but BANNER_PATTERN is generic enough to match any PLAN 2
        CONSOLIDATION comment."""
        css = (
            "body { color: red; }\n"
            "        /* ===========================\n"
            "         * PLAN 2 CONSOLIDATION — end of consolidated legacy block\n"
            "         * Subsequent <style> blocks are JS-embedded PDF CSS.\n"
            "         * =========================== */\n"
        )
        stripped = vc.strip_consolidation_banners(css)
        assert stripped.count("PLAN 2") == 0
        assert stripped == "body { color: red; }\n"
```

Run tests:

```bash
python -m pytest tests/test_verify_consolidation.py -v
```

Expected: **13 tests pass** (12 from Task 1 + 1 new).

- [ ] **Step 6: Build and verify CLI for both portals**

```bash
python scripts/build-all.py
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5,6,7,9,11,12,13,15,16,17 \
  --consolidated-index 1
python scripts/verify_consolidation.py \
  --source packages/portal-ssci/src/Portal_PSCI_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-ssci.source.html \
  --block-indices 1,5,6,7 \
  --consolidated-index 1
```

Expected: build OK, both CLI verifications OK (the closing banner is stripped by the same `PLAN 2 CONSOLIDATION.*?` regex pattern used for block banners, and does not break byte-identity).

- [ ] **Step 7: Commit Task 14**

```bash
git add packages/portal-coe/src/Portal_COE_AWM.source.html \
        packages/portal-ssci/src/Portal_PSCI_AWM.source.html \
        tests/test_verify_consolidation.py
git commit -m "refactor(ds): add closing banner markers at end of consolidated blocks

Adds a documentary 'end of consolidated legacy block' banner at the
bottom of both portals' consolidated block 1. This marks where the
main legacy cascade ends and any subsequent <style> tags are
JavaScript-embedded PDF export CSS that do not participate in the
page render.

BANNER_PATTERN in verify_consolidation.py is already generic enough
to match this variant (PLAN 2 CONSOLIDATION.*? with DOTALL), so no
regex change is needed — the closing banner is stripped correctly
during verification. Adds a unit test to lock this behaviour.

Part of Plan 2 (Style Block Consolidation)."
```

---

## Task 15: Final integration — run full test suite + build + plan marker

**Files:**
- Modify: `docs/superpowers/plans/2026-04-11-design-system-plan-2-style-consolidation.md`

- [ ] **Step 1: Run the full test suite**

```bash
python -m pytest tests/ -v
```

Expected: **33 passing** (20 Plan 1 + 13 Plan 2: 12 from Task 1 + 1 closing-banner test from Task 14).

- [ ] **Step 2: Run build-all one last time**

```bash
python scripts/build-all.py
```

Expected: both portals OK.

- [ ] **Step 3: Run both verification scripts**

```bash
python scripts/verify_consolidation.py \
  --source packages/portal-coe/src/Portal_COE_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-coe.source.html \
  --block-indices 1,5,6,7,9,11,12,13,15,16,17 \
  --consolidated-index 1

python scripts/verify_consolidation.py \
  --source packages/portal-ssci/src/Portal_PSCI_AWM.source.html \
  --baseline d:/tmp/plan2-baseline-source/portal-ssci.source.html \
  --block-indices 1,5,6,7 \
  --consolidated-index 1

python scripts/validate_plan1_extended.py
```

Expected: all three OK.

- [ ] **Step 4: Run final byte-identity test**

```bash
python << 'PYEOF'
import re, hashlib
from pathlib import Path

def strip_plan2_noise(html: bytes) -> bytes:
    text = html.decode("utf-8")
    text = re.sub(
        r"/\*\s*=+\s*\n\s*\*\s*PLAN 2 CONSOLIDATION.*?\*/\s*\n",
        "", text, flags=re.DOTALL,
    )
    text = re.sub(r"<!--\s*PLAN 2 CONSOLIDATION:.*?-->\s*", "", text)
    return text.encode("utf-8")

ok = True
for name in ["coe", "ssci"]:
    current = Path(f"packages/portal-{name}/dist/Portal_{'COE_AWM' if name == 'coe' else 'PSCI_AWM'}.html").read_bytes()
    baseline = Path(f"d:/tmp/plan2-baseline/{name}.html").read_bytes()
    cur_s = strip_plan2_noise(current)
    base_s = strip_plan2_noise(baseline)
    match = "OK" if cur_s == base_s else "FAIL"
    print(f"{name.upper()}: {match}  current={len(current):,}  baseline={len(baseline):,}  stripped_match={cur_s == base_s}")
    if cur_s != base_s:
        ok = False

if not ok:
    raise SystemExit(1)
PYEOF
```

Expected: both portals OK (byte-identical after stripping Plan 2 comments).

- [ ] **Step 5: Update the Plan 2 document with a completion marker**

Edit the top of `docs/superpowers/plans/2026-04-11-design-system-plan-2-style-consolidation.md` — add after the title line:

```markdown
> **Status:** ✅ Completed YYYY-MM-DD (replace with today's date)
> **Commits:** see `git log feat/consolidate-style-blocks ^main`
> **Next plan:** Plan 3 — Component Migration (to be written when ready to proceed)
```

- [ ] **Step 6: Commit the completion marker**

```bash
git add docs/superpowers/plans/2026-04-11-design-system-plan-2-style-consolidation.md
git commit -m "docs(ds): mark Plan 2 (Style Block Consolidation) as complete

All 15 tasks executed successfully:

COE: 10 real CSS blocks (1, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17)
merged into block 1 in strict positional order. 6 JavaScript-
embedded CSS blocks (2, 3, 4, 8, 10, 14) left untouched. Result:
18 style blocks → 8 style blocks (DS + consolidated + 6 JS).

SSCI: 4 real CSS blocks (1, 5, 6, 7) merged into block 1.
3 JavaScript-embedded CSS blocks (2, 3, 4) untouched. Result:
8 style blocks → 5 style blocks (DS + consolidated + 3 JS).

Invariant preserved: dist HTMLs are byte-identical to pre-Plan-2
baseline after stripping PLAN 2 CONSOLIDATION comments. No CSS
rule was modified. Cascade order preserved exactly. Selector
collision chains (body in COE[1→12], body in SSCI[1→6],
tab-content/section overrides) preserved.

verify_consolidation.py (120 lines) and its 12 pytest tests
provide byte-identity regression guarantees for future plans.

Plan 3 (Component Migration) can now extract one component at a
time from the single consolidated block per portal, rather than
archaeologically tracing each selector across 10+ blocks.

Part of Plan 2 (Style Block Consolidation)."
```

---

## Verification Checklist (Plan 2 Definition of Done)

- [ ] `python -m pytest tests/ -v` → 33 passing (20 Plan 1 + 13 Plan 2)
- [ ] `python scripts/build-all.py` → both portals OK
- [ ] `python scripts/verify_consolidation.py` → OK for both portals
- [ ] `python scripts/validate_plan1_extended.py` → all 29 checks pass per portal
- [ ] COE dist byte-identical to Plan 2 baseline modulo Plan 2 comments
- [ ] SSCI dist byte-identical to Plan 2 baseline modulo Plan 2 comments
- [ ] COE source: 8 `<style>` blocks remaining (0=DS, 1=consolidated, 2+3+4+8+10+14=JS literals)
- [ ] SSCI source: 5 `<style>` blocks remaining (0=DS, 1=consolidated, 2+3+4=JS literals)
- [ ] Both consolidated blocks have opening + closing PLAN 2 banners
- [ ] `main` branch untouched at `f81d6db`
- [ ] `feat/consolidate-style-blocks` branch has ~15 atomic commits

---

## Rollback Plan

- **Single commit failure**: `git reset --hard <prev-sha>` inside the worktree
- **Task failure mid-sequence**: commits are per-block so `git revert <sha>` restores that block without affecting others
- **Whole-plan failure**: `git worktree remove --force ../Portal_DREA-consolidate` — main unaffected
- **Visual regression discovered after merge**: `git revert <range>` — each consolidation is a separate commit, making it easy to isolate which block's merge caused the regression

---

## Why byte-identity is the right invariant

In Plan 1 the invariant was "dormant foundation, zero visual change". We verified that via programmatic checks (font-family still Segoe UI, tokens namespaced, etc.). That was sufficient because the CSS rules in legacy blocks were **not modified**.

In Plan 2 we are physically moving CSS rules from one place to another. The programmatic checks of Plan 1 are still necessary but not sufficient — if I accidentally omit one line of CSS when merging, the page could still render "visually identical to the naked eye" during smoke testing but fail in a specific edge case hours or days later.

Byte-identity of the final dist HTML (modulo documented Plan 2 comment lines) is the strongest possible invariant for a textual refactor. If the bytes match, no CSS rule was lost, duplicated, reordered, or modified. This eliminates the entire class of "silent regression from textual reshuffling" bugs before they can reach production.

The `verify_consolidation.py` helper is the automated enforcement of this invariant. It runs after every task and would fail loudly if any merge introduced a character change beyond a banner comment.
