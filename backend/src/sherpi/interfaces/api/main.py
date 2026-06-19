"""FastAPI — driving adapter do SHERPI.

Expõe o pipeline de análise via HTTP. Erros de domínio são traduzidos em
respostas consistentes **sem vazar stack trace**.

CSRF: as rotas autenticadas aceitam Bearer (stateless, imune a CSRF) ou cookie
httpOnly+SameSite=lax. O atributo SameSite=lax bloqueia envio de cookie em
requisições cross-site iniciadas pelo navegador, mitigando CSRF em browsers modernos
sem necessidade de token CSRF adicional (aceito para o MVP académico).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sherpi.application.analyze_petition import AnalysisResult, AnalyzePetition
from sherpi.application.persistence import AnalysisRecord, AnalysisRepository
from sherpi.config import Settings, get_settings
from sherpi.contexts.identity.application.authenticate import Authenticate
from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.identity.infrastructure.repository import SqlUserRepository
from sherpi.contexts.review.application.record_review import RecordReview
from sherpi.contexts.review.domain.events import AuditEvent, ReviewDecision
from sherpi.contexts.review.domain.ports import AuditRepository
from sherpi.infrastructure.logging import configure_logging, get_logger
from sherpi.interfaces.api.dependencies import (
    get_audit_repository,
    get_authenticate,
    get_current_user,
    get_orchestrator,
    get_record_review,
    get_repository,
)
from sherpi.interfaces.api.middleware import CorrelationIdMiddleware
from sherpi.shared_kernel.errors import (
    AuthenticationError,
    LLMProviderError,
    UntrustedDocumentError,
)
from sherpi.shared_kernel.value_objects import Rito


class AnalyzeResponse(BaseModel):
    id: str
    result: AnalysisResult


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReviewRequest(BaseModel):
    decision: ReviewDecision
    comment: str | None = None


def _seed_user(settings: Settings) -> None:
    if not settings.seed_user_password:
        return
    from sherpi.infrastructure.persistence.engine import make_engine

    engine = make_engine(settings.database_url)
    repo = SqlUserRepository(engine)
    if not repo.exists(settings.seed_user_email):
        hasher = BcryptHasher()
        repo.save(
            User(
                id=uuid.uuid4().hex,
                email=settings.seed_user_email,
                hashed_password=hasher.hash(settings.seed_user_password),
                role=Role.ADMIN,
            )
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    configure_logging(log_level=cfg.log_level, json_logs=cfg.env == "prod")
    logger = get_logger("sherpi.api")

    if cfg.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(dsn=cfg.sentry_dsn, traces_sample_rate=0.1)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        _seed_user(cfg)
        yield

    app = FastAPI(title="SHERPI API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready(
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        response: Response,
    ) -> dict[str, str]:
        if repository.ping():
            return {"status": "ok"}
        response.status_code = 503
        return {"status": "unavailable"}

    v1 = APIRouter(prefix="/v1")

    @v1.post("/auth/login", response_model=TokenResponse)
    def login(
        authenticate: Annotated[Authenticate, Depends(get_authenticate)],
        response: Response,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ) -> TokenResponse:
        try:
            token = authenticate.run(username, password)
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        response.set_cookie("access_token", token, httponly=True, samesite="lax")
        return TokenResponse(access_token=token)

    @v1.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(
        orchestrator: Annotated[AnalyzePetition, Depends(get_orchestrator)],
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
        file: Annotated[UploadFile, File(description="PDF da petição inicial")],
        rito: Annotated[Rito, Form(description="Rito processual (default cível)")] = Rito.CIVEL,
    ) -> AnalyzeResponse:
        logger.info("analyze.start", filename=file.filename, rito=rito, user=current_user.email)
        content = await file.read()
        max_bytes = cfg.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail=f"Arquivo excede {cfg.max_upload_mb} MB.")
        try:
            result = await orchestrator.run(content, max_pages=cfg.max_pdf_pages, rito=rito)
        except UntrustedDocumentError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc
        except LLMProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        record = AnalysisRecord(
            id=uuid.uuid4().hex,
            created_at=datetime.now(UTC),
            filename=file.filename,
            result=result,
        )
        repository.save(record)
        logger.info("analyze.done", analysis_id=record.id, verdict=result.forensics.verdict)
        return AnalyzeResponse(id=record.id, result=result)

    @v1.get("/analyses/{analysis_id}", response_model=AnalyzeResponse)
    def get_analysis(
        analysis_id: str,
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> AnalyzeResponse:
        record = repository.get(analysis_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")
        return AnalyzeResponse(id=record.id, result=record.result)

    @v1.post("/analyses/{analysis_id}/review", response_model=AuditEvent)
    def create_review(
        analysis_id: str,
        body: ReviewRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        record_review: Annotated[RecordReview, Depends(get_record_review)],
    ) -> AuditEvent:
        if repository.get(analysis_id) is None:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")
        return record_review.run(analysis_id, current_user, body.decision, body.comment)

    @v1.get("/analyses/{analysis_id}/reviews", response_model=list[AuditEvent])
    def list_reviews(
        analysis_id: str,
        current_user: Annotated[User, Depends(get_current_user)],
        audit_repo: Annotated[AuditRepository, Depends(get_audit_repository)],
    ) -> list[AuditEvent]:
        return audit_repo.list_by_analysis(analysis_id)

    @v1.delete("/analyses/{analysis_id}", status_code=204)
    def delete_analysis(
        analysis_id: str,
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> None:
        if not repository.delete(analysis_id):
            raise HTTPException(status_code=404, detail="Análise não encontrada.")
        logger.info("analysis.deleted", analysis_id=analysis_id, user=current_user.email)

    @v1.delete("/analyses", response_model=dict[str, int])
    def delete_old_analyses(
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
        older_than_days: Annotated[int, Query(ge=0)] = cfg.retention_days,
    ) -> dict[str, int]:
        cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
        ids = repository.list_older_than(cutoff)
        for analysis_id in ids:
            repository.delete(analysis_id)
        logger.info("analyses.bulk_delete", count=len(ids), older_than_days=older_than_days)
        return {"deleted": len(ids)}

    app.include_router(v1)
    return app


app = create_app()
