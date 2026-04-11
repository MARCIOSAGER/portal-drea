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
