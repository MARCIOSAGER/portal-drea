"""
Extended validation for Plan 1 dormant foundation.
Programmatic checks spanning Level 3 (cross-browser parse), Level 4 (print),
and Level 5 (WCAG tokens / font / data URI).

Critical: most checks compare AGAINST the baseline HTMLs on `main`, so
pre-existing quirks (e.g., an off-by-one brace in the COE legacy CSS that
has been there since v1.x) do not generate false positives — only actual
regressions introduced by Plan 1 fail.

Local validation helper — not part of the project build pipeline.
"""
import base64
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

WORKTREE = Path("d:/VSCode_Claude/03-Resende/Portal_DREA-ds")
MAIN_TREE = Path("d:/VSCode_Claude/03-Resende/Portal_DREA")

PORTALS = [
    (
        "COE",
        "packages/portal-coe/dist/Portal_COE_AWM.html",
        {"expected_scripts": 18, "body_font_has": "Segoe UI"},
    ),
    (
        "SSCI",
        "packages/portal-ssci/dist/Portal_PSCI_AWM.html",
        {"expected_scripts": 7, "body_font_has": "Segoe UI"},
    ),
]

ALL_OK = True


def check(label, ok, detail=""):
    global ALL_OK
    tag = "OK  " if ok else "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"  [{tag}] {label}{suffix}")
    if not ok:
        ALL_OK = False


class CollectingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tags_opened = 0
        self.style_blocks = 0
        self.svg_blocks = 0
        self.script_blocks = 0

    def error(self, msg):
        self.errors.append(msg)

    def handle_starttag(self, tag, attrs):
        self.tags_opened += 1
        if tag == "style":
            self.style_blocks += 1
        if tag == "svg":
            self.svg_blocks += 1
        if tag == "script":
            self.script_blocks += 1


def parse_stats(html: str):
    p = CollectingParser()
    try:
        p.feed(html)
        return p, None
    except Exception as e:
        return p, e


def style_blocks(html: str):
    return re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)


def count_braces_total(blocks):
    return sum(b.count("{") for b in blocks), sum(b.count("}") for b in blocks)


def count_print_rules(blocks):
    total = 0
    for b in blocks:
        total += len(re.findall(r"@media\s+print\s*\{", b))
    return total


