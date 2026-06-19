"""Orquestrador `AnalyzePetition` — o pipeline do MVP (substitui o LangGraph).

Use case explícito que compõe os bounded contexts em um fluxo linear com um
único *early-exit*:

    firewall (DetectInjection) -> [BLOCK? encerra] -> anonimiza -> extrai -> admissibilidade

Regra inegociável: se o firewall retornar BLOCK, o fluxo encerra **sem nenhuma
chamada de LLM**. O orquestrador é assíncrono (a extração via LLM é async).
"""

from __future__ import annotations

from pydantic import BaseModel

from sherpi.contexts.document_integrity.application.analyze import guard_upload
from sherpi.contexts.document_integrity.application.ports import PdfParser
from sherpi.contexts.document_integrity.domain.detector import DetectInjection
from sherpi.contexts.document_integrity.domain.report import ForensicsReport
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.admissibility import (
    AdmissibilityReport,
    CheckAdmissibility,
)
from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary
from sherpi.shared_kernel.ports import Anonymizer


class AnalysisResult(BaseModel):
    """Resultado consolidado da análise de uma petição.

    Quando `forensics.verdict == BLOCK`, `summary` e `admissibility` são None
    (o fluxo encerrou antes do LLM).
    """

    model_config = {"frozen": True}

    forensics: ForensicsReport
    summary: PetitionSummary | None = None
    admissibility: AdmissibilityReport | None = None

    @property
    def blocked(self) -> bool:
        return self.forensics.blocked


class AnalyzePetition:
    def __init__(
        self,
        parser: PdfParser,
        extractor: ExtractPetition,
        *,
        detector: DetectInjection | None = None,
        admissibility: CheckAdmissibility | None = None,
        anonymizer: Anonymizer | None = None,
    ) -> None:
        self._parser = parser
        self._extractor = extractor
        self._detector = detector or DetectInjection()
        self._admissibility = admissibility or CheckAdmissibility()
        self._anonymizer = anonymizer

    async def run(self, content: bytes, *, max_pages: int) -> AnalysisResult:
        guard_upload(content)
        document = self._parser.parse(content, max_pages=max_pages)
        forensics = self._detector.run(document)
        if forensics.blocked:
            return AnalysisResult(forensics=forensics)  # early-exit: sem LLM

        text = document.visible_text()
        if self._anonymizer is not None:
            text = self._anonymizer.anonymize(text)
        summary = await self._extractor.run(text)
        admissibility = self._admissibility.run(summary)
        return AnalysisResult(forensics=forensics, summary=summary, admissibility=admissibility)
