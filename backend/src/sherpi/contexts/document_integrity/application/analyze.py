"""Use case: análise de integridade documental (o firewall em ação)."""

from __future__ import annotations

from sherpi.contexts.document_integrity.application.ports import PdfParser
from sherpi.contexts.document_integrity.domain.detector import DetectInjection
from sherpi.contexts.document_integrity.domain.report import ForensicsReport
from sherpi.shared_kernel.errors import UntrustedDocumentError

_PDF_MAGIC = b"%PDF-"


def guard_upload(content: bytes) -> None:
    """Validação barata de upload (defesa contra arquivo hostil), antes do parser.

    Reutilizada pelo firewall e pelo orquestrador.
    """
    if not content:
        raise UntrustedDocumentError("Arquivo vazio.")
    if not content.startswith(_PDF_MAGIC):
        raise UntrustedDocumentError("Arquivo não é um PDF válido (assinatura ausente).")


class AnalyzeDocumentIntegrity:
    """Orquestra: valida upload → parseia → detecta manipulação.

    É a primeira barreira do pipeline. Um veredito BLOCK encerra o fluxo ANTES
    de qualquer gasto de token com LLM.
    """

    def __init__(self, parser: PdfParser, detector: DetectInjection | None = None) -> None:
        self._parser = parser
        self._detector = detector or DetectInjection()

    def run(self, content: bytes, *, max_pages: int) -> ForensicsReport:
        guard_upload(content)
        document = self._parser.parse(content, max_pages=max_pages)
        return self._detector.run(document)
