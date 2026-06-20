"""Testes do PersistingLLMProvider (auditoria durável das chamadas ao LLM)."""

from __future__ import annotations

import structlog
from pydantic import BaseModel

from sherpi.infrastructure.llm.audit_store import LLMCall, PersistingLLMProvider
from sherpi.shared_kernel.ports import ChatMessage, TModel


class _Out(BaseModel):
    ok: bool = True


class _FakeInner:
    model = "fake-model"

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        return response_schema.model_validate(_Out().model_dump())


class _MemRepo:
    def __init__(self) -> None:
        self.calls: list[LLMCall] = []

    def append(self, call: LLMCall) -> None:
        self.calls.append(call)

    def list_by_analysis(self, analysis_id: str) -> list[LLMCall]:
        return [c for c in self.calls if c.analysis_id == analysis_id]


async def test_persists_call_with_analysis_id_from_contextvars() -> None:
    repo = _MemRepo()
    provider = PersistingLLMProvider(_FakeInner(), repo, label="extract")
    structlog.contextvars.bind_contextvars(analysis_id="a-123")
    try:
        await provider.complete([ChatMessage(role="user", content="petição")], _Out)
    finally:
        structlog.contextvars.clear_contextvars()

    assert len(repo.calls) == 1
    call = repo.calls[0]
    assert call.analysis_id == "a-123"
    assert call.call_type == "extract"
    assert call.model == "fake-model"
    assert "petição" in call.prompt
    assert call.prompt_chars > 0
    assert call.response_chars > 0


async def test_analysis_id_none_when_unbound() -> None:
    structlog.contextvars.clear_contextvars()
    repo = _MemRepo()
    await PersistingLLMProvider(_FakeInner(), repo).complete(
        [ChatMessage(role="user", content="x")], _Out
    )
    assert repo.calls[0].analysis_id is None


async def test_persist_failure_does_not_break_the_call() -> None:
    class _BadRepo:
        def append(self, call: LLMCall) -> None:
            raise RuntimeError("db down")

        def list_by_analysis(self, analysis_id: str) -> list[LLMCall]:
            return []

    result = await PersistingLLMProvider(_FakeInner(), _BadRepo()).complete(
        [ChatMessage(role="user", content="x")], _Out
    )
    # Best-effort: a falha de auditoria não derruba a análise.
    assert result.ok is True
