"""Seleção do adapter de LLM a partir da configuração.

É o único ponto que decide qual provider concreto usar. Trocar de LLM = mudar
`SHERPI_LLM_BACKEND` no `.env`, sem tocar no domínio nem nos use cases.
"""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.llm.anthropic import AnthropicProvider
from sherpi.infrastructure.llm.gemini import GeminiProvider
from sherpi.infrastructure.llm.grok import GrokProvider
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import LLMProvider

# Modelo default por backend — usado quando `SHERPI_LLM_MODEL` ainda está no default
# de fábrica (o de Gemini), evitando rodar um backend com o nome de modelo errado.
_GEMINI_DEFAULT = "gemini-2.5-flash"
_DEFAULT_MODEL = {"grok": "grok-4-latest", "anthropic": "claude-sonnet-4-6"}


def _resolve_model(settings: Settings) -> str:
    if settings.llm_model == _GEMINI_DEFAULT and settings.llm_backend in _DEFAULT_MODEL:
        return _DEFAULT_MODEL[settings.llm_backend]
    return settings.llm_model


def build_llm_provider(settings: Settings) -> LLMProvider:
    """Constrói o `LLMProvider` configurado.

    O backend `fake` não é construído aqui — o `FakeProvider` é injetado
    diretamente nos testes (precisa de respostas pré-definidas).
    """
    backend = settings.llm_backend
    if backend == "fake":
        raise LLMProviderError(
            "Backend 'fake' não é construído pela factory (injeção direta nos testes)."
        )
    if not settings.llm_api_key:
        raise LLMProviderError(f"SHERPI_LLM_API_KEY é obrigatório para o backend '{backend}'.")

    if backend == "gemini":
        return GeminiProvider(
            model=_resolve_model(settings),
            api_key=settings.llm_api_key,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            max_input_tokens=settings.llm_max_input_tokens,
        )
    if backend in ("grok", "anthropic"):
        cls = GrokProvider if backend == "grok" else AnthropicProvider
        return cls(
            model=_resolve_model(settings),
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            max_input_tokens=settings.llm_max_input_tokens,
        )
    raise LLMProviderError(f"Backend de LLM '{backend}' desconhecido.")
