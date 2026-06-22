"""Adapter Anthropic (Claude Sonnet) do port `LLMProvider`.

A Messages API da Anthropic não tem `response_format` JSON nativo; forçamos saída
estruturada via **tool-use**: declaramos uma tool cujo `input_schema` é o JSON
Schema esperado e obrigamos a chamada (`tool_choice`). O bloco `tool_use` da
resposta carrega o objeto já estruturado. Usa httpx direto (sem o SDK oficial).
"""

from __future__ import annotations

import httpx

from sherpi.infrastructure.llm.http_base import HttpLLMProvider
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage, TModel

_DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
_API_VERSION = "2023-06-01"
_TOOL_NAME = "extract"


class AnthropicProvider(HttpLLMProvider):
    """Implementação do port `LLMProvider` usando a Messages API da Anthropic."""

    provider_name = "Anthropic"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        max_input_tokens: int = 200_000,
        max_output_tokens: int = 4096,
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
        self._max_output_tokens = max_output_tokens

    async def _request(
        self,
        client: httpx.AsyncClient,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        temperature: float,
        max_tokens: int | None,
    ) -> TModel:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        chat = [
            {"role": "assistant" if m.role == "assistant" else "user", "content": m.content}
            for m in messages
            if m.role != "system"
        ]
        payload: dict[str, object] = {
            "model": self._model,
            "max_tokens": max_tokens or self._max_output_tokens,
            "temperature": temperature,
            "messages": chat,
            "tools": [
                {
                    "name": _TOOL_NAME,
                    "description": "Retorna o resultado estruturado da extração.",
                    "input_schema": response_schema.model_json_schema(),
                }
            ],
            "tool_choice": {"type": "tool", "name": _TOOL_NAME},
        }
        if system:
            payload["system"] = system
        resp = await client.post(
            f"{self._base_url}/messages",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": _API_VERSION,
                "content-type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        for block in resp.json().get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == _TOOL_NAME:
                return response_schema.model_validate(block["input"])
        raise LLMProviderError("Anthropic não retornou um bloco tool_use estruturado.")
