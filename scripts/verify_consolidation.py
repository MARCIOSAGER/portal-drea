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
