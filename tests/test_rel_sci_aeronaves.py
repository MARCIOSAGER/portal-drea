"""Structural tests for the Relatório SCI Aeronaves feature (AP.04.033)."""
import re
from pathlib import Path

import pytest


@pytest.fixture
def source_html(repo_root: Path) -> str:
    path = repo_root / "packages" / "portal-ssci" / "src" / "Portal_PSCI_AWM.source.html"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def dist_html(repo_root: Path) -> str:
    path = repo_root / "packages" / "portal-ssci" / "dist" / "Portal_PSCI_AWM.html"
    return path.read_text(encoding="utf-8")


class TestSidebarEntry:
    def test_sidebar_group_title_present(self, source_html: str):
        assert "Relatórios de Ocorrência" in source_html

    def test_nav_button_wires_correct_section_id(self, source_html: str):
        assert "openSection('rel-sci-aeronaves'" in source_html


class TestSectionScaffold:
    def test_section_container_exists(self, source_html: str):
        assert 'id="rel-sci-aeronaves"' in source_html

    def test_three_state_containers_exist(self, source_html: str):
        for s in ("lista", "editor", "visualizacao"):
            assert f'data-state="{s}"' in source_html


class TestJsModule:
    def test_module_exposed_globally(self, source_html: str):
        assert "window.RelSciAeronaves" in source_html

    def test_storage_keys_namespaced(self, source_html: str):
        assert "psci.rel-sci-aeronaves.draft" in source_html
        assert "psci.rel-sci-aeronaves.finalized" in source_html
        assert "psci.rel-sci-aeronaves.counter." in source_html

    def test_public_methods_present(self, source_html: str):
        for method in ("init:", "setState:", "novoRascunho:", "descartarRascunho:",
                       "saveField:", "gerarNumeroControlo:", "imprimir:"):
            assert method in source_html, f"Missing public method: {method}"


class TestControlNumberFormat:
    """The control number is generated in JS. Verify the pattern literal is correct."""

    def test_uses_oaci_year_seq_pattern(self, source_html: str):
        # regex: `oaci + '/' + ano + '/' + String(seq).padStart(3, '0')`
        pattern = re.search(
            r"oaci\s*\+\s*['\"]\/?['\"]\s*\+\s*ano\s*\+\s*['\"]\/?['\"]\s*\+\s*String\(seq\)\.padStart\(3,\s*['\"]0['\"]\)",
            source_html,
        )
        assert pattern, "Control number must follow {OACI}/{year}/{NNN} with 3-digit padding"


class TestBuildArtifacts:
    def test_dist_contains_feature(self, dist_html: str):
        """After build, dist/ must include the new section and module."""
        assert "rel-sci-aeronaves" in dist_html
        assert "Relatórios de Ocorrência" in dist_html

    def test_dist_sidebar_has_no_unresolved_oaci_token(self, dist_html: str):
        """AIRPORT.OACI template token must be replaced in the sidebar header area."""
        idx = dist_html.find('Relatórios de Ocorrência')
        sidebar_block = dist_html[idx:idx + 500]
        assert "{{AIRPORT.OACI}}" not in sidebar_block


class TestValidationRules:
    """The validator lives in JS — verify the required-field set is declared."""

    def test_section1_required_fields_declared(self, source_html: str):
        for f in ("aerodromo", "provincia", "dataAcidente", "horaAcidente",
                  "tipoAeronave", "matricula", "empresa"):
            assert f"'{f}'" in source_html, f"Required s1 field not declared: {f}"

    def test_section2_at_least_one_phase_rule(self, source_html: str):
        assert "marcar pelo menos uma fase" in source_html.lower() or \
               "marcar pelo menos uma fase da operação" in source_html
