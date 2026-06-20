"""Use case: análise de integridade documental (o firewall em ação)."""

from __future__ import annotations

from typing import Literal

from sherpi.contexts.document_integrity.application.ports import DocumentParser
from sherpi.contexts.document_integrity.domain.detector import DetectInjection
from sherpi.contexts.document_integrity.domain.report import ForensicsReport
from sherpi.shared_kernel.errors import UntrustedDocumentError

_PDF_MAGIC = b"%PDF-"
_ZIP_MAGIC = b"PK\x03\x04"  # OOXML (.docx) é um zip; o parser valida o conteúdo

DocumentFormat = Literal["pdf", "docx"]


def detect_format(content: bytes) -> DocumentFormat:
    """Identifica o formato pelo *magic number*. Levanta se não for suportado."""
    if content.startswith(_PDF_MAGIC):
        return "pdf"
    if content.startswith(_ZIP_MAGIC):
        return "docx"
    raise UntrustedDocumentError("Arquivo não suportado (esperado PDF ou DOCX).")


def guard_upload(content: bytes) -> None:
    """Validação barata de upload (defesa contra arquivo hostil), antes do parser.

    Reutilizada pelo firewall e pelo orquestrador.
    """
    if not content:
        raise UntrustedDocumentError("Arquivo vazio.")
    detect_format(content)  # levanta UntrustedDocumentError se o formato não for suportado


class AnalyzeDocumentIntegrity:
    """Orquestra: valida upload → parseia → detecta manipulação.

    É a primeira barreira do pipeline. Um veredito BLOCK encerra o fluxo ANTES
    de qualquer gasto de token com LLM.
    """

    def __init__(self, parser: DocumentParser, detector: DetectInjection | None = None) -> None:
        self._parser = parser
        self._detector = detector or DetectInjection()

    def run(self, content: bytes, *, max_pages: int) -> ForensicsReport:
        guard_upload(content)
        document = self._parser.parse(content, max_pages=max_pages)
        return self._detector.run(document)
