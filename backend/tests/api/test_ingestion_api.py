from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.integration.infrastructure.queue import IngestQueue
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
from sherpi.interfaces.api.dependencies import (
    get_current_user,
    get_ingest_queue,
    get_job_repository,
    get_orchestrator,
    get_repository,
)
from sherpi.interfaces.api.main import create_app

_FAKE_USER = User(id="u-test", email="test@sherpi.local", hashed_password="x", role=Role.REVISOR)

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
def client() -> Iterator[TestClient]:
    app = create_app()
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    repository = SqlAnalysisRepository(engine)
    job_repo = SqlIngestJobRepository(engine)
    # Fila mock que não inicia worker de verdade em testes síncronos
    ingest_queue = IngestQueue()
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_job_repository] = lambda: job_repo
    app.dependency_overrides[get_ingest_queue] = lambda: ingest_queue
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def unauth_client() -> Iterator[TestClient]:
    app = create_app()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    repository = SqlAnalysisRepository(engine)
    job_repo = SqlIngestJobRepository(engine)
    ingest_queue = IngestQueue()
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_job_repository] = lambda: job_repo
    app.dependency_overrides[get_ingest_queue] = lambda: ingest_queue
    # no get_current_user override → uses real auth → 401
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_job_returns_202(client: TestClient) -> None:
    resp = client.post(
        "/v1/ingestion/jobs",
        json={
            "source": "SANDBOX",
            "tribunal": "TJSP",
            "date_from": "2024-01-01",
            "date_to": "2024-01-07",
        },
    )
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "QUEUED"
    assert body["tribunal"] == "TJSP"
    assert body["id"]


def test_list_jobs(client: TestClient) -> None:
    client.post(
        "/v1/ingestion/jobs",
        json={
            "source": "SANDBOX",
            "tribunal": "TJSP",
            "date_from": "2024-01-01",
            "date_to": "2024-01-07",
        },
    )
    resp = client.get("/v1/ingestion/jobs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_job_status(client: TestClient) -> None:
    created = client.post(
        "/v1/ingestion/jobs",
        json={
            "source": "SANDBOX",
            "tribunal": "TRT2",
            "date_from": "2024-01-01",
            "date_to": "2024-01-07",
        },
    ).json()
    resp = client.get(f"/v1/ingestion/jobs/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_unknown_job_returns_404(client: TestClient) -> None:
    assert client.get("/v1/ingestion/jobs/nonexistent").status_code == 404


def test_create_job_unauthorized(unauth_client: TestClient) -> None:
    resp = unauth_client.post(
        "/v1/ingestion/jobs",
        json={
            "source": "SANDBOX",
            "tribunal": "TJSP",
            "date_from": "2024-01-01",
            "date_to": "2024-01-07",
        },
    )
    assert resp.status_code == 401


def test_list_jobs_unauthorized(unauth_client: TestClient) -> None:
    assert unauth_client.get("/v1/ingestion/jobs").status_code == 401
