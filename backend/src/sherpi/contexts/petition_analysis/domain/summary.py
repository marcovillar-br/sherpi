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
    ACTIVE = "ACTIVE"
    PASSIVE = "PASSIVE"


class ClaimType(StrEnum):
    MAIN = "MAIN"
    INJUNCTION = "INJUNCTION"
    SUBSIDIARY = "SUBSIDIARY"


class Parte(BaseModel):
    """Uma parte do processo (polo ativo ou passivo)."""

    name: str
    document: str | None = Field(default=None, description="CPF ou CNPJ como aparece no texto")
    pole: Polo
    address: str | None = None


class Pedido(BaseModel):
    """Um pedido formulado na petição."""

    description: str
    type: ClaimType = ClaimType.MAIN
    amount: str | None = Field(
        default=None,
        description=(
            "Valor do pedido como texto (ex.: 'R$ 5.000,00'), quando informado. "
            "Relevante para o pedido líquido do rito trabalhista (CLT 840 §1º)."
        ),
    )


class PetitionSummary(BaseModel):
    """Sumário executivo estruturado da petição inicial (art. 319 do CPC)."""

    court: str | None = Field(
        default=None, description="Juízo a que é dirigida / endereçamento (art. 319, I)"
    )
    parties: list[Parte] = Field(default_factory=list)
    facts: str = Field(description="Síntese objetiva dos fatos em um parágrafo (art. 319, III)")
    legal_basis: str = Field(
        description="Fundamentação jurídica invocada, sem cópia de jurisprudência (art. 319, III)"
    )
    claims: list[Pedido] = Field(default_factory=list)
    has_injunction: bool = Field(description="Há pedido de tutela de urgência/liminar?")
    claim_amount: str | None = Field(
        default=None, description="Valor da causa como texto (ex.: 'R$ 15.000,00') (art. 319, V)"
    )
    requests_evidence: bool = Field(
        default=False, description="O autor indica/protesta provar os fatos? (art. 319, VI)"
    )
    hearing_option: bool | None = Field(
        default=None,
        description="Manifestou opção por audiência de conciliação/mediação? (art. 319, VII)",
    )
    cited_documents: list[str] = Field(
        default_factory=list,
        description="Documentos citados/anexados (ex.: 'procuração', 'comprovante de residência')",
    )
