"""Parser que despacha por formato (PDF → PyMuPDF, DOCX → python-docx).

Implementa o port `DocumentParser` compondo os adapters concretos. O resto do
pipeline (firewall, anonimização, extração, admissibilidade, TPU) é agnóstico ao
formato — só esta peça e os parsers conhecem PDF vs DOCX.
"""

from __future__ import annotations

from sherpi.contexts.document_integrity.application.analyze import detect_format
from sherpi.contexts.document_integrity.application.ports import DocumentParser
from sherpi.contexts.document_integrity.domain.document import ParsedDocument


class DispatchingParser:
    """Seleciona o parser pelo *magic number* do conteúdo."""

    def __init__(self, pdf: DocumentParser, docx: DocumentParser) -> None:
        self._pdf = pdf
        self._docx = docx

    def parse(self, content: bytes, *, max_pages: int) -> ParsedDocument:
        parser = self._pdf if detect_format(content) == "pdf" else self._docx
        return parser.parse(content, max_pages=max_pages)
