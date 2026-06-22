"""Adapters Grok (xAI) e Anthropic (Sonnet) — httpx mockado, sem rede."""

from __future__ import annotations

import json

import httpx
import pytest

from sherpi.config import Settings
from sherpi.contexts.petition_analysis.domain.summary import Parte, Pedido, PetitionSummary, Polo
from sherpi.infrastructure.llm.anthropic import AnthropicProvider
from sherpi.infrastructure.llm.factory import build_llm_provider
from sherpi.infrastructure.llm.grok import GrokProvider
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import ChatMessage

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
)
_MESSAGES = [
    ChatMessage(role="system", content="Você é um extrator."),
    ChatMessage(role="user", content="Petição..."),
]


def _transport(handler: object) -> httpx.MockTransport:
    return httpx.MockTransport(handler)  # type: ignore[arg-type]


async def test_grok_posts_openai_compatible_and_parses() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        body = json.loads(request.content)
        seen["body"] = body
        content = _SUMMARY.model_dump_json()
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    grok = GrokProvider(model="grok-test", api_key="xai-key", transport=_transport(handler))
    out = await grok.complete(_MESSAGES, PetitionSummary)

    assert out == _SUMMARY
    assert grok.model == "grok-test"
    assert seen["url"] == "https://api.x.ai/v1/chat/completions"
    assert seen["auth"] == "Bearer xai-key"
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["model"] == "grok-test"
    assert body["response_format"]["type"] == "json_schema"
    assert body["messages"][0]["role"] == "system"


async def test_anthropic_uses_tool_use_and_parses() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("x-api-key")
        seen["version"] = request.headers.get("anthropic-version")
        body = json.loads(request.content)
        seen["body"] = body
        return httpx.Response(
            200,
            json={
                "content": [{"type": "tool_use", "name": "extract", "input": _SUMMARY.model_dump()}]
            },
        )

    claude = AnthropicProvider(model="claude-test", api_key="sk-ant", transport=_transport(handler))
    out = await claude.complete(_MESSAGES, PetitionSummary)

    assert out == _SUMMARY
    assert claude.model == "claude-test"
    assert seen["url"] == "https://api.anthropic.com/v1/messages"
    assert seen["key"] == "sk-ant"
    assert seen["version"] == "2023-06-01"
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["system"] == "Você é um extrator."  # system separado das messages
    assert body["tool_choice"] == {"type": "tool", "name": "extract"}
    assert body["messages"][0]["role"] == "user"  # só não-system vão em messages


async def test_grok_raises_on_empty_choice() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": ""}}]})

    grok = GrokProvider(
        model="grok-test", api_key="k", max_retries=1, transport=_transport(handler)
    )
    with pytest.raises(LLMProviderError):
        await grok.complete(_MESSAGES, PetitionSummary)


async def test_anthropic_raises_without_tool_use() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"content": [{"type": "text", "text": "oi"}]})

    claude = AnthropicProvider(
        model="claude-test", api_key="k", max_retries=1, transport=_transport(handler)
    )
    with pytest.raises(LLMProviderError):
        await claude.complete(_MESSAGES, PetitionSummary)


def test_factory_builds_grok_and_anthropic_with_default_model() -> None:
    grok = build_llm_provider(Settings(llm_backend="grok", llm_api_key="k"))
    assert isinstance(grok, GrokProvider)
    assert grok.model == "grok-4-latest"  # default por backend

    claude = build_llm_provider(Settings(llm_backend="anthropic", llm_api_key="k"))
    assert isinstance(claude, AnthropicProvider)
    assert claude.model == "claude-sonnet-4-6"


def test_factory_requires_api_key() -> None:
    with pytest.raises(LLMProviderError):
        build_llm_provider(Settings(llm_backend="grok", llm_api_key=None))


def test_external_llm_backends_require_anonymization() -> None:
    assert Settings(llm_backend="grok").is_external_llm is True
    assert Settings(llm_backend="anthropic").is_external_llm is True
    assert Settings(llm_backend="fake").is_external_llm is False
