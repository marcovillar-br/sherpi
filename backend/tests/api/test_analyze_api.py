"""Testes da API (/analyze, /health, /ready) com TestClient + FakeProvider."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from synthetic.builder import build_clean, build_white_on_white

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.identity.domain.user import Role, User
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
from sherpi.interfaces.api.dependencies import get_current_user, get_orchestrator, get_repository
from sherpi.interfaces.api.main import create_app

_FAKE_USER = User(id="u-test", email="test@sherpi.local", hashed_password="x", role=Role.REVISOR)

_SUMMARY = PetitionSummary(
    juizo="Vara Cível de São Paulo",
    partes=[
        Parte(nome="Fulano", documento="529.982.247-25", polo=Polo.ATIVO),
        Parte(nome="Empresa", documento="11.222.333/0001-81", polo=Polo.PASSIVO),
    ],
    fato_gerador="Contrato inadimplido.",
    fundamentacao="CPC.",
    pedidos=[Pedido(descricao="Pagamento")],
    tem_liminar=False,
    valor_causa="R$ 15.000,00",
    requer_provas=True,
    opcao_audiencia=True,
    documentos_mencionados=["procuração"],
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    # Repositório real (SqlAnalysisRepository) sobre SQLite in-memory — exercita o
    # caminho de persistência sem precisar de Postgres.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    repository = SqlAnalysisRepository(engine)
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_ready(client: TestClient) -> None:
    assert client.get("/ready").status_code == 200


def test_analyze_clean_pdf(client: TestClient) -> None:
    resp = client.post("/v1/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"]
    assert body["result"]["forensics"]["verdict"] == "PASS"
    assert body["result"]["summary"]["partes"][0]["nome"] == "Fulano"
    assert body["result"]["admissibility"]["semaforo"] == "VERDE"


def test_analyze_default_rito_is_civel(client: TestClient) -> None:
    resp = client.post("/v1/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")})
    assert resp.status_code == 200
    assert resp.json()["result"]["rito"] == "CIVEL"


def test_analyze_rito_trabalhista_exige_pedido_liquido(client: TestClient) -> None:
    # O FakeProvider devolve um pedido SEM valor → ilíquido no rito trabalhista.
    resp = client.post(
        "/v1/analyze",
        files={"file": ("p.pdf", build_clean(), "application/pdf")},
        data={"rito": "TRABALHISTA"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["rito"] == "TRABALHISTA"
    assert body["result"]["admissibility"]["semaforo"] == "VERMELHO"


def test_analyze_rito_invalido_retorna_422(client: TestClient) -> None:
    resp = client.post(
        "/v1/analyze",
        files={"file": ("p.pdf", build_clean(), "application/pdf")},
        data={"rito": "CRIMINAL"},
    )
    assert resp.status_code == 422


def test_analyze_injection_blocks(client: TestClient) -> None:
    resp = client.post(
        "/v1/analyze", files={"file": ("p.pdf", build_white_on_white(), "application/pdf")}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["forensics"]["verdict"] == "BLOCK"
    assert body["result"]["summary"] is None


def test_analyze_non_pdf_returns_415(client: TestClient) -> None:
    resp = client.post("/v1/analyze", files={"file": ("x.txt", b"not a pdf", "text/plain")})
    assert resp.status_code == 415


def test_analyze_persists_and_get_roundtrip(client: TestClient) -> None:
    created = client.post(
        "/v1/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")}
    ).json()
    fetched = client.get(f"/v1/analyses/{created['id']}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["id"] == created["id"]
    assert body["result"]["summary"]["partes"][0]["nome"] == "Fulano"


def test_get_unknown_analysis_returns_404(client: TestClient) -> None:
    assert client.get("/v1/analyses/inexistente").status_code == 404


def test_ready_ok_with_reachable_db(client: TestClient) -> None:
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
