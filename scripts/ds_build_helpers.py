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


_VALID_DENSITIES = ("compact", "comfortable")


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

    Raises:
        ValueError: if the resolved value is not in _VALID_DENSITIES
            (e.g., airport override or portal config contains a typo like "medium")
    """
    portal_id = portal_config.get("id", "")

    # Step 1: airport override
    airport_portals = airport.get("portals", {}) or {}
    override = airport_portals.get(portal_id, {}) or {}
    if "density" in override:
        resolved = override["density"]
    # Step 2: portal default
    elif "density" in portal_config:
        resolved = portal_config["density"]
    # Step 3: fallback
    else:
        resolved = default

    if resolved not in _VALID_DENSITIES:
        raise ValueError(
            f"Invalid density {resolved!r}; must be one of {_VALID_DENSITIES}"
        )
    return resolved


def compile_design_system_css(styles_root: Path, density: str) -> str:
    """
    Read the Design System CSS files under `styles_root` and concatenate them
    in the deterministic cascade order defined in the spec (Section 6.2).

    Current cascade (Plan 4 — Foundation + Base + Chrome + Components + Print):
      1. tokens/primitive.css     (required)
      2. tokens/semantic.css      (required)
      3. tokens/density-<X>.css   (required, where X = density param)
      4. base/*.css               (optional, alphabetical filename order)
      5. chrome/*.css             (optional, alphabetical filename order)
      6. components/*.css         (optional, alphabetical filename order)
      7. print/print.css          (optional, ALWAYS LAST)

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

    # Required token files
    required_files = [
        styles_root / "tokens" / "primitive.css",
        styles_root / "tokens" / "semantic.css",
        styles_root / "tokens" / f"density-{density}.css",
    ]
    for f in required_files:
        if not f.exists():
            raise FileNotFoundError(f"Required DS CSS file not found: {f}")

    # Optional directories, in cascade order. Each entry has *.css files
    # picked up in alphabetical order. `print/` is the exception — it's
    # a single file treated as the final block.
    optional_dirs_alpha = [
        styles_root / "base",
        styles_root / "chrome",
        styles_root / "components",
    ]
    print_file = styles_root / "print" / "print.css"

    def _collect_alpha(directory: Path) -> list[Path]:
        if not directory.exists():
            return []
        return sorted(p for p in directory.glob("*.css") if p.is_file())

    pieces: list[str] = []

    def _append_file(f: Path) -> None:
        rel_path = f.relative_to(styles_root.parent).as_posix()
        banner = f"/* ---------- {rel_path} ---------- */"
        pieces.append(banner)
        pieces.append(f.read_text(encoding="utf-8").rstrip())
        pieces.append("")  # blank line separator

    # 1-3: required tokens
    for f in required_files:
        _append_file(f)

    # 4-6: optional directories, alphabetical within each
    for d in optional_dirs_alpha:
        for f in _collect_alpha(d):
            _append_file(f)

    # 7: print file is always last
    if print_file.exists():
        _append_file(print_file)

    return "\n".join(pieces)


def encode_font_woff2_base64(woff2_path: Path) -> str:
    """
    Read a .woff2 font file and return its base64-encoded content as an ASCII
    string suitable for embedding in a CSS `src: url('data:font/woff2;base64,...')`
    rule.

    Args:
        woff2_path: absolute Path to the .woff2 file

    Returns:
        base64-encoded ASCII string (no data: prefix, no line wraps)

    Raises:
        FileNotFoundError: if the file does not exist
    """
    data = Path(woff2_path).read_bytes()
    return base64.b64encode(data).decode("ascii")


def encode_image_base64(image_path: Path) -> str:
    """
    Read an image file (PNG/JPG/WebP/SVG) and return its base64-encoded content
    as an ASCII string suitable for embedding in an HTML `<img src="data:image/X;base64,...">`
    attribute or CSS `background-image: url('data:image/X;base64,...')` rule.

    Args:
        image_path: absolute Path to the image file

    Returns:
        base64-encoded ASCII string (no data: prefix, no line wraps)

    Raises:
        FileNotFoundError: if the file does not exist
    """
    data = Path(image_path).read_bytes()
    return base64.b64encode(data).decode("ascii")
