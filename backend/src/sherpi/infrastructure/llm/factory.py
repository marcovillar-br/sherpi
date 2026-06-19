"""Seleção do adapter de LLM a partir da configuração.

É o único ponto que decide qual provider concreto usar. Trocar de LLM = mudar
`SHERPI_LLM_BACKEND` no `.env`, sem tocar no domínio nem nos use cases.
"""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.llm.gemini import GeminiProvider
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import LLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    """Constrói o `LLMProvider` configurado.

    O backend `fake` não é construído aqui — o `FakeProvider` é injetado
    diretamente nos testes (precisa de respostas pré-definidas).
    """
    backend = settings.llm_backend
    if backend == "gemini":
        if not settings.llm_api_key:
            raise LLMProviderError("SHERPI_LLM_API_KEY é obrigatório para o backend 'gemini'.")
        return GeminiProvider(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            max_input_tokens=settings.llm_max_input_tokens,
        )
    if backend == "openai_compat":
        # Adapter Maritaca Sabiá / OpenAI / Ollama (API OpenAI-compatível) — Fase 4.
        raise LLMProviderError(
            "Backend 'openai_compat' ainda não implementado (planejado para a Fase 4)."
        )
    raise LLMProviderError(
        f"Backend de LLM '{backend}' não pode ser construído pela factory "
        "(use injeção direta do FakeProvider em testes)."
    )
