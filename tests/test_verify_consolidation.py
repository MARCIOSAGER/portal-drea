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
