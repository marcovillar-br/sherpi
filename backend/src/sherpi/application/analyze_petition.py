"""Orquestrador `AnalyzePetition` — o pipeline do MVP (substitui o LangGraph).

Use case explícito que compõe os bounded contexts em um fluxo linear com um
único *early-exit*:

    firewall (DetectInjection) -> [BLOCK? encerra] -> anonimiza -> extrai -> admissibilidade

Regra inegociável: se o firewall retornar BLOCK, o fluxo encerra **sem nenhuma
chamada de LLM**. O orquestrador é assíncrono (a extração via LLM é async).
"""

from __future__ import annotations

from pydantic import BaseModel

from sherpi.application.deanonymize import deanonymize_model
from sherpi.contexts.document_integrity.application.analyze import guard_upload
from sherpi.contexts.document_integrity.application.ports import DocumentParser
from sherpi.contexts.document_integrity.domain.detector import DetectInjection
from sherpi.contexts.document_integrity.domain.report import ForensicsReport
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.admissibility import (
    AdmissibilityReport,
    CheckAdmissibility,
)
from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary
from sherpi.contexts.taxonomy.application.suggest_tpu import SuggestTpu
from sherpi.contexts.taxonomy.domain.tpu import TpuSuggestion
from sherpi.shared_kernel.ports import ReversibleAnonymizer
from sherpi.shared_kernel.value_objects import Rito


class AnalysisResult(BaseModel):
    """Resultado consolidado da análise de uma petição.

    Quando `forensics.verdict == BLOCK`, `summary` e `admissibility` são None
    (o fluxo encerrou antes do LLM).
    """

    model_config = {"frozen": True}

    rito: Rito = Rito.CIVEL
    forensics: ForensicsReport
    summary: PetitionSummary | None = None
    admissibility: AdmissibilityReport | None = None
    tpu_suggestions: list[TpuSuggestion] | None = None

    @property
    def blocked(self) -> bool:
        return self.forensics.blocked


class AnalyzePetition:
    def __init__(
        self,
        parser: DocumentParser,
        extractor: ExtractPetition,
        *,
        detector: DetectInjection | None = None,
        admissibility: CheckAdmissibility | None = None,
        anonymizer: ReversibleAnonymizer | None = None,
        suggest_tpu: SuggestTpu | None = None,
    ) -> None:
        self._parser = parser
        self._extractor = extractor
        self._detector = detector or DetectInjection()
        self._admissibility = admissibility or CheckAdmissibility()
        self._anonymizer = anonymizer
        self._suggest_tpu = suggest_tpu

    async def run(
        self, content: bytes, *, max_pages: int, rito: Rito = Rito.CIVEL
    ) -> AnalysisResult:
        guard_upload(content)
        document = self._parser.parse(content, max_pages=max_pages)
        forensics = self._detector.run(document)
        if forensics.blocked:
            return AnalysisResult(rito=rito, forensics=forensics)  # early-exit: sem LLM

        original_text = document.visible_text()
        if not original_text.strip():
            # Sem texto extraível (provável documento-imagem/escaneado): não há o que
            # analisar cognitivamente. O laudo sinaliza via forensics.image_only_pages.
            return AnalysisResult(rito=rito, forensics=forensics)
        # O texto que vai ao LLM externo é anonimizado (LGPD); guardamos o mapa para
        # restaurar os valores reais no resumo do revisor (a admissibilidade já usa o
        # original). O prompt persistido para auditoria permanece anonimizado.
        if self._anonymizer is not None:
            llm_text, pii_map = self._anonymizer.anonymize_mapped(original_text)
        else:
            llm_text, pii_map = original_text, {}
        summary = await self._extractor.run(llm_text)
        summary = deanonymize_model(summary, pii_map)  # restaura nome/CPF/CNPJ reais
        admissibility = self._admissibility.run(summary, rito, raw_text=original_text)
        tpu_suggestions: list[TpuSuggestion] | None = None
        if self._suggest_tpu is not None:
            tpu_suggestions = self._suggest_tpu.run(original_text, rito=rito)
        return AnalysisResult(
            rito=rito,
            forensics=forensics,
            summary=summary,
            admissibility=admissibility,
            tpu_suggestions=tpu_suggestions,
        )
