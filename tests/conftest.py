"""Shared pytest fixtures for Portal DREA test suite."""
from pathlib import Path
import pytest


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the Portal DREA repo root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def shared_styles_root(repo_root: Path) -> Path:
    """Absolute path to shared/styles/."""
    return repo_root / "shared" / "styles"


@pytest.fixture
def shared_assets_root(repo_root: Path) -> Path:
    """Absolute path to shared/assets/."""
    return repo_root / "shared" / "assets"
