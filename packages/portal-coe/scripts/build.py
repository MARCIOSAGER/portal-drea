#!/usr/bin/env python3
"""
Portal COE — Build Script (Portal DREA monorepo)
=================================================

Gera o HTML final distribuível do Portal COE (módulo do Portal DREA) a partir
dos ficheiros fonte em packages/portal-coe/src/ e da configuração do aeroporto
em config/airport-XXXX.json (raiz do monorepo, partilhado com portal-ssci).

Uso (a partir da raiz do monorepo):
    python packages/portal-coe/scripts/build.py
    python packages/portal-coe/scripts/build.py --config config/airport-fnmo.json
    python packages/portal-coe/scripts/build.py --no-validate

Uso (a partir de dentro do package):
    cd packages/portal-coe && python scripts/build.py

Estrutura esperada:
    <monorepo-root>/
    ├── VERSION                        (plataforma DREA)
    ├── config/
    │   └── airport-fnmo.json          (partilhado com portal-ssci)
    ├── shared/                        (código partilhado futuro)
    └── packages/
        └── portal-coe/
            ├── src/Portal_COE_AWM.source.html
            ├── scripts/build.py       (este ficheiro)
            └── dist/Portal_COE_AWM.html  (output)

Fase actual:
    Etapa 2 — passthrough. O script copia src/Portal_COE_AWM.source.html
    para dist/ sem alterações estruturais, apenas substitui placeholders
    básicos. Isto valida o pipeline antes de começarmos a partir o ficheiro
    em secções.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ========================================================================
# Configuração de caminhos
# ========================================================================
# Estrutura monorepo:
#   REPO_ROOT/
#   ├── VERSION                              ← versão da plataforma DREA
#   ├── config/airport-fnmo.json             ← config partilhada
#   ├── shared/                              ← código partilhado
#   └── packages/portal-coe/
#       ├── src/                             ← PACKAGE_ROOT/src
#       ├── dist/                            ← PACKAGE_ROOT/dist (output)
#       └── scripts/build.py                 ← este ficheiro

# __file__ = packages/portal-coe/scripts/build.py
# parent = packages/portal-coe/scripts
# parent.parent = packages/portal-coe (PACKAGE_ROOT)
# parent.parent.parent = packages
# parent.parent.parent.parent = REPO_ROOT
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent.parent

SRC_DIR = PACKAGE_ROOT / "src"
DIST_DIR = PACKAGE_ROOT / "dist"

CONFIG_DIR = REPO_ROOT / "config"
VERSION_FILE = REPO_ROOT / "VERSION"
SHARED_DIR = REPO_ROOT / "shared"

DEFAULT_SOURCE = SRC_DIR / "Portal_COE_AWM.source.html"
DEFAULT_CONFIG = CONFIG_DIR / "airport-fnmo.json"
DEFAULT_OUTPUT = DIST_DIR / "Portal_COE_AWM.html"


# --- Design System helpers (Plan 1: Foundation Dormant) -------------------
# Import ds_build_helpers from scripts/ at the repo root. Shared between
# portal-coe and portal-ssci builds.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import ds_build_helpers as dsh  # noqa: E402


# ========================================================================
# Helpers
# ========================================================================

def _rel(path: Path) -> Path:
    """
    Devolve o path relativo ao REPO_ROOT quando possível, para prints legíveis.
    Se o path estiver fora do REPO_ROOT, devolve o path absoluto.
    """
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def read_version() -> str:
    """Lê a versão do ficheiro VERSION na raiz."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0-unknown"


def read_config(config_path: Path) -> dict:
    """Lê o JSON de configuração do aeroporto. Devolve dict vazio se não existir."""
    if not config_path.exists():
        print(f"  [warn] Config não encontrada: {config_path}")
        print(f"  [warn] A build vai prosseguir com defaults mínimos.")
        return {
            "airport": {
                "name": "Aeroporto Welwitschia Mirabilis",
                "oaci": "FNMO",
                "iata": "MSZ",
                "location": "Namibe, Angola",
            }
        }
    return json.loads(config_path.read_text(encoding="utf-8"))


