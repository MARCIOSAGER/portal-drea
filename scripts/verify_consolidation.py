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
# Both the "block N" banners and the "end of consolidated legacy block"
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