def strip_css_comments(css: str) -> str:
    """Remove /* ... */ comments from a CSS blob before running regex checks.

    Without this, the namespace-explanation comment in primitive.css that
    references legacy '--dark-blue'/'--medium-blue' would generate false
    positives in the DS-block-purity check."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def aggregate_vars(blocks, prefix=None, strip_comments=True):
    """Collect all --* variable DECLARATIONS across blocks.

    Only matches variable definitions (followed by `:`), not usages inside
    var() or text in comments. Optionally filtered by prefix."""
    out = set()
    for b in blocks:
        content = strip_css_comments(b) if strip_comments else b
        # Match variable declarations: --name: ...
        for v in re.findall(r"(--[a-z][a-z0-9-]+)\s*:", content):
            if prefix is None or v.startswith(prefix):
                out.add(v)
    return out


for name, rel_path, expected in PORTALS:
    print(f"\n=== {name} ===")
    worktree_path = WORKTREE / rel_path
    main_path = MAIN_TREE / rel_path

    cur = worktree_path.read_bytes().decode("utf-8")
    base = main_path.read_bytes().decode("utf-8")

    # -----------------------------------------------------------------
    # LEVEL 3 — Cross-browser parse sanity
    # -----------------------------------------------------------------
    print("\nLevel 3 — parse sanity:")

    cur_stats, cur_err = parse_stats(cur)
    base_stats, base_err = parse_stats(base)

    check(
        "HTML parses without error (current)",
        cur_err is None and len(cur_stats.errors) == 0,
        f"{cur_stats.tags_opened:,} tags, {cur_stats.style_blocks} style, {cur_stats.svg_blocks} svg, {cur_stats.script_blocks} script",
    )
    check(
        "HTML parses without error (baseline)",
        base_err is None and len(base_stats.errors) == 0,
        f"{base_stats.tags_opened:,} tags, {base_stats.style_blocks} style, {base_stats.svg_blocks} svg, {base_stats.script_blocks} script",
    )

    # Delta counts: DS must add exactly 1 <style> block and 1 <svg> block
    delta_style = cur_stats.style_blocks - base_stats.style_blocks
    delta_svg = cur_stats.svg_blocks - base_stats.svg_blocks
    delta_scripts = cur_stats.script_blocks - base_stats.script_blocks
    check("exactly +1 <style> block vs baseline (DS CSS)", delta_style == 1, f"delta={delta_style}")
    check("exactly +1 <svg> block vs baseline (icon sprite)", delta_svg == 1, f"delta={delta_svg}")
    check("script block count unchanged", delta_scripts == 0, f"delta={delta_scripts}")

    # DOCTYPE, lang, data-density attribute
    check("starts with DOCTYPE html", cur.lstrip().lower().startswith("<!doctype html"))
    m_html = re.search(r"<html\b[^>]*>", cur[:500])
    check("html tag has lang attribute", bool(m_html) and "lang=" in m_html.group(0))
    check(
        "html tag has data-density attribute (NEW in Plan 1)",
        bool(m_html) and "data-density=" in m_html.group(0),
    )

    # Style block structure
    cur_blocks = style_blocks(cur)
    base_blocks = style_blocks(base)
    ds_block = cur_blocks[0]
    cur_legacy_blocks = cur_blocks[1:]  # everything after DS

    # DS block: confirm only DS tokens, no legacy
    ds_vars = aggregate_vars([ds_block])
    ds_only_vars = {v for v in ds_vars if v.startswith("--ds-")}
    non_ds_in_ds_block = {v for v in ds_vars if not v.startswith("--ds-")}
    check(
        "DS style block contains only --ds-* variables",
        len(non_ds_in_ds_block) == 0,
        f"{len(ds_only_vars)} --ds-* vars"
        + (f", STRAY: {non_ds_in_ds_block}" if non_ds_in_ds_block else ""),
    )

    # Legacy blocks: confirm NO --ds-* variables leaked
    legacy_vars = aggregate_vars(cur_legacy_blocks)
    ds_in_legacy = {v for v in legacy_vars if v.startswith("--ds-")}
    check("no --ds-* variables in legacy <style> blocks", len(ds_in_legacy) == 0)

    # DS block brace balance
    check(
        "DS style block brace balance (new block)",
        ds_block.count("{") == ds_block.count("}"),
    )

    # Legacy brace balance: compare DELTA vs baseline (not absolute).
    # COE has a pre-existing off-by-one in its legacy CSS that Chrome tolerates.
    cur_legacy_open, cur_legacy_close = count_braces_total(cur_legacy_blocks)
    base_open, base_close = count_braces_total(base_blocks)
    cur_imbalance = cur_legacy_open - cur_legacy_close
    base_imbalance = base_open - base_close
    check(
        "legacy brace balance unchanged vs baseline",
        cur_imbalance == base_imbalance,
        f"current={cur_imbalance}, baseline={base_imbalance}",
    )

    # -----------------------------------------------------------------
    # LEVEL 4 — Print media sanity
    # -----------------------------------------------------------------
    print("\nLevel 4 — print media:")

    # DS block must NOT add @media print rules (those come in Plan 3)
    ds_print = count_print_rules([ds_block])
    check("DS block has zero @media print rules", ds_print == 0)

    # Total @media print rules across ALL style blocks — must equal baseline
    cur_total_print = count_print_rules(cur_blocks)
    base_total_print = count_print_rules(base_blocks)
    check(
        "total @media print rules unchanged vs baseline",
        cur_total_print == base_total_print,
        f"current={cur_total_print}, baseline={base_total_print}",
    )

    # Icon sprite is display:none (invisible in print)
    svg_match = re.search(
        r'<svg[^>]*style\s*=\s*["\']([^"\']*)["\'][^>]*>', cur
    )
    sprite_hidden = bool(svg_match) and "display:none" in svg_match.group(1)
    check("icon sprite is display:none", sprite_hidden)

    # -----------------------------------------------------------------
    # LEVEL 5 — Font, tokens, WCAG
    # -----------------------------------------------------------------
    print("\nLevel 5 — font / tokens / data URI / body font:")

    # @font-face declaration in DS block
    font_face = re.search(r"@font-face\s*\{[^}]*\}", ds_block, re.DOTALL)
    check("DS block has @font-face rule", font_face is not None)

    if font_face:
        ff = font_face.group(0)
        check(
            "  @font-face has font-family: Inter",
            "font-family: 'Inter'" in ff or 'font-family: "Inter"' in ff,
        )
        check("  @font-face has variable font-weight 100 900", "font-weight: 100 900" in ff)
        check("  @font-face has font-display: swap", "font-display: swap" in ff)
        check("  @font-face uses data:font/woff2;base64", "data:font/woff2;base64," in ff)

    # Base64 font payload integrity
    b64_match = re.search(r"data:font/woff2;base64,([A-Za-z0-9+/=]+)", ds_block)
    if b64_match:
        b64 = b64_match.group(1)
        try:
            raw = base64.b64decode(b64)
            check("  base64 font payload decodes", True, f"{len(raw):,} bytes")
            check("  decoded bytes start with wOF2 magic", raw[:4] == b"wOF2")
            check(
                "  decoded size ~344 KB (within 300-400 KB)",
                300_000 <= len(raw) <= 400_000,
                f"{len(raw) / 1024:.0f} KB",
            )
        except Exception as e:
            check("  base64 font payload decodes", False, str(e))
    else:
        check("  base64 font payload present", False, "no match")

    # Required semantic text tokens present
    required_semantic = [
        "--ds-brand-primary",
        "--ds-neutral-fg",
        "--ds-status-info-fg",
        "--ds-status-success-fg",
        "--ds-status-warning-fg",
        "--ds-status-alert-fg",
        "--ds-status-emergency-fg",
        "--ds-focus-ring-color",
    ]
    missing = [t for t in required_semantic if t not in ds_block]
    check(
        "all required semantic text tokens present",
        len(missing) == 0,
        f"{len(required_semantic)} tokens"
        + (f", missing: {missing}" if missing else ""),
    )

    # Body font-family still legacy stack (Inter NOT applied — dormant)
    body_rule_search = re.search(
        r"(^|\s|\})body\s*\{[^}]*font-family\s*:\s*([^;]+);",
        "\n".join(cur_legacy_blocks),
    )
    if body_rule_search:
        body_ff = body_rule_search.group(2).strip()
        is_legacy = expected["body_font_has"] in body_ff and "Inter" not in body_ff
        check(
            "body font-family is legacy stack (Inter NOT applied)",
            is_legacy,
            body_ff[:70],
        )
    else:
        check("body font-family rule found in legacy", False, "no match")

    # Token aliasing spot-checks — follow var() chains through the 3-layer
    # architecture (primitive → semantic → component). Semantic tokens
    # reference primitives via var(), not literal hex values.
    #
    # Extract all --* definitions from the DS block and build a lookup.
    ds_no_comments = strip_css_comments(ds_block)
    all_defs = dict(
        re.findall(r"(--[a-z][a-z0-9-]+)\s*:\s*([^;]+);", ds_no_comments)
    )

    def resolve(token: str, max_depth: int = 5) -> str:
        """Resolve a var() chain to a literal value."""
        val = all_defs.get(token, "").strip()
        depth = 0
        while val.startswith("var(") and depth < max_depth:
            m = re.match(r"var\(\s*(--[a-z][a-z0-9-]+)\s*\)", val)
            if not m:
                break
            val = all_defs.get(m.group(1), "").strip()
            depth += 1
        return val

    resolution_spot_checks = {
        "--ds-brand-primary": "#004C7B",
        "--ds-brand-primary-hover": "#003a5e",
        "--ds-status-alert-border": "#c62828",
        "--ds-cat-avsec-bombeiros": "#c62828",
        "--ds-neutral-canvas": "#f6f8fa",
    }
    for token, expected_primitive in resolution_spot_checks.items():
        if token not in all_defs:
            check(f"  {token} defined", False, "not found in DS block")
            continue
        actual = resolve(token)
        check(
            f"  {token} resolves to {expected_primitive}",
            actual.lower() == expected_primitive.lower(),
            f"resolved: {actual}",
        )


print("\n" + "=" * 60)
if ALL_OK:
    print("ALL PROGRAMMATIC LEVEL 3/4/5 CHECKS PASS (delta-based vs baseline)")
    sys.exit(0)
else:
    print("SOME CHECKS FAILED — see above")
    sys.exit(1)
