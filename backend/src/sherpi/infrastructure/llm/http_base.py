"""Base comum dos adapters de LLM sobre HTTP (httpx).

Concentra o que não depende do provedor: **guarda de custo** (corta entrada
acima do limite), **timeout** e **retry com backoff**. Cada provider concreto
implementa apenas `_request` (montagem do payload + parsing da resposta). É um
adapter: trocá-lo não toca no domínio.
"""

from __future__ import annotations

import asyncio

import httpx

from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel

# Estimativa grosseira de tokens (~4 chars/token) para a guarda de custo.
_CHARS_PER_TOKEN = 4


class HttpLLMProvider:
    """Implementação parcial do port `LLMProvider` sobre httpx."""

    provider_name = "LLM"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        max_input_tokens: int = 200_000,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._max_retries = max_retries
        self._max_input_tokens = max_input_tokens
        self._transport = transport  # injetável para testes (httpx.MockTransport)

    @property
    def model(self) -> str:
        """Nome do modelo (para auditoria/logs)."""
        return self._model

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        self._guard_cost(messages)
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self._timeout, transport=self._transport
                ) as client:
                    return await self._request(
                        client, messages, response_schema, temperature, max_tokens
                    )
            except Exception as exc:  # retry abrange rede, timeout e schema inválido
                last_error = exc
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # backoff exponencial
        raise LLMProviderError(
            f"Falha ao chamar {self.provider_name} após {self._max_retries} tentativas: {last_error}"
        ) from last_error

    def _guard_cost(self, messages: list[ChatMessage]) -> None:
        chars = sum(len(m.content) for m in messages)
        if chars // _CHARS_PER_TOKEN > self._max_input_tokens:
            raise LLMProviderError(
                f"Entrada (~{chars // _CHARS_PER_TOKEN} tokens) excede o limite de "
                f"{self._max_input_tokens}. Reduza/fatie o documento."
            )

    async def _request(
        self,
        client: httpx.AsyncClient,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        temperature: float,
        max_tokens: int | None,
    ) -> TModel:
        raise NotImplementedError
