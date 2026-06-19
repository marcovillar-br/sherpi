"""`FakeProvider` — adapter de LLM determinístico, sem rede, para testes.

Devolve respostas pré-definidas (validadas contra o `response_schema`) e registra
as mensagens recebidas, permitindo asserts sobre o prompt sem chamar nenhuma API.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel

from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel


class FakeProvider:
    """Implementação fake do port `LLMProvider`."""

    def __init__(self, responses: BaseModel | Sequence[BaseModel]) -> None:
        self._responses: list[BaseModel] = (
            [responses] if isinstance(responses, BaseModel) else list(responses)
        )
        self._index = 0
        self.calls: list[list[ChatMessage]] = []  # histórico de chamadas (para asserts)

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        self.calls.append(list(messages))
        if self._index >= len(self._responses):
            raise LLMProviderError("FakeProvider: sem respostas pré-definidas restantes.")
        response = self._responses[self._index]
        self._index += 1
        # Revalida contra o schema esperado (garante o mesmo contrato do adapter real).
        return response_schema.model_validate(response.model_dump())
