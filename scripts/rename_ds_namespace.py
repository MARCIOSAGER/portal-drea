"""
Plan 6 Task 2 — Global --ds-* → --* rename.

Replaces every occurrence of `--ds-NAME` with `--NAME` across a
configurable set of files. Preserves legacy variables that happen
to contain 'ds' in their name (e.g., `--dark-blue` stays
unchanged because the match is anchored to `--ds-`).

Matches:
  --ds-blue-800     → --blue-800
  var(--ds-brand-primary)  → var(--brand-primary)
  var(--ds-foo, #fff)      → var(--foo, #fff)

Does NOT match:
  --dark-blue       (not prefixed with ds-)
  --disabled        (not prefixed with ds-)
  "--ds-" in prose  (comments intentionally kept)

Usage:
  python scripts/rename_ds_namespace.py --dry-run <file> [<file> ...]
  python scripts/rename_ds_namespace.py --write <file> [<file> ...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Match --ds-<name> where <name> is [a-z0-9-]+ (one or more).
# Anchored so --ds-foo is replaced with --foo but --dsfoo (no hyphen)
# and --dark-blue are NOT matched.
PATTERN = re.compile(r"--ds-([a-z0-9][a-z0-9-]*)")


def rename_in_text(text: str) -> tuple[str, int]:
    """Return (new_text, count_replaced)."""
    count = 0

    def sub(m):
        nonlocal count
        count += 1
        return "--" + m.group(1)

    new_text = PATTERN.sub(sub, text)
    return new_text, count


def process_file(path: Path, write: bool) -> int:
    """Read file, rename, optionally write back. Return count of replacements."""
    original = path.read_text(encoding="utf-8")
    new, count = rename_in_text(original)
    if count == 0:
        return 0
    if write:
        path.write_text(new, encoding="utf-8")
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report counts without writing")
    ap.add_argument("--write", action="store_true", help="Write changes to disk")
    ap.add_argument("files", nargs="+", type=Path, help="Files to process")
    args = ap.parse_args()

    if args.dry_run and args.write:
        print("Cannot combine --dry-run and --write", file=sys.stderr)
        return 2
    if not args.dry_run and not args.write:
        print("Must specify --dry-run or --write", file=sys.stderr)
        return 2

    total = 0
    for f in args.files:
        if not f.exists():
            print(f"SKIP (not found): {f}")
            continue
        n = process_file(f, args.write)
        total += n
        mode = "would replace" if args.dry_run else "replaced"
        print(f"{mode} {n:>6} in {f}")
    print(f"Total: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
