"""Testes da API (/analyze, /health, /ready) com TestClient + FakeProvider."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from synthetic.builder import build_clean, build_white_on_white

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.infrastructure.llm.fake import FakeProvider
from sherpi.interfaces.api.dependencies import get_orchestrator
from sherpi.interfaces.api.main import create_app

_SUMMARY = PetitionSummary(
    partes=[
        Parte(nome="Fulano", documento="529.982.247-25", polo=Polo.ATIVO),
        Parte(nome="Empresa", documento="11.222.333/0001-81", polo=Polo.PASSIVO),
    ],
    fato_gerador="Contrato inadimplido.",
    fundamentacao="CPC.",
    pedidos=[Pedido(descricao="Pagamento")],
    tem_liminar=False,
    valor_causa="R$ 15.000,00",
    documentos_mencionados=["procuração"],
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_ready(client: TestClient) -> None:
    assert client.get("/ready").status_code == 200


def test_analyze_clean_pdf(client: TestClient) -> None:
    resp = client.post("/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"]
    assert body["result"]["forensics"]["verdict"] == "PASS"
    assert body["result"]["summary"]["partes"][0]["nome"] == "Fulano"
    assert body["result"]["admissibility"]["semaforo"] == "VERDE"


def test_analyze_injection_blocks(client: TestClient) -> None:
    resp = client.post(
        "/analyze", files={"file": ("p.pdf", build_white_on_white(), "application/pdf")}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["forensics"]["verdict"] == "BLOCK"
    assert body["result"]["summary"] is None


def test_analyze_non_pdf_returns_415(client: TestClient) -> None:
    resp = client.post("/analyze", files={"file": ("x.txt", b"not a pdf", "text/plain")})
    assert resp.status_code == 415
