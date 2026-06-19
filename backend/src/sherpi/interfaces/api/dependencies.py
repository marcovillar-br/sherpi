"""Composição (wiring) das dependências da API.

Monta o orquestrador a partir da configuração. É sobreposto nos testes
(`app.dependency_overrides`) para injetar o `FakeProvider` — sem rede.
"""

from __future__ import annotations

from functools import lru_cache

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.application.persistence import AnalysisRepository
from sherpi.config import Settings, get_settings
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.infrastructure.llm.factory import build_llm_provider
from sherpi.infrastructure.persistence.engine import make_engine
from sherpi.infrastructure.persistence.repository import SqlAnalysisRepository


@lru_cache
def _build_orchestrator() -> AnalyzePetition:
    settings: Settings = get_settings()
    llm = build_llm_provider(settings)
    return AnalyzePetition(PyMuPDFParser(), ExtractPetition(llm))


@lru_cache
def _build_repository() -> SqlAnalysisRepository:
    settings: Settings = get_settings()
    return SqlAnalysisRepository(make_engine(settings.database_url))


def get_orchestrator() -> AnalyzePetition:
    """Dependency: o pipeline `AnalyzePetition` (LLM real via config)."""
    return _build_orchestrator()


def get_repository() -> AnalysisRepository:
    """Dependency: repositório de análises (Postgres via config)."""
    return _build_repository()
