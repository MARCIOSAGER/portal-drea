"""Unit tests for scripts/rename_ds_namespace.py."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import rename_ds_namespace as rn  # noqa: E402


class TestRenameInText:
    def test_simple_variable_declaration(self):
        text = "--ds-blue-800: #004C7B;"
        new, count = rn.rename_in_text(text)
        assert new == "--blue-800: #004C7B;"
        assert count == 1

    def test_var_reference(self):
        text = "color: var(--ds-brand-primary);"
        new, count = rn.rename_in_text(text)
        assert new == "color: var(--brand-primary);"
        assert count == 1

    def test_var_with_fallback(self):
        text = "color: var(--ds-brand-primary, #004C7B);"
        new, count = rn.rename_in_text(text)
        assert new == "color: var(--brand-primary, #004C7B);"
        assert count == 1

    def test_multiple_on_same_line(self):
        text = "--ds-a: 1; --ds-b: 2;"
        new, count = rn.rename_in_text(text)
        assert new == "--a: 1; --b: 2;"
        assert count == 2

    def test_nested_var(self):
        text = "--ds-brand-primary: var(--ds-blue-800);"
        new, count = rn.rename_in_text(text)
        assert new == "--brand-primary: var(--blue-800);"
        assert count == 2

    def test_preserves_dark_blue_legacy(self):
        """Legacy tokens that happen to contain 'ds' in their middle are NOT touched."""
        text = "--dark-blue: #004C7B;"
        new, count = rn.rename_in_text(text)
        assert new == "--dark-blue: #004C7B;"
        assert count == 0

    def test_preserves_disabled_not_ds_prefix(self):
        text = "input:disabled { opacity: 0.5; }"
        new, count = rn.rename_in_text(text)
        assert new == text
        assert count == 0

    def test_preserves_text_in_comments_but_renames_vars(self):
        """The regex is purely textual — it will also rename --ds- references
        inside comments. This is acceptable because Plan 6 does not care
        about comment content matching the code. If a comment says
        `/* was --ds-blue-800 */`, it becomes `/* was --blue-800 */` —
        which is accurate, not broken."""
        text = "/* The --ds-blue-800 token */ .btn { color: var(--ds-blue-800); }"
        new, count = rn.rename_in_text(text)
        assert new == "/* The --blue-800 token */ .btn { color: var(--blue-800); }"
        assert count == 2

    def test_empty_text(self):
        new, count = rn.rename_in_text("")
        assert new == ""
        assert count == 0

    def test_no_matches(self):
        text = "body { color: red; }"
        new, count = rn.rename_in_text(text)
        assert new == text
        assert count == 0

    def test_multiline(self):
        text = """:root {
    --ds-blue-800: #004C7B;
    --ds-brand-primary: var(--ds-blue-800);
}
body { color: var(--ds-brand-primary); }"""
        new, count = rn.rename_in_text(text)
        assert "--ds-" not in new
        assert count == 4

    def test_partial_word_not_matched(self):
        """--ds without a hyphen following is not a token — not matched."""
        text = "--ds: 1;"
        new, count = rn.rename_in_text(text)
        assert count == 0


class TestIntegrationWithRealLikeFile:
    def test_process_file_dry_run(self, tmp_path: Path):
        f = tmp_path / "example.css"
        f.write_text(":root { --ds-a: 1; --ds-b: 2; }", encoding="utf-8")
        n = rn.process_file(f, write=False)
        assert n == 2
        # File unchanged
        assert f.read_text(encoding="utf-8") == ":root { --ds-a: 1; --ds-b: 2; }"

    def test_process_file_write(self, tmp_path: Path):
        f = tmp_path / "example.css"
        f.write_text(":root { --ds-a: 1; --ds-b: 2; }", encoding="utf-8")
        n = rn.process_file(f, write=True)
        assert n == 2
        # File written
        assert f.read_text(encoding="utf-8") == ":root { --a: 1; --b: 2; }"

    def test_process_file_no_matches_is_noop(self, tmp_path: Path):
        f = tmp_path / "example.css"
        f.write_text("body { color: red; }", encoding="utf-8")
        n = rn.process_file(f, write=True)
        assert n == 0
