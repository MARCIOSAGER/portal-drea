"""Unit tests for scripts/ds_build_helpers.py — helpers used by both portal build.py scripts."""
import sys
from pathlib import Path

import pytest

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
        with pytest.raises(FileNotFoundError):
            dsh.load_portal_config(missing)


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

    def test_raises_on_invalid_density_from_airport_override(self):
        airport = {
            "portals": {"portal-coe": {"density": "medium"}},  # typo
        }
        portal_config = {"id": "portal-coe", "density": "compact"}

        with pytest.raises(ValueError, match="density"):
            dsh.resolve_density(airport, portal_config)

    def test_raises_on_invalid_density_from_portal_config(self):
        airport = {}
        portal_config = {"id": "portal-coe", "density": "roomy"}  # typo

        with pytest.raises(ValueError, match="density"):
            dsh.resolve_density(airport, portal_config)


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

        with pytest.raises(ValueError, match="density"):
            dsh.compile_design_system_css(tmp_path, density="medium")

    def test_raises_when_primitive_css_missing(self, tmp_path: Path):
        (tmp_path / "tokens").mkdir()
        # Do not create primitive.css

        with pytest.raises(FileNotFoundError):
            dsh.compile_design_system_css(tmp_path, density="compact")

    def test_raises_when_requested_density_file_missing(self, tmp_path: Path):
        """If density=comfortable requested but only density-compact.css exists,
        must raise FileNotFoundError (not silently fall back)."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "tokens" / "density-comfortable.css").unlink()

        with pytest.raises(FileNotFoundError):
            dsh.compile_design_system_css(tmp_path, density="comfortable")

    def test_handles_missing_base_fonts_css_gracefully_in_phase_1(self, tmp_path: Path):
        """Phase 1 may or may not have base/fonts.css at first — compile must not
        crash if it is missing (fonts are optional during dormant phase)."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "base" / "fonts.css").unlink()

        # Should not raise; result omits the fonts section
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* fonts */" not in result
        assert "/* primitive */" in result  # tokens still present

    def test_components_dir_absent_is_ok(self, tmp_path: Path):
        """Plan 1 world: no components/ directory — compile must still succeed."""
        self._setup_fake_styles(tmp_path)
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* primitive */" in result
        assert "components/" not in result

    def test_components_dir_empty_is_ok(self, tmp_path: Path):
        """Plan 3 Task 1 world: components/ exists but is empty — compile succeeds."""
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
        assert result.index("/* fonts */") < result.index("/* button */")

    def test_components_multiple_css_files_alphabetical_order(self, tmp_path: Path):
        """Multiple components/*.css concatenated in alphabetical filename order."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "components").mkdir()
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
        assert result.index("/* button */") < result.index("/* card */")
        assert result.index("/* card */") < result.index("/* zebra */")

    def test_components_non_css_files_ignored(self, tmp_path: Path):
        """Only files matching *.css are concatenated."""
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

    # ---- Plan 4: full cascade (base/chrome/components/print) ----

    def _setup_plan4_styles(self, root: Path) -> None:
        self._setup_fake_styles(root)  # tokens + base/fonts.css
        (root / "base" / "reset.css").write_text("/* reset */\n", encoding="utf-8")
        (root / "base" / "typography.css").write_text("/* typography */\n", encoding="utf-8")
        (root / "base" / "global.css").write_text("/* global */\n", encoding="utf-8")
        (root / "chrome").mkdir()
        (root / "chrome" / "shell-bar.css").write_text("/* shell-bar */\n", encoding="utf-8")
        (root / "chrome" / "sidebar.css").write_text("/* sidebar */\n", encoding="utf-8")
        (root / "chrome" / "page-grid.css").write_text("/* page-grid */\n", encoding="utf-8")
        (root / "chrome" / "splash.css").write_text("/* splash */\n", encoding="utf-8")
        (root / "chrome" / "footer.css").write_text("/* footer */\n", encoding="utf-8")
        (root / "components").mkdir()
        (root / "components" / "button.css").write_text("/* button */\n", encoding="utf-8")
        (root / "print").mkdir()
        (root / "print" / "print.css").write_text("/* print */\n", encoding="utf-8")

    def test_plan4_full_cascade_order(self, tmp_path: Path):
        """tokens → base/ (alpha) → chrome/ (alpha) → components/ → print/"""
        self._setup_plan4_styles(tmp_path)
        r = dsh.compile_design_system_css(tmp_path, density="compact")
        # tokens first
        assert r.index("/* primitive */") < r.index("/* semantic */") < r.index("/* compact */")
        # base/ alphabetical: fonts, global, reset, typography
        assert r.index("/* compact */") < r.index("/* fonts */")
        assert r.index("/* fonts */") < r.index("/* global */")
        assert r.index("/* global */") < r.index("/* reset */")
        assert r.index("/* reset */") < r.index("/* typography */")
        # chrome/ alphabetical: footer, page-grid, shell-bar, sidebar, splash
        assert r.index("/* typography */") < r.index("/* footer */")
        assert r.index("/* footer */") < r.index("/* page-grid */")
        assert r.index("/* page-grid */") < r.index("/* shell-bar */")
        assert r.index("/* shell-bar */") < r.index("/* sidebar */")
        assert r.index("/* sidebar */") < r.index("/* splash */")
        # components/ next
        assert r.index("/* splash */") < r.index("/* button */")
        # print last
        assert r.index("/* button */") < r.index("/* print */")

    def test_plan4_missing_base_dir_is_ok(self, tmp_path: Path):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "primitive.css").write_text("/* primitive */\n", encoding="utf-8")
        (tmp_path / "tokens" / "semantic.css").write_text("/* semantic */\n", encoding="utf-8")
        (tmp_path / "tokens" / "density-compact.css").write_text("/* compact */\n", encoding="utf-8")
        r = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* primitive */" in r
        assert "/* reset */" not in r

    def test_plan4_empty_chrome_dir_is_ok(self, tmp_path: Path):
        self._setup_fake_styles(tmp_path)
        (tmp_path / "chrome").mkdir()
        r = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* primitive */" in r

    def test_plan4_print_css_is_always_last(self, tmp_path: Path):
        self._setup_plan4_styles(tmp_path)
        (tmp_path / "chrome" / "zzz.css").write_text("/* zzz */\n", encoding="utf-8")
        r = dsh.compile_design_system_css(tmp_path, density="compact")
        assert r.index("/* zzz */") < r.index("/* print */")

    def test_plan4_components_between_chrome_and_print(self, tmp_path: Path):
        self._setup_plan4_styles(tmp_path)
        r = dsh.compile_design_system_css(tmp_path, density="compact")
        assert r.index("/* sidebar */") < r.index("/* button */")
        assert r.index("/* button */") < r.index("/* print */")


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
        with pytest.raises(FileNotFoundError):
            dsh.encode_font_woff2_base64(missing)
