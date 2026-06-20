"""Composição (wiring) das dependências da API.

Monta o orquestrador a partir da configuração. É sobreposto nos testes
(`app.dependency_overrides`) para injetar o `FakeProvider` — sem rede.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.application.persistence import AnalysisRepository
from sherpi.config import Settings, get_settings
from sherpi.contexts.document_integrity.infrastructure.dispatching_parser import DispatchingParser
from sherpi.contexts.document_integrity.infrastructure.docx_parser import DocxParser
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.identity.application.authenticate import Authenticate
from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.issuer import JwtIssuer
from sherpi.contexts.identity.domain.ports import UserRepository
from sherpi.contexts.identity.domain.user import User
from sherpi.contexts.identity.infrastructure.repository import SqlUserRepository
from sherpi.contexts.integration.infrastructure.queue import IngestQueue
from sherpi.contexts.integration.infrastructure.sql_job_repository import SqlIngestJobRepository
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.contexts.review.application.record_review import RecordReview
from sherpi.contexts.review.domain.ports import AuditRepository
from sherpi.contexts.review.infrastructure.repository import SqlAuditRepository
from sherpi.contexts.taxonomy.application.suggest_tpu import SuggestTpu
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.anonymization.factory import build_anonymizer
from sherpi.infrastructure.llm.audit import LoggingLLMProvider
from sherpi.infrastructure.llm.audit_store import LLMCallRepository, PersistingLLMProvider
from sherpi.infrastructure.llm.circuit_breaker import CircuitBreakerLLMProvider
from sherpi.infrastructure.llm.factory import build_llm_provider
from sherpi.infrastructure.llm.fake import RepeatingFakeProvider
from sherpi.infrastructure.persistence.engine import make_engine
from sherpi.infrastructure.persistence.repository import SqlAnalysisRepository, SqlLLMCallRepository
from sherpi.shared_kernel.ports import LLMProvider

_bearer = HTTPBearer(auto_error=False)

# Resumo canônico devolvido pelo backend fake (sem rede). Stub schema-válido: o
# e2e valida o veredito do firewall, não o conteúdo da extração.
_FAKE_SUMMARY = PetitionSummary(
    court="Vara Cível (stub fake)",
    parties=[
        Parte(name="Autor Stub", pole=Polo.ACTIVE),
        Parte(name="Réu Stub", pole=Polo.PASSIVE),
    ],
    facts="Resumo sintético gerado pelo provider fake (sem LLM).",
    legal_basis="Fundamentação stub (sem LLM).",
    claims=[Pedido(description="Pedido stub")],
    has_injunction=False,
    claim_amount="R$ 1.000,00",
)


@lru_cache
def _build_tpu_index() -> SqlTpuIndex:
    settings: Settings = get_settings()
    return SqlTpuIndex(make_engine(settings.database_url))


def _build_suggest_tpu() -> SuggestTpu | None:
    try:
        index = _build_tpu_index()
        if index.count() == 0:
            return None
    except Exception:
        return None
    embedder = FakeEmbeddingModel()
    return SuggestTpu(embedder, index, top_k=get_settings().tpu_top_k)


@lru_cache
def _build_orchestrator() -> AnalyzePetition:
    settings: Settings = get_settings()
    inner: LLMProvider
    if settings.llm_backend == "fake":
        # Servidor sem rede (dev-backend-fake/e2e): extração determinística, zero token.
        inner = RepeatingFakeProvider(_FAKE_SUMMARY)
    else:
        # Provedor real → circuit breaker (corta falhas sustentadas).
        inner = CircuitBreakerLLMProvider(
            build_llm_provider(settings),
            failure_threshold=settings.llm_circuit_breaker_threshold,
            reset_timeout=settings.llm_circuit_breaker_reset_seconds,
        )
    # Persiste cada chamada (prompt+resposta) e loga metadados.
    persisted = PersistingLLMProvider(inner, _build_llm_call_repository(), label="extract")
    llm = LoggingLLMProvider(persisted, label="extract")
    return AnalyzePetition(
        DispatchingParser(
            PyMuPDFParser(timeout_seconds=settings.pdf_parse_timeout_seconds),
            DocxParser(),
        ),
        ExtractPetition(llm, temperature=settings.llm_temperature),
        anonymizer=build_anonymizer(settings),
        suggest_tpu=_build_suggest_tpu(),
    )


@lru_cache
def _build_repository() -> SqlAnalysisRepository:
    settings: Settings = get_settings()
    return SqlAnalysisRepository(make_engine(settings.database_url))


@lru_cache
def _build_llm_call_repository() -> SqlLLMCallRepository:
    settings: Settings = get_settings()
    return SqlLLMCallRepository(make_engine(settings.database_url))


def get_llm_call_repository() -> LLMCallRepository:
    """Dependency: repositório de auditoria das chamadas ao LLM (prompt+resposta)."""
    return _build_llm_call_repository()


@lru_cache
def _build_user_repository() -> SqlUserRepository:
    settings: Settings = get_settings()
    return SqlUserRepository(make_engine(settings.database_url))


@lru_cache
def _build_audit_repository() -> SqlAuditRepository:
    settings: Settings = get_settings()
    return SqlAuditRepository(make_engine(settings.database_url))


@lru_cache
def _build_authenticate() -> Authenticate:
    settings: Settings = get_settings()
    repo = _build_user_repository()
    hasher = BcryptHasher()
    issuer = JwtIssuer(settings.jwt_secret, settings.jwt_algorithm, settings.jwt_expire_minutes)
    return Authenticate(
        repo,
        hasher,
        issuer,
        max_attempts=settings.login_max_attempts,
        lockout_minutes=settings.login_lockout_minutes,
    )


@lru_cache
def _build_issuer() -> JwtIssuer:
    settings: Settings = get_settings()
    return JwtIssuer(settings.jwt_secret, settings.jwt_algorithm, settings.jwt_expire_minutes)


def get_orchestrator() -> AnalyzePetition:
    """Dependency: o pipeline `AnalyzePetition` (LLM real via config)."""
    return _build_orchestrator()


def get_repository() -> AnalysisRepository:
    """Dependency: repositório de análises (Postgres via config)."""
    return _build_repository()


def get_user_repository() -> UserRepository:
    """Dependency: repositório de usuários."""
    return _build_user_repository()


def get_audit_repository() -> AuditRepository:
    """Dependency: repositório de auditoria (append-only)."""
    return _build_audit_repository()


def get_authenticate() -> Authenticate:
    """Dependency: use case de autenticação."""
    return _build_authenticate()


def get_record_review(
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repository)],
) -> RecordReview:
    """Dependency: use case de registro de revisão."""
    return RecordReview(audit_repo)


@lru_cache
def _build_job_repository() -> SqlIngestJobRepository:
    settings: Settings = get_settings()
    return SqlIngestJobRepository(make_engine(settings.database_url))


@lru_cache
def _build_ingest_queue() -> IngestQueue:
    return IngestQueue()


def get_job_repository() -> SqlIngestJobRepository:
    """Dependency: repositório de jobs de ingestão."""
    return _build_job_repository()


def get_ingest_queue() -> IngestQueue:
    """Dependency: fila assíncrona de ingestão (singleton)."""
    return _build_ingest_queue()


def get_current_user(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """Extrai e valida o JWT do Bearer header ou cookie; retorna o usuário autenticado."""
    token: str | None = None
    if credentials is not None:
        token = credentials.credentials
    elif access_token is not None:
        token = access_token

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado.")

    try:
        payload = _build_issuer().verify(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido."
        ) from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    user = user_repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado."
        )
    return user
