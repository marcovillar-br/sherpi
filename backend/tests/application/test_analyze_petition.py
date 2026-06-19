"""Testes do orquestrador AnalyzePetition (PDF sintético + FakeProvider, sem rede)."""

from __future__ import annotations

import pytest
from synthetic.builder import build_injecao, build_integra

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.infrastructure.llm.fake import FakeProvider
from sherpi.shared_kernel.value_objects import RiskVerdict

_SUMMARY = PetitionSummary(
    partes=[
        Parte(nome="Fulano", documento="529.982.247-25", polo=Polo.ATIVO),
        Parte(nome="Empresa", documento="11.222.333/0001-81", polo=Polo.PASSIVO),
    ],
    fato_gerador="Contrato inadimplido.",
    fundamentacao="CPC.",
    pedidos=[Pedido(descricao="Pagamento")],
    tem_liminar=False,
    valor_causa="R$ 15.000,00",
    documentos_mencionados=["procuração"],
)


def _orchestrator(fake: FakeProvider) -> AnalyzePetition:
    return AnalyzePetition(PyMuPDFParser(), ExtractPetition(fake))


async def test_clean_petition_runs_full_pipeline() -> None:
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_integra(), max_pages=300)
    assert result.forensics.verdict is RiskVerdict.PASS
    assert result.summary is not None
    assert result.admissibility is not None
    assert len(fake.calls) == 1  # houve exatamente uma chamada de LLM


async def test_injection_blocks_before_llm() -> None:
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_injecao(), max_pages=300)
    assert result.blocked is True
    assert result.summary is None and result.admissibility is None
    assert fake.calls == []  # NENHUMA chamada de LLM no caminho bloqueado


async def test_non_pdf_rejected() -> None:
    from sherpi.shared_kernel.errors import UntrustedDocumentError

    with pytest.raises(UntrustedDocumentError):
        await _orchestrator(FakeProvider(_SUMMARY)).run(b"not a pdf", max_pages=300)


async def test_anonymizer_masks_pii_before_llm_but_admissibility_uses_original() -> None:
    from sherpi.infrastructure.anonymization.regex import RegexAnonymizer

    fake = FakeProvider(_SUMMARY)
    orchestrator = AnalyzePetition(
        PyMuPDFParser(), ExtractPetition(fake), anonymizer=RegexAnonymizer()
    )
    result = await orchestrator.run(build_integra(), max_pages=300)

    # O texto enviado ao LLM NÃO contém o CPF bruto (mascarado).
    user_msg = next(m.content for m in fake.calls[0] if m.role == "user")
    assert "529.982.247-25" not in user_msg
    assert "[CPF]" in user_msg

    # Ainda assim a admissibilidade valida o CPF a partir do texto ORIGINAL.
    qualificacao = next(
        i for i in result.admissibility.itens if i.requisito.value == "qualificacao"
    )
    assert qualificacao.presente is True
