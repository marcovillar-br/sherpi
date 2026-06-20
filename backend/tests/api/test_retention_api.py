"""Testes dos endpoints de retenção/exclusão de análises (LGPD)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from synthetic.builder import build_clean

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
from sherpi.contexts.review.infrastructure.repository import SqlAuditRepository
from sherpi.infrastructure.llm.audit_store import LLMCall
from sherpi.infrastructure.llm.fake import FakeProvider
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.infrastructure.persistence.repository import SqlAnalysisRepository, SqlLLMCallRepository
from sherpi.interfaces.api.dependencies import (
    get_audit_repository,
    get_current_user,
    get_llm_call_repository,
    get_orchestrator,
    get_repository,
)
from sherpi.interfaces.api.main import create_app

_FAKE_USER = User(id="u-ret", email="ret@sherpi.local", hashed_password="x", role=Role.ADMIN)

_SUMMARY = PetitionSummary(
    court="Vara",
    parties=[Parte(name="A", document="529.982.247-25", pole=Polo.ACTIVE)],
    facts="Fato.",
    legal_basis="Lei.",
    claims=[Pedido(description="Pedido")],
    has_injunction=False,
    claim_amount="R$ 1.000,00",
    requests_evidence=False,
    hearing_option=False,
    cited_documents=[],
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
    audit_repo = SqlAuditRepository(engine)
    llm_repo = SqlLLMCallRepository(engine)
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_audit_repository] = lambda: audit_repo
    app.dependency_overrides[get_llm_call_repository] = lambda: llm_repo
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER
    yield TestClient(app)
    app.dependency_overrides.clear()


def _post_analysis(client: TestClient) -> str:
    resp = client.post("/v1/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")})
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


# --- Histórico: GET /v1/analyses (lista resumida) ---


def test_list_analyses_empty(client: TestClient) -> None:
    resp = client.get("/v1/analyses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_analyses_returns_summaries(client: TestClient) -> None:
    id1 = _post_analysis(client)
    id2 = _post_analysis(client)
    resp = client.get("/v1/analyses")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert {it["id"] for it in items} == {id1, id2}
    item = items[0]
    assert item["verdict"] in ("PASS", "WARN", "BLOCK")
    assert item["rito"] in ("CIVEL", "TRABALHISTA")
    # PDF limpo → análise cognitiva executada → status presente.
    assert item["admissibility_status"] in ("GREEN", "YELLOW", "RED")
    assert item["has_injunction"] is False
    assert "filename" in item and "created_at" in item


def test_list_analyses_requires_auth(client: TestClient) -> None:
    _post_analysis(client)
    app = client.app  # type: ignore[union-attr]
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get("/v1/analyses")
    assert resp.status_code == 401
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER


def test_list_includes_latest_review(client: TestClient) -> None:
    aid = _post_analysis(client)
    r = client.post(
        f"/v1/analyses/{aid}/review",
        json={"decision": "AMEND", "comment": "Falta procuração."},
    )
    assert r.status_code == 200
    item = next(it for it in client.get("/v1/analyses").json() if it["id"] == aid)
    assert item["review_decision"] == "AMEND"
    assert item["review_comment"] == "Falta procuração."


def test_list_without_review_has_null_fields(client: TestClient) -> None:
    _post_analysis(client)
    item = client.get("/v1/analyses").json()[0]
    assert item["review_decision"] is None
    assert item["review_comment"] is None


# --- Auditoria do LLM: GET /v1/analyses/{id}/llm-calls ---


def _seed_llm_call(client: TestClient, analysis_id: str) -> None:
    app = client.app  # type: ignore[union-attr]
    repo = app.dependency_overrides[get_llm_call_repository]()
    repo.append(
        LLMCall(
            id="call-1",
            analysis_id=analysis_id,
            call_type="extract",
            model="gemini-test",
            prompt='[{"role": "user", "content": "petição..."}]',
            response='{"facts": "..."}',
            prompt_chars=30,
            response_chars=16,
            duration_ms=42,
            created_at=datetime.now(UTC),
        )
    )


def test_list_llm_calls_returns_persisted(client: TestClient) -> None:
    aid = _post_analysis(client)
    _seed_llm_call(client, aid)
    items = client.get(f"/v1/analyses/{aid}/llm-calls").json()
    assert len(items) == 1
    assert items[0]["analysis_id"] == aid
    assert items[0]["call_type"] == "extract"
    assert "petição" in items[0]["prompt"]
    assert items[0]["response"] == '{"facts": "..."}'


def test_list_llm_calls_empty_when_none(client: TestClient) -> None:
    aid = _post_analysis(client)
    assert client.get(f"/v1/analyses/{aid}/llm-calls").json() == []


def test_list_llm_calls_requires_auth(client: TestClient) -> None:
    aid = _post_analysis(client)
    app = client.app  # type: ignore[union-attr]
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.get(f"/v1/analyses/{aid}/llm-calls")
    assert resp.status_code == 401
    app.dependency_overrides[get_current_user] = lambda: _FAKE_USER
