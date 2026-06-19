"""Seleção do adapter de anonimização a partir da configuração."""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.anonymization.regex import NoOpAnonymizer, RegexAnonymizer
from sherpi.shared_kernel.ports import Anonymizer


def build_anonymizer(settings: Settings) -> Anonymizer:
    """Anonimiza só quando faz sentido: flag ligada **e** LLM externo.

    Com LLM local/on-prem (ex.: Ollama) os dados não saem do perímetro, então
    o mascaramento é dispensável.
    """
    if settings.anonymize_before_llm and settings.is_external_llm:
        return RegexAnonymizer()
    return NoOpAnonymizer()
