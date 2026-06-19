from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import StaticPool, create_engine

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.integration.application.ingest_petitions import IngestPetitions
from sherpi.contexts.integration.domain.ingestion import IngestJob, IngestStatus
from sherpi.contexts.integration.infrastructure.sandbox_adapter import SandboxSourceAdapter
from sherpi.contexts.integration.infrastructure.sql_job_repository import SqlIngestJobRepository
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.infrastructure.llm.fake import FakeProvider
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.infrastructure.persistence.repository import SqlAnalysisRepository

_SUMMARY = PetitionSummary(
    juizo="Vara Cível de SP",
    partes=[Parte(nome="Fulano", documento="529.982.247-25", polo=Polo.ATIVO)],
    fato_gerador="Contrato.",
    fundamentacao="CPC.",
    pedidos=[Pedido(descricao="Pagamento", valor="R$ 1.000,00")],
    tem_liminar=False,
    valor_causa="R$ 1.000,00",
    requer_provas=False,
    opcao_audiencia=False,
    documentos_mencionados=[],
)


@pytest.fixture
def engine():  # type: ignore[no-untyped-def]
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(eng)
    return eng


async def test_ingest_job_done(engine) -> None:  # type: ignore[no-untyped-def]
    analysis_repo = SqlAnalysisRepository(engine)
    job_repo = SqlIngestJobRepository(engine)
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    source = SandboxSourceAdapter()

    job = IngestJob(
        id="job-001",
        source="SANDBOX",
        tribunal="TJSP",
        date_from=date(2024, 1, 1),
        date_to=date(2024, 1, 7),
        created_at=datetime.now(UTC),
    )

    use_case = IngestPetitions(source, orchestrator, analysis_repo, job_repo)
    result = await use_case.run(job)

    assert result.status == IngestStatus.DONE
    assert result.total > 0
    assert result.processed + result.failed == result.total
    assert result.processed > 0
    assert result.finished_at is not None


async def test_ingest_job_persisted(engine) -> None:  # type: ignore[no-untyped-def]
    analysis_repo = SqlAnalysisRepository(engine)
    job_repo = SqlIngestJobRepository(engine)
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))

    job = IngestJob(
        id="job-002",
        source="SANDBOX",
        tribunal="TRT2",
        date_from=date(2024, 1, 1),
        date_to=date(2024, 1, 7),
        created_at=datetime.now(UTC),
    )

    use_case = IngestPetitions(
        source=SandboxSourceAdapter(),
        orchestrator=orchestrator,
        analysis_repo=analysis_repo,
        job_repo=job_repo,
    )
    await use_case.run(job)

    persisted = job_repo.get("job-002")
    assert persisted is not None
    assert persisted.status == IngestStatus.DONE


def test_job_repository_list_all(engine) -> None:  # type: ignore[no-untyped-def]
    job_repo = SqlIngestJobRepository(engine)
    job = IngestJob(
        id="job-003",
        source="SANDBOX",
        tribunal="TJRJ",
        date_from=date(2024, 2, 1),
        date_to=date(2024, 2, 7),
        created_at=datetime.now(UTC),
    )
    job_repo.save(job)
    jobs = job_repo.list_all()
    assert any(j.id == "job-003" for j in jobs)


def test_job_repository_get_missing(engine) -> None:  # type: ignore[no-untyped-def]
    job_repo = SqlIngestJobRepository(engine)
    assert job_repo.get("nonexistent") is None
