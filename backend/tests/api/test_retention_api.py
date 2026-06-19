"""Testes dos endpoints de retenção/exclusão de análises (LGPD)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from synthetic.builder import build_integra

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

_FAKE_USER = User(id="u-ret", email="ret@sherpi.local", hashed_password="x", role=Role.ADMIN)

_SUMMARY = PetitionSummary(
    juizo="Vara",
    partes=[Parte(nome="A", documento="529.982.247-25", polo=Polo.ATIVO)],
    fato_gerador="Fato.",
    fundamentacao="Lei.",
    pedidos=[Pedido(descricao="Pedido")],
    tem_liminar=False,
    valor_causa="R$ 1.000,00",
    requer_provas=False,
    opcao_audiencia=False,
    documentos_mencionados=[],
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider([_SUMMARY] * 10)))
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


def _post_analysis(client: TestClient) -> str:
    resp = client.post("/v1/analyze", files={"file": ("p.pdf", build_integra(), "application/pdf")})
    assert resp.status_code == 200
    return resp.json()["id"]


def test_delete_requires_auth(client: TestClient) -> None:
    analysis_id = _post_analysis(client)
    app = client.app  # type: ignore[union-attr]
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.delete(f"/v1/analyses/{analysis_id}")
    assert resp.status_code == 401
    # restore
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER


def test_delete_existing_analysis(client: TestClient) -> None:
    analysis_id = _post_analysis(client)
    resp = client.delete(f"/v1/analyses/{analysis_id}")
    assert resp.status_code == 204
    assert client.get(f"/v1/analyses/{analysis_id}").status_code == 404


def test_delete_nonexistent_returns_404(client: TestClient) -> None:
    resp = client.delete("/v1/analyses/id-inexistente")
    assert resp.status_code == 404


def test_bulk_delete_older_than_zero(client: TestClient) -> None:
    _post_analysis(client)
    _post_analysis(client)
    resp = client.delete("/v1/analyses", params={"older_than_days": 0})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2


def test_bulk_delete_future_cutoff_deletes_nothing(client: TestClient) -> None:
    _post_analysis(client)
    # older_than_days=9999 → cutoff muito no passado, nenhuma análise é mais antiga
    resp = client.delete("/v1/analyses", params={"older_than_days": 9999})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 0
