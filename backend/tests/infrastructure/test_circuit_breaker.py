"""Testes do CircuitBreakerLLMProvider (clock injetável, sem rede nem sleep)."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from sherpi.infrastructure.llm.circuit_breaker import CircuitBreakerLLMProvider
from sherpi.shared_kernel.errors import CircuitOpenError, LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel


class _Out(BaseModel):
    ok: bool = True


class _ScriptedProvider:
    """Provider que falha enquanto `fail` for True; conta as chamadas reais."""

    def __init__(self) -> None:
        self.fail = False
        self.calls = 0

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        self.calls += 1
        if self.fail:
            raise LLMProviderError("boom")
        return response_schema.model_validate(_Out().model_dump())


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


async def _call(breaker: CircuitBreakerLLMProvider) -> _Out:
    return await breaker.complete([ChatMessage(role="user", content="x")], _Out)


async def test_closed_passes_through_and_resets_on_success() -> None:
    inner = _ScriptedProvider()
    breaker = CircuitBreakerLLMProvider(inner, failure_threshold=3, clock=_Clock())
    inner.fail = True
    for _ in range(2):  # 2 falhas < limite de 3: circuito segue fechado
        with pytest.raises(LLMProviderError):
            await _call(breaker)
    inner.fail = False
    assert (await _call(breaker)).ok  # sucesso zera o contador
    inner.fail = True
    for _ in range(2):  # contador reiniciou: mais 2 falhas ainda não abrem
        with pytest.raises(LLMProviderError):
            await _call(breaker)
    assert inner.calls == 5  # todas as chamadas chegaram ao provider (nada curto-circuitado)


async def test_opens_after_threshold_and_fails_fast() -> None:
    inner = _ScriptedProvider()
    breaker = CircuitBreakerLLMProvider(inner, failure_threshold=3, clock=_Clock())
    inner.fail = True
    for _ in range(3):
        with pytest.raises(LLMProviderError):
            await _call(breaker)
    calls_at_open = inner.calls
    # Circuito aberto: falha rápido sem tocar no provider.
    with pytest.raises(CircuitOpenError):
        await _call(breaker)
    assert inner.calls == calls_at_open  # nenhuma chamada nova chegou ao provider


async def test_half_open_recovers_after_cooldown() -> None:
    clock = _Clock()
    inner = _ScriptedProvider()
    breaker = CircuitBreakerLLMProvider(inner, failure_threshold=2, reset_timeout=30.0, clock=clock)
    inner.fail = True
    for _ in range(2):
        with pytest.raises(LLMProviderError):
            await _call(breaker)
    # Antes do cooldown: ainda aberto.
    clock.t = 29.0
    with pytest.raises(CircuitOpenError):
        await _call(breaker)
    # Após o cooldown + provider saudável: half_open libera tentativa, sucesso fecha.
    clock.t = 31.0
    inner.fail = False
    assert (await _call(breaker)).ok


async def test_half_open_failure_reopens_immediately() -> None:
    clock = _Clock()
    inner = _ScriptedProvider()
    breaker = CircuitBreakerLLMProvider(inner, failure_threshold=2, reset_timeout=30.0, clock=clock)
    inner.fail = True
    for _ in range(2):
        with pytest.raises(LLMProviderError):
            await _call(breaker)
    clock.t = 31.0  # cooldown expirou → half_open
    with pytest.raises(LLMProviderError):
        await _call(breaker)  # tentativa de teste falha → reabre
    calls_after_trial = inner.calls
    clock.t = 31.5  # ainda dentro do novo cooldown
    with pytest.raises(CircuitOpenError):
        await _call(breaker)
    assert inner.calls == calls_after_trial  # reaberto: falha rápido de novo


def test_model_property_delegates_to_inner() -> None:
    inner = _ScriptedProvider()
    inner.model = "gemini-x"  # type: ignore[attr-defined]
    assert CircuitBreakerLLMProvider(inner).model == "gemini-x"


def test_model_property_none_when_inner_has_no_model() -> None:
    assert CircuitBreakerLLMProvider(_ScriptedProvider()).model is None
