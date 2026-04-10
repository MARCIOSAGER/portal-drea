#!/usr/bin/env python3
"""
Portal SSCI — Build Script (Portal DREA monorepo)
===================================================

Gera o HTML final distribuível do Portal SSCI (módulo do Portal DREA) a partir
dos ficheiros fonte em packages/portal-ssci/src/ e da configuração do aeroporto
em config/airport-XXXX.json (raiz do monorepo, partilhado com portal-coe).

Uso (a partir da raiz do monorepo):
    python packages/portal-ssci/scripts/build.py
    python packages/portal-ssci/scripts/build.py --config config/airport-fnmo.json
    python packages/portal-ssci/scripts/build.py --no-validate

Uso (a partir de dentro do package):
    cd packages/portal-ssci && python scripts/build.py

Estrutura esperada:
    <monorepo-root>/
    ├── VERSION                        (plataforma DREA)
    ├── config/
    │   └── airport-fnmo.json          (partilhado com portal-coe)
    ├── shared/                        (código partilhado futuro)
    └── packages/
        └── portal-ssci/
            ├── src/Portal_PSCI_AWM.source.html
            ├── scripts/build.py       (este ficheiro)
            └── dist/Portal_PSCI_AWM.html  (output)

Fase actual:
    Etapa 2 — passthrough. O script copia src/Portal_PSCI_AWM.source.html
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
#   └── packages/portal-ssci/
#       ├── src/                             ← PACKAGE_ROOT/src
#       ├── dist/                            ← PACKAGE_ROOT/dist (output)
#       └── scripts/build.py                 ← este ficheiro

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent.parent

SRC_DIR = PACKAGE_ROOT / "src"
DIST_DIR = PACKAGE_ROOT / "dist"

CONFIG_DIR = REPO_ROOT / "config"
VERSION_FILE = REPO_ROOT / "VERSION"
SHARED_DIR = REPO_ROOT / "shared"

DEFAULT_SOURCE = SRC_DIR / "Portal_PSCI_AWM.source.html"
DEFAULT_CONFIG = CONFIG_DIR / "airport-fnmo.json"
DEFAULT_OUTPUT = DIST_DIR / "Portal_PSCI_AWM.html"


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

    Placeholders suportados nesta fase:
        {{VERSION}}           → versão do Portal DREA (plataforma)
        {{BUILD_DATE}}        → data/hora do build (ISO)
        {{BUILD_DATE_SHORT}}  → data do build (YYYY-MM-DD)
        {{AIRPORT.NAME}}      → nome do aeroporto
        {{AIRPORT.OACI}}      → código OACI (ex: "FNMO")
        {{AIRPORT.IATA}}      → código IATA
        {{AIRPORT.LOCATION}}  → localização

    Nesta Etapa 2 (passthrough), os placeholders ainda não existem no source
    HTML, então esta função é um no-op efectivo — só substitui os que encontrar.
    """
    flat = _flatten_dict(context)
    for key, value in flat.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value))
    return html


def _flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Achata um dict aninhado em chaves tipo "airport.name"."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        new_key_upper = new_key.upper()
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key_upper, sep).items())
        else:
            items.append((new_key_upper, v))
    return dict(items)


def validate_inline_scripts(html: str) -> tuple[int, int]:
    """
    Valida sintaticamente cada bloco <script> inline usando `node --check`.
    Devolve tuple (total_blocks, errors).
    """
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
    print("Portal SSCI — Build Script")
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

    # --- 3. Construir contexto de substituição ---
    context = {
        "version": version,
        "build_date": build_date.isoformat(timespec="seconds"),
        "build_date_short": build_date.strftime("%Y-%m-%d"),
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
        total, errors = validate_inline_scripts(output_html)
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
        description="Portal SSCI — Build Script",
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
        target = args.output
        if not target.exists():
            print(f"[error] Ficheiro não existe: {target}")
            return 1
        html = target.read_text(encoding="utf-8")
        print(f"Validando: {target}")
        total, errors = validate_inline_scripts(html)
        status = "OK" if errors == 0 else "FAIL"
        print(f"[{status}] {total} blocks, {errors} errors")
        return 0 if errors == 0 else 2

    return build(
        source_path=args.source,
        config_path=args.config,
        output_path=args.output,
        validate=not args.no_validate,
    )


if __name__ == "__main__":
    sys.exit(main())
