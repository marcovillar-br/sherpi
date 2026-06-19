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
from sherpi.shared_kernel.value_objects import CNPJ, CPF, Rito, ValorCausa

if TYPE_CHECKING:
    from sherpi.contexts.petition_analysis.domain.strategies import AdmissibilityStrategy


class Semaforo(StrEnum):
    VERDE = "VERDE"  # apto a prosseguir
    AMARELO = "AMARELO"  # vícios sanáveis menores
    VERMELHO = "VERMELHO"  # requer emenda (art. 321)


class MetodoCheck(StrEnum):
    DETERMINISTICO = "DETERMINISTICO"
    SEMANTICO = "SEMANTICO"


class Requisito(StrEnum):
    JUIZO = "juizo"  # art. 319, I
    PARTES = "partes"  # art. 319, II
    QUALIFICACAO = "qualificacao"  # art. 319, II
    FATOS = "fatos"  # art. 319, III
    FUNDAMENTACAO = "fundamentacao"  # art. 319, III
    PEDIDOS = "pedidos"  # art. 319, IV
    VALOR_CAUSA = "valor_causa"  # art. 319, V
    PROVAS = "provas"  # art. 319, VI
    AUDIENCIA = "audiencia"  # art. 319, VII
    DOCUMENTOS = "documentos"  # art. 320 (procuração etc.)
    PEDIDO_LIQUIDO = "pedido_liquido"  # CLT art. 840 §1º (rito trabalhista)


# Requisitos essenciais cuja ausência exige emenda (art. 321 / CLT 840) → VERMELHO.
# PEDIDO_LIQUIDO só é emitido pela estratégia trabalhista; nos demais ritos o item
# nunca aparece, então incluí-lo aqui é inócuo para o cível.
_ESSENCIAIS = {
    Requisito.PARTES,
    Requisito.FATOS,
    Requisito.PEDIDOS,
    Requisito.VALOR_CAUSA,
    Requisito.PEDIDO_LIQUIDO,
}

# Candidatos a CPF/CNPJ no texto bruto (validação por checksum vem depois).
_CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


class ChecklistItem(BaseModel):
    model_config = {"frozen": True}

    requisito: Requisito
    presente: bool
    metodo: MetodoCheck
    evidencia: str | None = None
    detalhe: str | None = None


class AdmissibilityReport(BaseModel):
    model_config = {"frozen": True}

    itens: list[ChecklistItem]
    semaforo: Semaforo
    requer_emenda: bool

    @classmethod
    def from_items(cls, itens: list[ChecklistItem]) -> AdmissibilityReport:
        ausentes = {i.requisito for i in itens if not i.presente}
        requer_emenda = bool(ausentes & _ESSENCIAIS)
        if requer_emenda:
            semaforo = Semaforo.VERMELHO
        elif ausentes:
            semaforo = Semaforo.AMARELO
        else:
            semaforo = Semaforo.VERDE
        return cls(itens=itens, semaforo=semaforo, requer_emenda=requer_emenda)


def parse_valor_causa(texto: str | None) -> ValorCausa | None:
    """Converte 'R$ 15.000,00' (ou variações) em `ValorCausa`. None se não parseável."""
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
        return ValorCausa(amount=amount)
    except ValueError:
        return None


def _valid_documento(value: str | None) -> str | None:
    """Retorna o documento formatado se for CPF ou CNPJ válido; senão None."""
    if not value:
        return None
    for vo in (CPF, CNPJ):
        try:
            return vo(value=value).formatted
        except ValueError:
            continue
    return None


def _scan_valid_documento(text: str) -> str | None:
    """Procura no texto bruto o primeiro CPF/CNPJ com checksum válido."""
    for pattern in (_CNPJ_RE, _CPF_RE):
        for match in pattern.finditer(text):
            doc = _valid_documento(match.group())
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
