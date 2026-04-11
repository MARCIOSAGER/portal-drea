# scripts/ds_build_helpers.py
"""
Design System SGA — build helper functions.

Shared by both packages/portal-coe/scripts/build.py and
packages/portal-ssci/scripts/build.py. Exposes:

- load_portal_config(path)        → dict
- resolve_density(airport, portal_config, default="compact") → str
- compile_design_system_css(styles_root, density) → str
- encode_font_woff2_base64(woff2_path) → str

Import with:
    import sys
    from pathlib import Path
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import ds_build_helpers as dsh
"""
from __future__ import annotations

import base64
import json
from pathlib import Path


def load_portal_config(path: Path) -> dict:
    """
    Load a packages/portal-XXX/portal.config.json file.

    Returns the parsed JSON as a dict. Raises FileNotFoundError if missing,
    json.JSONDecodeError if malformed.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_density(
    airport: dict,
    portal_config: dict,
    default: str = "compact",
) -> str:
    """
    Resolve the density mode for a portal build.

    Resolution order (first wins):
      1. airport.portals[portal_id].density  — per-airport per-portal override
      2. portal_config.density               — portal default
      3. default parameter                   — fallback (defaults to "compact")

    Returns one of "compact" | "comfortable".
    """
    portal_id = portal_config.get("id", "")

    # Step 1: airport override
    airport_portals = airport.get("portals", {}) or {}
    override = airport_portals.get(portal_id, {}) or {}
    if "density" in override:
        return override["density"]

    # Step 2: portal default
    if "density" in portal_config:
        return portal_config["density"]

    # Step 3: fallback
    return default
