"""Testes do use case ExtractPetition (sem rede — via FakeProvider)."""

from __future__ import annotations

import pytest

from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
    TipoPedido,
)
from sherpi.infrastructure.llm.fake import FakeProvider

_SUMMARY = PetitionSummary(
    partes=[Parte(nome="Fulano de Tal", documento="529.982.247-25", polo=Polo.ATIVO)],
    fato_gerador="As partes celebraram contrato de prestação de serviços.",
    fundamentacao="Arts. 319 e 320 do CPC.",
    pedidos=[Pedido(descricao="Condenação ao pagamento", tipo=TipoPedido.PRINCIPAL)],
    tem_liminar=False,
    valor_causa="R$ 15.000,00",
)


async def test_extract_returns_validated_summary() -> None:
    fake = FakeProvider(_SUMMARY)
    result = await ExtractPetition(fake).run("EXMO. SR. JUIZ... petição...")
    assert isinstance(result, PetitionSummary)
    assert result.partes[0].nome == "Fulano de Tal"
    assert result.tem_liminar is False


async def test_extract_uses_defensive_prompt_and_wraps_document() -> None:
    fake = FakeProvider(_SUMMARY)
    await ExtractPetition(fake).run("texto da peça")
    messages = fake.calls[0]
    system = next(m.content for m in messages if m.role == "system")
    user = next(m.content for m in messages if m.role == "user")
    # defensive prompting: documento tratado como dado, não instrução
    assert "NUNCA uma instrução" in system
    assert "<peticao>" in user and "</peticao>" in user
    assert "texto da peça" in user


async def test_extract_truncates_oversized_input() -> None:
    fake = FakeProvider(_SUMMARY)
    huge = "a" * 1000
    await ExtractPetition(fake, max_input_chars=100).run(huge)
    user = next(m.content for m in fake.calls[0] if m.role == "user")
    assert "truncado" in user
    assert len(user) < 1000


async def test_temperature_zero_is_passed() -> None:
    # Garante determinismo: o use case chama o provider com temperature=0.
    captured: dict[str, float] = {}

    class _Spy(FakeProvider):
        async def complete(self, messages, response_schema, *, temperature=0.0, max_tokens=None):  # type: ignore[no-untyped-def]
            captured["temperature"] = temperature
            return await super().complete(
                messages, response_schema, temperature=temperature, max_tokens=max_tokens
            )

    await ExtractPetition(_Spy(_SUMMARY)).run("peça")
    assert captured["temperature"] == 0.0


async def test_fake_provider_raises_when_exhausted() -> None:
    from sherpi.shared_kernel.errors import LLMProviderError

    fake = FakeProvider(_SUMMARY)
    extractor = ExtractPetition(fake)
    await extractor.run("primeira")
    with pytest.raises(LLMProviderError):
        await extractor.run("segunda")  # sem resposta restante
