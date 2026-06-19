"""Resumo estruturado de uma petição inicial (saída da extração).

Estes modelos são o **contrato de saída** do use case `ExtractPetition` e o
schema de saída forçado no LLM. São intencionalmente **tolerantes** (campos como
documento/valor da causa ficam como texto bruto): a extração é semântica e não
deve falhar por ruído do modelo. A **validação estrita** (checksum de CPF/CNPJ,
parsing do valor) é responsabilidade do `CheckAdmissibility` (Sprint 2), que usa
os Value Objects do `shared_kernel` — separando extração de validação.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Polo(StrEnum):
    ATIVO = "ATIVO"
    PASSIVO = "PASSIVO"


class TipoPedido(StrEnum):
    PRINCIPAL = "PRINCIPAL"
    LIMINAR = "LIMINAR"
    SUBSIDIARIO = "SUBSIDIARIO"


class Parte(BaseModel):
    """Uma parte do processo (polo ativo ou passivo)."""

    nome: str
    documento: str | None = Field(default=None, description="CPF ou CNPJ como aparece no texto")
    polo: Polo
    endereco: str | None = None


class Pedido(BaseModel):
    """Um pedido formulado na petição."""

    descricao: str
    tipo: TipoPedido = TipoPedido.PRINCIPAL


class PetitionSummary(BaseModel):
    """Sumário executivo estruturado da petição inicial."""

    partes: list[Parte] = Field(default_factory=list)
    fato_gerador: str = Field(description="Síntese objetiva dos fatos em um parágrafo")
    fundamentacao: str = Field(
        description="Fundamentação jurídica invocada, sem cópia de jurisprudência"
    )
    pedidos: list[Pedido] = Field(default_factory=list)
    tem_liminar: bool = Field(description="Há pedido de tutela de urgência/liminar?")
    valor_causa: str | None = Field(
        default=None, description="Valor da causa como texto (ex.: 'R$ 15.000,00')"
    )
