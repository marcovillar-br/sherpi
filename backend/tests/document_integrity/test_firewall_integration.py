"""Testes de integração do firewall, dirigidos pela massa de cenários.

Cada cenário do catálogo sintético (clean/defect/injection) é exercitado e o
veredito do firewall é comparado ao *ground truth* (`expected_verdict`).
"""

from __future__ import annotations

import pytest
from synthetic.builder import SyntheticPetition, build_clean, build_corpus

from sherpi.contexts.document_integrity.application.analyze import AnalyzeDocumentIntegrity
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.shared_kernel.errors import UntrustedDocumentError

_CORPUS = build_corpus()


@pytest.fixture
def firewall() -> AnalyzeDocumentIntegrity:
    return AnalyzeDocumentIntegrity(PyMuPDFParser())


@pytest.mark.parametrize("petition", _CORPUS, ids=[p.name for p in _CORPUS])
def test_firewall_verdict_matches_scenario(
    firewall: AnalyzeDocumentIntegrity, petition: SyntheticPetition
) -> None:
    report = firewall.run(petition.content, max_pages=300)
    assert report.verdict.value == petition.expected_verdict
    # Injeções devem produzir risco > 0; cenários limpos/defeituosos, risco zero.
    if petition.is_malicious:
        assert report.risk_score > 0.0
    else:
        assert report.risk_score == 0.0


def test_corpus_cobre_categorias_variadas() -> None:
    categorias = {p.category for p in _CORPUS}
    assert categorias == {"clean", "defect", "injection", "trabalhista", "scanned"}
    assert sum(p.is_malicious for p in _CORPUS) >= 4  # ao menos os 4 vetores de injeção


def test_non_pdf_is_rejected(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(b"isto nao e um pdf", max_pages=300)


def test_empty_upload_is_rejected(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(b"", max_pages=300)


def test_page_limit_is_enforced(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(build_clean(), max_pages=0)
