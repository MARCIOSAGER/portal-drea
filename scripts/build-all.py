#!/usr/bin/env python3
"""
Portal DREA — Build All
========================

Builda todos os packages do monorepo Portal DREA em sequência:
  - packages/portal-coe   (Portal do Coordenador COE)
  - packages/portal-ssci  (Portal do Chefe SSCI / Bombeiros)

Uso:
    python scripts/build-all.py                      # build completo
    python scripts/build-all.py --no-validate        # mais rápido
    python scripts/build-all.py --config config/airport-luanda.json  # outro aeroporto

Os builds individuais chamados por este script também podem ser corridos
directamente:
    python packages/portal-coe/scripts/build.py
    python packages/portal-ssci/scripts/build.py

Saída:
    packages/portal-coe/dist/Portal_COE_AWM.html
    packages/portal-ssci/dist/Portal_PSCI_AWM.html

Falha o processo inteiro com código != 0 se qualquer dos builds falhar.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PACKAGES = [
    {
        "name": "portal-coe",
        "label": "Portal COE",
        "build_script": REPO_ROOT / "packages" / "portal-coe" / "scripts" / "build.py",
    },
    {
        "name": "portal-ssci",
        "label": "Portal SSCI",
        "build_script": REPO_ROOT / "packages" / "portal-ssci" / "scripts" / "build.py",
    },
]


def run_build(pkg: dict, extra_args: list[str]) -> int:
    """Corre o build.py de um package e devolve o exit code."""
    print()
    print("#" * 72)
    print(f"#  {pkg['label']} ({pkg['name']})")
    print("#" * 72)

    if not pkg["build_script"].exists():
        print(f"  [error] Build script não encontrado: {pkg['build_script']}")
        return 1

    cmd = [sys.executable, str(pkg["build_script"])] + extra_args
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Portal DREA — Build All Packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Caminho da config do aeroporto (relativo ou absoluto). Passa --config para cada build.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Saltar validação sintáctica com node --check",
    )
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        choices=[p["name"] for p in PACKAGES],
        help="Buildar apenas um package específico",
    )

    args = parser.parse_args()

    # Preparar argumentos extra para passar ao build individual
    extra_args = []
    if args.config:
        extra_args.extend(["--config", args.config])
    if args.no_validate:
        extra_args.append("--no-validate")

    # Decidir quais packages buildar
    if args.only:
        targets = [p for p in PACKAGES if p["name"] == args.only]
    else:
        targets = PACKAGES

    print()
    print("=" * 72)
    print("  Portal DREA — Build All")
    print("=" * 72)
    print(f"  Repo root:  {REPO_ROOT}")
    print(f"  Targets:    {', '.join(p['name'] for p in targets)}")
    if args.config:
        print(f"  Config:     {args.config}")
    print()

    results = []
    for pkg in targets:
        code = run_build(pkg, extra_args)
        results.append((pkg["name"], code))

    # Sumário
    print()
    print("=" * 72)
    print("  Sumário")
    print("=" * 72)
    all_ok = True
    for name, code in results:
        status = "OK" if code == 0 else f"FAIL (exit {code})"
        print(f"  [{status}] {name}")
        if code != 0:
            all_ok = False
    print()

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
