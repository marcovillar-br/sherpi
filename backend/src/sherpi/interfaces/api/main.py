"""FastAPI — driving adapter do SHERPI.

Expõe o pipeline de análise via HTTP. Erros de domínio são traduzidos em
respostas consistentes **sem vazar stack trace**.

CSRF: as rotas autenticadas aceitam Bearer (stateless, imune a CSRF) ou cookie
httpOnly+SameSite=lax. O atributo SameSite=lax bloqueia envio de cookie em
requisições cross-site iniciadas pelo navegador, mitigando CSRF em browsers modernos
sem necessidade de token CSRF adicional (aceito para o MVP académico).
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

import structlog
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
from sherpi.application.persistence import AnalysisRecord, AnalysisRepository, AnalysisSummary
from sherpi.config import Settings, get_settings
from sherpi.contexts.identity.application.authenticate import Authenticate
from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.identity.infrastructure.repository import SqlUserRepository
from sherpi.contexts.integration.application.ingest_petitions import IngestPetitions
from sherpi.contexts.integration.domain.ingestion import IngestJob, IngestStatus
from sherpi.contexts.integration.infrastructure.queue import IngestQueue
from sherpi.contexts.integration.infrastructure.sandbox_adapter import SandboxSourceAdapter
from sherpi.contexts.integration.infrastructure.sql_job_repository import SqlIngestJobRepository
from sherpi.contexts.review.application.record_review import RecordReview
from sherpi.contexts.review.domain.events import AuditEvent, ReviewDecision
from sherpi.contexts.review.domain.ports import AuditRepository
from sherpi.infrastructure.llm.audit_store import LLMCall, LLMCallRepository
from sherpi.infrastructure.logging import configure_logging, get_logger
from sherpi.interfaces.api.dependencies import (
    get_audit_repository,
    get_authenticate,
    get_current_user,
    get_ingest_queue,
    get_job_repository,
    get_llm_call_repository,
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


class AnalysisListItem(AnalysisSummary):
    """Item do histórico: o resumo + a revisão humana mais recente (se houver)."""

    review_decision: str | None = None
    review_comment: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReviewRequest(BaseModel):
    decision: ReviewDecision
    comment: str | None = None


class IngestJobRequest(BaseModel):
    source: str = "SANDBOX"
    tribunal: str
    date_from: date
    date_to: date


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
        ingest_queue = get_ingest_queue()
        worker_task = asyncio.create_task(ingest_queue.worker())
        yield
        worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await worker_task

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
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=cfg.cookie_secure,
            samesite="lax",
        )
        return TokenResponse(access_token=token)

    @v1.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(
        orchestrator: Annotated[AnalyzePetition, Depends(get_orchestrator)],
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
        file: Annotated[UploadFile, File(description="PDF da petição inicial")],
        rito: Annotated[Rito, Form(description="Rito processual (default cível)")] = Rito.CIVEL,
    ) -> AnalyzeResponse:
        analysis_id = uuid.uuid4().hex
        structlog.contextvars.bind_contextvars(analysis_id=analysis_id)
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
            id=analysis_id,
            created_at=datetime.now(UTC),
            filename=file.filename,
            result=result,
        )
        repository.save(record)
        logger.info("analyze.done", analysis_id=record.id, verdict=result.forensics.verdict)
        return AnalyzeResponse(id=record.id, result=result)

    @v1.get("/analyses", response_model=list[AnalysisListItem])
    def list_analyses(
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        audit_repo: Annotated[AuditRepository, Depends(get_audit_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> list[AnalysisListItem]:
        """Histórico: resumos das análises mais recentes + revisão mais recente de cada."""
        summaries = repository.list_recent()
        reviews = audit_repo.latest_by_analyses([s.id for s in summaries])
        items: list[AnalysisListItem] = []
        for s in summaries:
            rev = reviews.get(s.id)
            items.append(
                AnalysisListItem(
                    **s.model_dump(),
                    review_decision=rev.decision.value if rev else None,
                    review_comment=rev.comment if rev else None,
                )
            )
        return items

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

    @v1.get("/analyses/{analysis_id}/llm-calls", response_model=list[LLMCall])
    def list_llm_calls(
        analysis_id: str,
        llm_repo: Annotated[LLMCallRepository, Depends(get_llm_call_repository)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> list[LLMCall]:
        """Auditoria: prompt + resposta de cada chamada ao LLM desta análise."""
        return llm_repo.list_by_analysis(analysis_id)

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

    ingestion = APIRouter(prefix="/v1/ingestion")

    @ingestion.post("/jobs", response_model=IngestJob, status_code=202)
    async def create_ingest_job(
        body: IngestJobRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        orchestrator: Annotated[AnalyzePetition, Depends(get_orchestrator)],
        analysis_repo: Annotated[AnalysisRepository, Depends(get_repository)],
        job_repo: Annotated[SqlIngestJobRepository, Depends(get_job_repository)],
        ingest_queue: Annotated[IngestQueue, Depends(get_ingest_queue)],
    ) -> IngestJob:
        job = IngestJob(
            id=uuid.uuid4().hex,
            source=body.source,
            tribunal=body.tribunal,
            date_from=body.date_from,
            date_to=body.date_to,
            status=IngestStatus.QUEUED,
            created_at=datetime.now(UTC),
        )
        job_repo.save(job)
        source = SandboxSourceAdapter()
        use_case = IngestPetitions(
            source, orchestrator, analysis_repo, job_repo, max_pages=cfg.ingest_max_pages
        )
        await ingest_queue.enqueue(lambda: use_case.run(job))
        logger.info("ingest.queued", job_id=job.id, tribunal=job.tribunal, user=current_user.email)
        return job

    @ingestion.get("/jobs", response_model=list[IngestJob])
    def list_ingest_jobs(
        current_user: Annotated[User, Depends(get_current_user)],
        job_repo: Annotated[SqlIngestJobRepository, Depends(get_job_repository)],
    ) -> list[IngestJob]:
        return job_repo.list_all()

    @ingestion.get("/jobs/{job_id}", response_model=IngestJob)
    def get_ingest_job(
        job_id: str,
        current_user: Annotated[User, Depends(get_current_user)],
        job_repo: Annotated[SqlIngestJobRepository, Depends(get_job_repository)],
    ) -> IngestJob:
        job = job_repo.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        return job

    app.include_router(v1)
    app.include_router(ingestion)
    return app


app = create_app()
