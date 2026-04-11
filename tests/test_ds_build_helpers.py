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
