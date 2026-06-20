"""Integração: litisconsórcio (multi-parte) — parser → visible_text → anonimização.

Exercita a cadeia real (PDF → spans por bloco → mascaramento) num cenário com 2
autores e 2 rés, garantindo que NENHUM nome/identificador vaze para o LLM.
"""

from __future__ import annotations

import re

from synthetic.builder import build_one

from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.infrastructure.anonymization.regex import (
    CompositeAnonymizer,
    RegexAnonymizer,
    RegexNameAnonymizer,
)

_NAMES = ("FULANO", "BELTRANA", "SOUZA", "EMPRESA ALFA", "EMPRESA BETA", "ALFA", "BETA")


def test_litisconsorcio_pdf_is_fully_anonymized() -> None:
    pdf = build_one("clean_litisconsorcio")
    text = PyMuPDFParser().parse(pdf, max_pages=10).visible_text()
    anon = CompositeAnonymizer([RegexAnonymizer(), RegexNameAnonymizer()]).anonymize(text)

    # Nenhum nome das partes (2 autores, 2 rés) vaza.
    for name in _NAMES:
        assert name not in anon, f"vazou: {name}"
    # Nenhum CPF/CNPJ cru.
    assert not re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", anon)
    assert not re.search(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", anon)
    # Mascarou de fato (múltiplos [NOME]) e preservou a estrutura.
    assert anon.count("[NOME]") >= 2
    assert "VARA CÍVEL" in anon
    assert "AÇÃO DE COBRANÇA" in anon
