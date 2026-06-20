"""Detecção de PDF sem camada de texto (imagem/escaneado) — Nível 1 (sem OCR)."""

from __future__ import annotations

from synthetic.builder import build_clean, build_image_only, build_one

from sherpi.contexts.document_integrity.domain.detector import DetectInjection
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.shared_kernel.value_objects import RiskVerdict


def test_image_only_pdf_is_flagged_without_text() -> None:
    doc = PyMuPDFParser().parse(build_image_only(), max_pages=10)
    assert doc.visible_text().strip() == ""  # sem texto extraível
    assert doc.image_only_pages() == [0]  # página é imagem

    report = DetectInjection().run(doc)
    assert report.image_only_pages == [0]
    assert report.verdict is RiskVerdict.PASS  # imagem não é injeção — só não-analisável


def test_text_pdf_has_no_image_only_flag() -> None:
    doc = PyMuPDFParser().parse(build_clean(), max_pages=10)
    assert doc.image_only_pages() == []
    assert DetectInjection().run(doc).image_only_pages == []


def test_corpus_scanned_full_is_all_image() -> None:
    # Cenário rotulado do corpus: petição 100% imagem.
    doc = PyMuPDFParser().parse(build_one("scanned_acao_cobranca"), max_pages=10)
    assert doc.visible_text().strip() == ""
    assert doc.image_only_pages()  # ao menos uma página-imagem


def test_corpus_scanned_partial_has_both_text_and_image_pages() -> None:
    # Cenário parcial: página de texto extraível + página-imagem anexada.
    doc = PyMuPDFParser().parse(build_one("scanned_parcial"), max_pages=10)
    assert doc.visible_text().strip() != ""  # a página de texto é extraível
    flagged = doc.image_only_pages()
    assert flagged  # a página-imagem é sinalizada
    assert len(flagged) < doc.page_count  # mas nem todas as páginas são imagem
