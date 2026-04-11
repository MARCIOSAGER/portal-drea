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
