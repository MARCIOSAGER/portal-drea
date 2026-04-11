import sys
from pathlib import Path

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
        import pytest
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
        import pytest

        with pytest.raises(ValueError, match="density"):
            dsh.compile_design_system_css(tmp_path, density="medium")

    def test_raises_when_primitive_css_missing(self, tmp_path: Path):
        (tmp_path / "tokens").mkdir()
        # Do not create primitive.css
        import pytest

        with pytest.raises(FileNotFoundError):
            dsh.compile_design_system_css(tmp_path, density="compact")

    def test_handles_missing_base_fonts_css_gracefully_in_phase_1(self, tmp_path: Path):
        """Phase 1 may or may not have base/fonts.css at first — compile must not
        crash if it is missing (fonts are optional during dormant phase)."""
        self._setup_fake_styles(tmp_path)
        (tmp_path / "base" / "fonts.css").unlink()

        # Should not raise; result omits the fonts section
        result = dsh.compile_design_system_css(tmp_path, density="compact")
        assert "/* fonts */" not in result
        assert "/* primitive */" in result  # tokens still present
