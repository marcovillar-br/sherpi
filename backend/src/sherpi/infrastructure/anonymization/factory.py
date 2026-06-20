"""Seleção do adapter de anonimização a partir da configuração."""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.anonymization.regex import (
    MappedCompositeAnonymizer,
    MappedRegexAnonymizer,
    MappedRegexNameAnonymizer,
    NoOpAnonymizer,
)
from sherpi.shared_kernel.ports import ReversibleAnonymizer


def build_anonymizer(settings: Settings) -> ReversibleAnonymizer:
    """Anonimiza só quando faz sentido: flag ligada **e** LLM externo.

    Usa anonimizadores **reversíveis** (com mapa): o LLM externo recebe o texto
    mascarado, mas os valores reais são restaurados no resumo do revisor humano
    (ver `application/deanonymize.py`). Com `anonymize_names`, encadeia o
    mascaramento de nomes após os identificadores estruturados.
    """
    if not (settings.anonymize_before_llm and settings.is_external_llm):
        return NoOpAnonymizer()
    if settings.anonymize_names:
        return MappedCompositeAnonymizer([MappedRegexAnonymizer(), MappedRegexNameAnonymizer()])
    return MappedRegexAnonymizer()
