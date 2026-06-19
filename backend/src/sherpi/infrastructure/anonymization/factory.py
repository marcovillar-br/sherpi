"""Seleção do adapter de anonimização a partir da configuração."""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.anonymization.regex import (
    MappedRegexAnonymizer,
    NoOpAnonymizer,
    RegexAnonymizer,
)
from sherpi.shared_kernel.ports import Anonymizer


def build_anonymizer(settings: Settings) -> Anonymizer:
    """Anonimiza só quando faz sentido: flag ligada **e** LLM externo."""
    if settings.anonymize_before_llm and settings.is_external_llm:
        return RegexAnonymizer()
    return NoOpAnonymizer()


def build_mapped_anonymizer(settings: Settings) -> MappedRegexAnonymizer | NoOpAnonymizer:
    """Versão com mapeamento reversível — usada quando precisamos rastrear substituições."""
    if settings.anonymize_before_llm and settings.is_external_llm:
        return MappedRegexAnonymizer()
    return NoOpAnonymizer()