def substitute_placeholders(html: str, context: dict) -> str:
    """
    Substitui placeholders {{KEY}} no HTML pelo valor correspondente em context.

    Placeholders suportados:
        {{VERSION}}           → versão da plataforma DREA
        {{BUILD_DATE}}        → data/hora do build (ISO)
        {{BUILD_DATE_SHORT}}  → data do build (YYYY-MM-DD)
        {{AIRPORT.NAME}}      → nome do aeroporto (ex: "Aeroporto Welwitschia Mirabilis")
        {{AIRPORT.OACI}}      → código OACI (ex: "FNMO")
        {{AIRPORT.IATA}}      → código IATA (ex: "MSZ")
        {{AIRPORT.LOCATION}}  → localização (ex: "Namibe, Angola")
        {{AIRPORT.*}}         → qualquer campo aninhado do airport (flatten)
        {{CONTACTS_JSON}}     → JSON literal dos contactos (array), pronto para
                                substituir `var AWM_CONTACTS_DEFAULT = ...;`
    """
    # --- Placeholder especial: CONTACTS_JSON ---
    # Extrai config.contacts.items (se existir) e serializa como JSON bem formado.
    # O resultado é injectado directamente como literal JavaScript:
    #     var AWM_CONTACTS_DEFAULT = {{CONTACTS_JSON}};
    # →   var AWM_CONTACTS_DEFAULT = [ {...}, {...}, ... ];
    contacts_json = "[]"
    contacts_node = context.get("contacts") if isinstance(context.get("contacts"), dict) else None
    if contacts_node and isinstance(contacts_node.get("items"), list):
        contacts_json = json.dumps(
            contacts_node["items"],
            ensure_ascii=False,
            indent=None,
            separators=(",", ":"),
        )
    html = html.replace("{{CONTACTS_JSON}}", contacts_json)

    # --- Placeholders planos ---
    # Campos aninhados são achatados em chaves tipo AIRPORT.NAME.
    # Listas e dicts aninhados complexos são ignorados (não substituem nada).
    flat = _flatten_dict(context)
    for key, value in flat.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value))

    return html


