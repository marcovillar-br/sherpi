"""Adapter Google Gemini do port `LLMProvider` (default).

Força saída estruturada (JSON validado contra o `response_schema`), aplica
`temperature` baixa, **guarda de custo** (corta entrada acima do limite),
**timeout** e **retry com backoff** — resiliência exigida no plano. É um adapter:
trocá-lo por outro provider não toca no domínio.
"""

from __future__ import annotations

import asyncio

from google import genai
from google.genai import types

from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel

# Estimativa grosseira de tokens (~4 chars/token) para a guarda de custo.
_CHARS_PER_TOKEN = 4


class GeminiProvider:
    """Implementação do port `LLMProvider` usando a API Gemini."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        max_input_tokens: int = 200_000,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._max_retries = max_retries
        self._max_input_tokens = max_input_tokens
        self._client: genai.Client | None = None

    @property
    def model(self) -> str:
        """Nome do modelo (para auditoria/logs)."""
        return self._model

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        return self._client

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
                return await asyncio.wait_for(
                    asyncio.to_thread(
                        self._generate, messages, response_schema, temperature, max_tokens
                    ),
                    timeout=self._timeout,
                )
            except Exception as exc:  # retry abrange rede, timeout e schema inválido
                last_error = exc
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # backoff exponencial
        raise LLMProviderError(
            f"Falha ao chamar Gemini após {self._max_retries} tentativas: {last_error}"
        ) from last_error

    def _guard_cost(self, messages: list[ChatMessage]) -> None:
        chars = sum(len(m.content) for m in messages)
        if chars // _CHARS_PER_TOKEN > self._max_input_tokens:
            raise LLMProviderError(
                f"Entrada (~{chars // _CHARS_PER_TOKEN} tokens) excede o limite de "
                f"{self._max_input_tokens}. Reduza/fatie o documento."
            )

    def _generate(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        temperature: float,
        max_tokens: int | None,
    ) -> TModel:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        user = "\n\n".join(m.content for m in messages if m.role != "system")
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system or None,
            max_output_tokens=max_tokens,
        )
        response = self._get_client().models.generate_content(
            model=self._model, contents=user, config=config
        )
        text = response.text
        if not text:
            raise LLMProviderError("Resposta vazia do Gemini.")
        return response_schema.model_validate_json(text)
