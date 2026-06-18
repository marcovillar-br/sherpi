"""Ports do contexto Document Integrity."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.document_integrity.domain.document import ParsedDocument


@runtime_checkable
class PdfParser(Protocol):
    """Extrai a estrutura forense de um PDF.

    O adapter (PyMuPDF) deve preservar atributos visuais (cor, tamanho, posição,
    camadas, /ActualText, metadados) — é deles que o detector depende. Deve
    respeitar `max_pages` e levantar `UntrustedDocumentError` para entrada inválida.
    """

    def parse(self, content: bytes, *, max_pages: int) -> ParsedDocument: ...
