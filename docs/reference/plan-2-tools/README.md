# Plan 2 Tools — Archived Reference

These two files supported the Portal DREA Design System SGA
migration **Plan 2: Style Block Consolidation** (2026-04-11).

## What they do

- `verify_consolidation.py` — CLI + library for verifying that a
  single consolidated `<style>` block in a source HTML is byte-
  identical (modulo banner comments) to the concatenation of the
  original N blocks it replaces.
- `test_verify_consolidation.py` — pytest unit tests for the above.

## Why they are archived, not deleted

Plan 2 was a byte-level operation on ~100 KB of CSS across 11
blocks of the COE source and 4 blocks of the SSCI. If a future
regression ever forces a re-consolidation (or a similar textual
equivalence check), having these tools in-repo saves hours of
rebuild. The cost is zero (~12 KB of text).

## Why they are not in `scripts/` or `tests/`

- `scripts/verify_consolidation.py` referenced paths that no
  longer exist after Plans 3-4 removed the legacy CSS block. It
  cannot be run against the current source HTMLs meaningfully.
- `tests/test_verify_consolidation.py` imports the script above;
  pytest would try to collect it and fail.

Moving both into `docs/reference/plan-2-tools/` prevents pytest
collection and signals clearly that these are historical.

## Historical context

See `docs/superpowers/plans/2026-04-11-design-system-plan-2-style-consolidation.md`
for the full operational context.
