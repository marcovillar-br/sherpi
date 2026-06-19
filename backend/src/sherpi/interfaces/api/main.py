"""FastAPI — driving adapter do SHERPI.

Expõe o pipeline de análise via HTTP. Erros de domínio são traduzidos em
respostas consistentes **sem vazar stack trace**.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sherpi.application.analyze_petition import AnalysisResult, AnalyzePetition
from sherpi.application.persistence import AnalysisRecord, AnalysisRepository
from sherpi.config import Settings, get_settings
from sherpi.interfaces.api.dependencies import get_orchestrator, get_repository
from sherpi.shared_kernel.errors import LLMProviderError, UntrustedDocumentError


class AnalyzeResponse(BaseModel):
    id: str
    result: AnalysisResult


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(title="SHERPI API", version="0.1.0")
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

    @app.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(
        orchestrator: Annotated[AnalyzePetition, Depends(get_orchestrator)],
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
        file: Annotated[UploadFile, File(description="PDF da petição inicial")],
    ) -> AnalyzeResponse:
        content = await file.read()
        max_bytes = cfg.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail=f"Arquivo excede {cfg.max_upload_mb} MB.")
        try:
            result = await orchestrator.run(content, max_pages=cfg.max_pdf_pages)
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
        return AnalyzeResponse(id=record.id, result=result)

    @app.get("/analyses/{analysis_id}", response_model=AnalyzeResponse)
    def get_analysis(
        analysis_id: str,
        repository: Annotated[AnalysisRepository, Depends(get_repository)],
    ) -> AnalyzeResponse:
        record = repository.get(analysis_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")
        return AnalyzeResponse(id=record.id, result=record.result)

    return app


app = create_app()
