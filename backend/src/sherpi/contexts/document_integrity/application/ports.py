"""Ports do contexto Document Integrity."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.document_integrity.domain.document import ParsedDocument


@runtime_checkable
class DocumentParser(Protocol):
    """Extrai a estrutura forense de um documento (PDF ou DOCX).

    O adapter deve preservar os atributos de que o detector depende — cor e tamanho
    da fonte, texto oculto, metadados (e, no PDF, posição/camadas/`/ActualText`).
    Deve respeitar `max_pages` e levantar `UntrustedDocumentError` para entrada inválida.
    """

    def parse(self, content: bytes, *, max_pages: int) -> ParsedDocument: ...
