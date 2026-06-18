"""Testes de integração do firewall: PDF sintético → parser → detector."""

from __future__ import annotations

import pytest
from synthetic.builder import BUILDERS, build_clean, build_corpus

from sherpi.contexts.document_integrity.application.analyze import AnalyzeDocumentIntegrity
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.shared_kernel.errors import UntrustedDocumentError
from sherpi.shared_kernel.value_objects import RiskVerdict


@pytest.fixture
def firewall() -> AnalyzeDocumentIntegrity:
    return AnalyzeDocumentIntegrity(PyMuPDFParser())


def test_clean_petition_passes(firewall: AnalyzeDocumentIntegrity) -> None:
    report = firewall.run(build_clean(), max_pages=300)
    assert report.verdict is RiskVerdict.PASS


@pytest.mark.parametrize(
    "name",
    [n for n, (_, malicious, _) in BUILDERS.items() if malicious],
)
def test_each_injection_vector_is_blocked(firewall: AnalyzeDocumentIntegrity, name: str) -> None:
    corpus = {p.name: p for p in build_corpus()}
    report = firewall.run(corpus[name].content, max_pages=300)
    assert report.verdict in (RiskVerdict.BLOCK, RiskVerdict.WARN), name
    assert report.risk_score > 0.0


def test_non_pdf_is_rejected(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(b"isto nao e um pdf", max_pages=300)


def test_empty_upload_is_rejected(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(b"", max_pages=300)


def test_page_limit_is_enforced(firewall: AnalyzeDocumentIntegrity) -> None:
    with pytest.raises(UntrustedDocumentError):
        firewall.run(build_clean(), max_pages=0)
