"""Testes do orquestrador AnalyzePetition (PDF sintético + FakeProvider, sem rede)."""

from __future__ import annotations

import pytest
from synthetic.builder import build_clean, build_image_only, build_one, build_white_on_white

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
    parties=[
        Parte(name="Fulano", document="529.982.247-25", pole=Polo.ACTIVE),
        Parte(name="Empresa", document="11.222.333/0001-81", pole=Polo.PASSIVE),
    ],
    facts="Contrato inadimplido.",
    legal_basis="CPC.",
    claims=[Pedido(description="Pagamento")],
    has_injunction=False,
    claim_amount="R$ 15.000,00",
    cited_documents=["procuração"],
)


def _orchestrator(fake: FakeProvider) -> AnalyzePetition:
    return AnalyzePetition(PyMuPDFParser(), ExtractPetition(fake))


async def test_clean_petition_runs_full_pipeline() -> None:
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_clean(), max_pages=300)
    assert result.forensics.verdict is RiskVerdict.PASS
    assert result.summary is not None
    assert result.admissibility is not None
    assert len(fake.calls) == 1  # houve exatamente uma chamada de LLM


async def test_injection_blocks_before_llm() -> None:
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_white_on_white(), max_pages=300)
    assert result.blocked is True
    assert result.summary is None and result.admissibility is None
    assert fake.calls == []  # NENHUMA chamada de LLM no caminho bloqueado


async def test_image_only_pdf_skips_extraction() -> None:
    # Documento sem texto (imagem/escaneado): firewall não bloqueia, mas a extração
    # é pulada (sem LLM) e o laudo sinaliza as páginas-imagem.
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_image_only(), max_pages=300)
    assert result.blocked is False
    assert result.summary is None and result.admissibility is None
    assert result.forensics.image_only_pages == [0]
    assert fake.calls == []  # nada a extrair → nenhuma chamada de LLM


async def test_mixed_page_warns_but_still_extracts() -> None:
    # Página mista (texto + imagem dominante): a extração do texto disponível
    # prossegue, mas o laudo avisa que pode haver conteúdo embutido na imagem.
    fake = FakeProvider(_SUMMARY)
    result = await _orchestrator(fake).run(build_one("scanned_mista"), max_pages=300)
    assert result.forensics.image_heavy_pages  # avisa
    assert not result.forensics.image_only_pages
    assert result.summary is not None  # ainda extrai (há texto)
    assert len(fake.calls) == 1


async def test_non_pdf_rejected() -> None:
    from sherpi.shared_kernel.errors import UntrustedDocumentError

    with pytest.raises(UntrustedDocumentError):
        await _orchestrator(FakeProvider(_SUMMARY)).run(b"not a pdf", max_pages=300)


async def test_anonymizer_masks_pii_before_llm_but_admissibility_uses_original() -> None:
    from sherpi.infrastructure.anonymization.regex import MappedRegexAnonymizer

    fake = FakeProvider(_SUMMARY)
    orchestrator = AnalyzePetition(
        PyMuPDFParser(), ExtractPetition(fake), anonymizer=MappedRegexAnonymizer()
    )
    result = await orchestrator.run(build_clean(), max_pages=300)

    # O texto enviado ao LLM NÃO contém o CPF bruto (mascarado, numerado).
    user_msg = next(m.content for m in fake.calls[0] if m.role == "user")
    assert "529.982.247-25" not in user_msg
    assert "[CPF_1]" in user_msg
    assert result.summary is not None


async def test_summary_restores_real_pii_for_human_reviewer() -> None:
    # A LLM recebe placeholders, mas o RESUMO exibido ao revisor deve trazer os
    # valores reais de volta (anonimização é só para o LLM externo).
    from sherpi.contexts.petition_analysis.domain.summary import Parte, PetitionSummary, Polo
    from sherpi.infrastructure.anonymization.regex import (
        MappedCompositeAnonymizer,
        MappedRegexAnonymizer,
        MappedRegexNameAnonymizer,
    )

    anonymizer = MappedCompositeAnonymizer([MappedRegexAnonymizer(), MappedRegexNameAnonymizer()])
    # Descobre os placeholders reais que a anonimização produz para esta peça.
    text = PyMuPDFParser().parse(build_clean(), max_pages=300).visible_text()
    _, mapping = anonymizer.anonymize_mapped(text)
    cpf_ph = next(k for k in mapping if k.startswith("[CPF"))
    nome_ph = next(k for k in mapping if k.startswith("[NOME"))

    # A "LLM" devolve um resumo COM placeholders (como aconteceria de fato).
    echoed = PetitionSummary(
        parties=[Parte(name=nome_ph, document=cpf_ph, pole=Polo.ACTIVE)],
        facts=f"O autor {nome_ph} (CPF {cpf_ph}) cobra a dívida.",
        legal_basis="CPC.",
        has_injunction=False,
    )
    orchestrator = AnalyzePetition(
        PyMuPDFParser(), ExtractPetition(FakeProvider(echoed)), anonymizer=anonymizer
    )
    result = await orchestrator.run(build_clean(), max_pages=300)

    assert result.summary is not None
    assert result.summary.parties[0].name == mapping[nome_ph]  # nome real restaurado
    assert result.summary.parties[0].document == mapping[cpf_ph]  # CPF real restaurado
    assert "[NOME" not in result.summary.facts and "[CPF" not in result.summary.facts

    # Ainda assim a admissibilidade valida o CPF a partir do texto ORIGINAL.
    qualification = next(
        i for i in result.admissibility.items if i.requirement.value == "qualification"
    )
    assert qualification.present is True