def _flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Achata um dict aninhado em chaves tipo "airport.name".

    Ignora valores que são listas, dicts aninhados complexos (com chaves _comment
    ou _placeholder), e chaves que começam com underscore (metadados).
    Apenas strings, números e bools chegam ao output final.
    """
    items = []
    for k, v in d.items():
        if k.startswith("_"):
            continue  # ignorar _meta, _comment, etc.
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        new_key_upper = new_key.upper()
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key_upper, sep).items())
        elif isinstance(v, list):
            continue  # listas não são substituíveis via placeholder simples
        else:
            items.append((new_key_upper, v))
    return dict(items)


def validate_inline_scripts(html: str, html_path: Path) -> tuple[int, int]:
    """
    Valida sintaticamente cada bloco <script> inline usando `node --check`.

    Devolve tuple (total_blocks, errors).
    """
    # Captura todos os <script> inline (não externos com src=)
    pattern = re.compile(
        r"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>",
        re.DOTALL | re.IGNORECASE,
    )
    blocks = pattern.findall(html)

    errors = 0
    for i, block in enumerate(blocks, 1):
        with tempfile.NamedTemporaryFile(
            "w",
            suffix=".js",
            delete=False,
            encoding="utf-8",
        ) as tf:
            tf.write(block)
            tmp_path = tf.name

        try:
            result = subprocess.run(
                ["node", "--check", tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors += 1
                print(f"  [error] Block #{i}:")
                print(f"    {result.stderr[:500]}")
        except FileNotFoundError:
            print("  [warn] Node.js não encontrado — validação sintáctica ignorada")
            return len(blocks), 0
        except subprocess.TimeoutExpired:
            errors += 1
            print(f"  [error] Block #{i}: timeout na validação")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return len(blocks), errors


# ========================================================================
# Build principal
# ========================================================================

def build(
    source_path: Path,
    config_path: Path,
    output_path: Path,
    validate: bool = True,
) -> int:
    """
    Executa o build. Devolve código de saída (0 = sucesso, !=0 = erro).
    """
    print("=" * 60)
    print("Portal COE — Build Script")
    print("=" * 60)

    version = read_version()
    build_date = datetime.now()

    print(f"  Version:     {version}")
    print(f"  Build date:  {build_date.isoformat(timespec='seconds')}")
    print(f"  Source:      {_rel(source_path)}")
    print(f"  Config:      {_rel(config_path) if config_path.exists() else '(default)'}")
    print(f"  Output:      {_rel(output_path)}")
    print()

    # --- 1. Verificar fonte ---
    if not source_path.exists():
        print(f"  [error] Source HTML não encontrado: {source_path}")
        return 1

    source_html = source_path.read_text(encoding="utf-8")
    source_size = len(source_html)
    print(f"  [step] Source lido: {source_size:,} chars ({source_size/1024/1024:.2f} MB)")

    # --- 2. Ler config do aeroporto ---
    config = read_config(config_path)

    # === Plan 1: Design System Foundation — dormant payload ==============
    # (1) Load the portal-level config
    portal_config_path = PACKAGE_ROOT / "portal.config.json"
    if not portal_config_path.exists():
        print(f"  [error] portal.config.json não encontrado em {portal_config_path}")
        return 1
    portal_config = dsh.load_portal_config(portal_config_path)

    # (2) Resolve density (airport override → portal default → fallback)
    density = dsh.resolve_density(config, portal_config, default="compact")
    print(f"  [ds] portal={portal_config['id']} density={density}")

    # (3) Compile the Design System CSS (tokens + base/fonts)
    shared_styles_root = SHARED_DIR / "styles"
    ds_css = dsh.compile_design_system_css(shared_styles_root, density=density)
    print(f"  [ds] compiled ds_css ({len(ds_css):,} chars)")

    # (4) Encode the Inter Variable font as base64
    inter_woff2_path = SHARED_DIR / "assets" / "fonts" / "Inter-VariableFont.woff2"
    if not inter_woff2_path.exists():
        print(f"  [error] Inter-VariableFont.woff2 não encontrado em {inter_woff2_path}")
        return 1
    ds_inter_b64 = dsh.encode_font_woff2_base64(inter_woff2_path)
    print(f"  [ds] encoded Inter woff2 ({len(ds_inter_b64):,} base64 chars)")

    # (5) Read the icon sprite (inline SVG, already wrapped in <svg style="display:none">)
    sprite_path = SHARED_DIR / "assets" / "icons" / "sprite.svg"
    if not sprite_path.exists():
        print(f"  [error] sprite.svg não encontrado em {sprite_path}")
        return 1
    icon_sprite = sprite_path.read_text(encoding="utf-8")

    # (5b) Encode the real SGA logo PNG (horizontal lockup with wordmark + graphic + tagline)
    logo_sga_path = SHARED_DIR / "assets" / "logo-sga.png"
    if not logo_sga_path.exists():
        print(f"  [error] logo-sga.png não encontrado em {logo_sga_path}")
        return 1
    logo_sga_b64 = dsh.encode_image_base64(logo_sga_path)
    print(f"  [ds] encoded logo-sga.png ({len(logo_sga_b64):,} base64 chars)")

    # (6) Inject DS blobs into source_html via direct string replacement.
    # This is done BEFORE the existing substitute_placeholders call, using
    # the same manual-replace pattern as {{CONTACTS_JSON}} inside
    # substitute_placeholders itself. These placeholders hold large blobs
    # that bypass the _flatten_dict mechanism.
    #
    # Sanity check: each DS marker must appear exactly once in source_html
    # before replace, and be fully consumed after. Catches source HTML typos
    # and prevents accidental silent double-replace.
    #
    # Note: {{DS_INTER_WOFF2_BASE64}} is NOT expected in source_html at this
    # point — it only appears AFTER {{DS_CSS}} is replaced (it lives inside
    # fonts.css which is part of ds_css). The two-phase replacement below
    # handles the ordering correctly.
    # Markers with expected count — single-occurrence invariants
    _ds_markers_single = [
        ("{{DS_CSS}}", ds_css),
        ("{{ICON_SPRITE}}", icon_sprite),
    ]
    for marker, value in _ds_markers_single:
        count = source_html.count(marker)
        if count != 1:
            print(f"  [error] Expected exactly 1 occurrence of {marker!r} in source HTML, found {count}")
            return 1
        source_html = source_html.replace(marker, value)
        if marker in source_html:
            print(f"  [error] {marker!r} still present after replacement")
            return 1

    # Markers allowed to appear multiple times (splash image + print header + etc)
    _ds_markers_multi = [
        ("{{LOGO_SGA_PNG_BASE64}}", logo_sga_b64),
    ]
    for marker, value in _ds_markers_multi:
        count = source_html.count(marker)
        if count < 1:
            print(f"  [error] Expected at least 1 occurrence of {marker!r} in source HTML, found 0")
            return 1
        source_html = source_html.replace(marker, value)
        if marker in source_html:
            print(f"  [error] {marker!r} still present after replacement")
            return 1
        print(f"  [ds] replaced {marker} in {count} location(s)")

    # Now source_html contains ds_css expanded, which itself contains
    # {{DS_INTER_WOFF2_BASE64}} inside the fonts.css @font-face src: url() line.
    # Replace it (expect exactly 1 occurrence after the fonts.css single-src fix).
    inter_marker = "{{DS_INTER_WOFF2_BASE64}}"
    count = source_html.count(inter_marker)
    if count != 1:
        print(f"  [error] Expected exactly 1 occurrence of {inter_marker!r} after DS_CSS replace, found {count}")
        return 1
    source_html = source_html.replace(inter_marker, ds_inter_b64)
    if inter_marker in source_html:
        print(f"  [error] {inter_marker!r} still present after replacement")
        return 1
    # Note: {{BUILD_DATE}} and {{BUILD_DATE_SHORT}} already exist in context and
    # are handled by substitute_placeholders.
    # ======================================================================

    # --- 3. Construir contexto de substituição ---
    context = {
        "version": version,
        "build_date": build_date.isoformat(timespec="seconds"),
        "build_date_short": build_date.strftime("%Y-%m-%d"),
        "portal": {**portal_config, "density": density},  # NEW: enables {{PORTAL.*}} placeholders. density here is the RESOLVED value (airport override → portal config → default), not the raw portal.config.json value.
        **config,
    }

    # --- 4. Substituir placeholders ---
    output_html = substitute_placeholders(source_html, context)
    print(f"  [step] Placeholders substituídos")

    # --- 5. Garantir pasta dist ---
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- 6. Escrever output ---
    output_path.write_text(output_html, encoding="utf-8")
    output_size = output_path.stat().st_size
    print(f"  [step] Output escrito: {output_size:,} chars ({output_size/1024/1024:.2f} MB)")

    # --- 7. Validar sintaxe dos scripts ---
    if validate:
        print(f"  [step] A validar blocos <script> inline com node --check...")
        total, errors = validate_inline_scripts(output_html, output_path)
        status = "OK" if errors == 0 else "FAIL"
        print(f"  [{status}] {total} blocks, {errors} errors")
        if errors > 0:
            return 2

    print()
    print("  [done] Build concluído com sucesso.")
    print(f"  [done] Abrir: {output_path}")
    print()
    return 0


# ========================================================================
# CLI
# ========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Portal COE — Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"HTML fonte (default: {_rel(DEFAULT_SOURCE)})",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Config do aeroporto (default: {_rel(DEFAULT_CONFIG)})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"HTML final (default: {_rel(DEFAULT_OUTPUT)})",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Saltar validação sintáctica com node --check",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Apenas validar o HTML final existente (não rebuilda)",
    )

    args = parser.parse_args()

    if args.validate:
        # Modo: apenas validar
        target = args.output
        if not target.exists():
            print(f"[error] Ficheiro não existe: {target}")
            return 1
        html = target.read_text(encoding="utf-8")
        print(f"Validando: {target}")
        total, errors = validate_inline_scripts(html, target)
        status = "OK" if errors == 0 else "FAIL"
        print(f"[{status}] {total} blocks, {errors} errors")
        return 0 if errors == 0 else 2

    # Modo: build normal
    return build(
        source_path=args.source,
        config_path=args.config,
        output_path=args.output,
        validate=not args.no_validate,
    )


if __name__ == "__main__":
    sys.exit(main())
