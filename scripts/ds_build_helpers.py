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


_VALID_DENSITIES = ("compact", "comfortable")


def compile_design_system_css(styles_root: Path, density: str) -> str:
    """
    Read the Design System CSS files under `styles_root` and concatenate them
    in the deterministic cascade order defined in the spec (Section 6.2).

    Current cascade (Plan 1 — Foundation Dormant):
      1. tokens/primitive.css     (required)
      2. tokens/semantic.css      (required)
      3. tokens/density-<X>.css   (required, where X = density param)
      4. base/fonts.css           (optional — OK if missing during Plan 1)

    Plans 2-3 will extend this by adding base/reset.css, base/typography.css,
    base/global.css, chrome/*.css, components/*.css, print/print.css.

    Args:
        styles_root: absolute Path to shared/styles/
        density: "compact" or "comfortable"

    Returns:
        A single string containing the concatenated CSS. Files are separated
        by a blank line and a banner comment indicating the source file.

    Raises:
        ValueError: if density is not "compact" or "comfortable"
        FileNotFoundError: if any required file is missing
    """
    if density not in _VALID_DENSITIES:
        raise ValueError(
            f"Invalid density {density!r}; must be one of {_VALID_DENSITIES}"
        )

    styles_root = Path(styles_root)

    # Build the ordered list of files to concatenate.
    # Required files come first; optional files are skipped if missing.
    required_files = [
        styles_root / "tokens" / "primitive.css",
        styles_root / "tokens" / "semantic.css",
        styles_root / "tokens" / f"density-{density}.css",
    ]
    optional_files = [
        styles_root / "base" / "fonts.css",
    ]

    # Verify all required files exist up-front
    for f in required_files:
        if not f.exists():
            raise FileNotFoundError(f"Required DS CSS file not found: {f}")

    pieces: list[str] = []
    for f in required_files + optional_files:
        if not f.exists():
            continue  # optional file, skip
        rel_path = f.relative_to(styles_root.parent).as_posix()
        banner = f"/* ---------- {rel_path} ---------- */"
        pieces.append(banner)
        pieces.append(f.read_text(encoding="utf-8").rstrip())
        pieces.append("")  # blank line separator

    return "\n".join(pieces)
