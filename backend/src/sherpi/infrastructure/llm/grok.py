"""Adapter Grok (xAI) do port `LLMProvider`.

A API do Grok é **OpenAI-compatível** (`/chat/completions`), então usamos httpx
direto (sem o SDK `openai`) e forçamos saída estruturada via `response_format`
do tipo `json_schema`. Resiliência (timeout/retry/guarda de custo) vem da base.
"""

from __future__ import annotations

import httpx

from sherpi.infrastructure.llm.http_base import HttpLLMProvider
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel

_DEFAULT_BASE_URL = "https://api.x.ai/v1"


class GrokProvider(HttpLLMProvider):
    """Implementação do port `LLMProvider` usando a API da xAI (Grok)."""

    provider_name = "Grok"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        max_input_tokens: int = 200_000,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url or _DEFAULT_BASE_URL,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            max_input_tokens=max_input_tokens,
            transport=transport,
        )

    async def _request(
        self,
        client: httpx.AsyncClient,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        temperature: float,
        max_tokens: int | None,
    ) -> TModel:
        payload: dict[str, object] = {
            "model": self._model,
            "temperature": temperature,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.__name__,
                    "schema": response_schema.model_json_schema(),
                },
            },
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        resp = await client.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json=payload,
        )
        resp.raise_for_status()
        choices = resp.json().get("choices") or []
        text = choices[0]["message"]["content"] if choices else ""
        if not text:
            raise LLMProviderError("Resposta vazia do Grok.")
        return response_schema.model_validate_json(text)
