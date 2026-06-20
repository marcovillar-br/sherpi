"""Checagem de admissibilidade da petição inicial (arts. 319/321 do CPC).

Domain service **puro**: opera sobre o `PetitionSummary` extraído e produz um
`AdmissibilityReport`. Separa explicitamente:
- **validadores determinísticos** (checksum de CPF/CNPJ, parsing do valor da causa,
  presença de campos) — confiáveis e exatos;
- **checagem semântica** (menção a documentos essenciais) — proveniente da extração.

Cada item carrega o método e a evidência (proveniência), atendendo à
interpretabilidade exigida.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary
from sherpi.shared_kernel.value_objects import CNPJ, CPF, ClaimAmount, Rito

if TYPE_CHECKING:
    from sherpi.contexts.petition_analysis.domain.strategies import AdmissibilityStrategy


class AdmissibilityStatus(StrEnum):
    GREEN = "GREEN"  # apto a prosseguir
    YELLOW = "YELLOW"  # vícios sanáveis menores
    RED = "RED"  # requer emenda (art. 321)


class CheckMethod(StrEnum):
    DETERMINISTIC = "DETERMINISTIC"
    SEMANTIC = "SEMANTIC"


class Requirement(StrEnum):
    COURT = "court"  # art. 319, I
    PARTIES = "parties"  # art. 319, II
    QUALIFICATION = "qualification"  # art. 319, II
    FACTS = "facts"  # art. 319, III
    LEGAL_BASIS = "legal_basis"  # art. 319, III
    CLAIMS = "claims"  # art. 319, IV
    CLAIM_VALUE = "claim_value"  # art. 319, V
    EVIDENCE = "evidence"  # art. 319, VI
    HEARING = "hearing"  # art. 319, VII
    DOCUMENTS = "documents"  # art. 320 (procuração etc.)
    LIQUID_CLAIM = "liquid_claim"  # CLT art. 840 §1º (rito trabalhista)


# Requisitos essenciais cuja ausência exige emenda (art. 321 / CLT 840) → RED.
# LIQUID_CLAIM só é emitido pela estratégia trabalhista; nos demais ritos o item
# nunca aparece, então incluí-lo aqui é inócuo para o cível.
_ESSENTIAL_REQS = {
    Requirement.PARTIES,
    Requirement.FACTS,
    Requirement.CLAIMS,
    Requirement.CLAIM_VALUE,
    Requirement.LIQUID_CLAIM,
}

# Candidatos a CPF/CNPJ no texto bruto (validação por checksum vem depois).
_CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


class ChecklistItem(BaseModel):
    model_config = {"frozen": True}

    requirement: Requirement
    present: bool
    method: CheckMethod
    evidence: str | None = None
    detail: str | None = None
    # Alerta ao revisor: o campo foi extraído, mas o marcador formal correspondente
    # não foi localizado no texto bruto — pode ter sido inferido da narrativa pelo LLM.
    # NÃO altera o veredito; é sinal de "confirme na peça original" (human-in-the-loop).
    caveat: str | None = None


class AdmissibilityReport(BaseModel):
    model_config = {"frozen": True}

    items: list[ChecklistItem]
    status: AdmissibilityStatus
    requires_amendment: bool

    @classmethod
    def from_items(cls, items: list[ChecklistItem]) -> AdmissibilityReport:
        missing = {i.requirement for i in items if not i.present}
        requires_amendment = bool(missing & _ESSENTIAL_REQS)
        if requires_amendment:
            status = AdmissibilityStatus.RED
        elif missing:
            status = AdmissibilityStatus.YELLOW
        else:
            status = AdmissibilityStatus.GREEN
        return cls(items=items, status=status, requires_amendment=requires_amendment)


def parse_claim_amount(texto: str | None) -> ClaimAmount | None:
    """Converte 'R$ 15.000,00' (ou variações) em `ClaimAmount`. None se não parseável."""
    if not texto:
        return None
    raw = re.sub(r"[^0-9,.]", "", texto)
    if not raw:
        return None
    # Formato brasileiro: '.' separa milhar e ',' separa decimal.
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    try:
        return ClaimAmount(amount=amount)
    except ValueError:
        return None


def _valid_document(value: str | None) -> str | None:
    """Retorna o documento formatado se for CPF ou CNPJ válido; senão None."""
    if not value:
        return None
    for vo in (CPF, CNPJ):
        try:
            return vo(value=value).formatted
        except ValueError:
            continue
    return None


def _scan_valid_document(text: str) -> str | None:
    """Procura no texto bruto o primeiro CPF/CNPJ com checksum válido."""
    for pattern in (_CNPJ_RE, _CPF_RE):
        for match in pattern.finditer(text):
            doc = _valid_document(match.group())
            if doc:
                return doc
    return None


class CheckAdmissibility:
    """Domain service: despacha a admissibilidade para a estratégia do rito.

    As regras de cada rito vivem em `AdmissibilityStrategy` (ver `strategies.py`);
    este serviço apenas roteia `Rito → estratégia`. O cível é o rito padrão (ADR-0008).
    """

    def __init__(self, strategies: dict[Rito, AdmissibilityStrategy] | None = None) -> None:
        if strategies is None:
            # Import tardio para evitar ciclo: strategies.py importa os tipos deste módulo.
            from sherpi.contexts.petition_analysis.domain.strategies import DEFAULT_STRATEGIES

            strategies = DEFAULT_STRATEGIES
        self._strategies = strategies

    def run(
        self,
        summary: PetitionSummary,
        rito: Rito = Rito.CIVEL,
        *,
        raw_text: str | None = None,
    ) -> AdmissibilityReport:
        """Avalia a admissibilidade segundo o `rito`.

        Se `raw_text` (texto ORIGINAL, não anonimizado) for fornecido, a validação
        de CPF/CNPJ roda sobre ele — assim o mascaramento de PII para o LLM não
        degrada a checagem determinística.
        """
        return self._strategies[rito].run(summary, raw_text=raw_text)
