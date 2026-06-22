"""Testes das rotas de autenticação e proteção de endpoints."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from synthetic.builder import build_clean

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.identity.application.authenticate import Authenticate
from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.issuer import JwtIssuer
from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.identity.infrastructure.repository import SqlUserRepository
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.contexts.review.infrastructure.repository import SqlAuditRepository
from sherpi.infrastructure.llm.fake import FakeProvider
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.infrastructure.persistence.repository import SqlAnalysisRepository
from sherpi.interfaces.api.dependencies import (
    get_audit_repository,
    get_authenticate,
    get_current_user,
    get_orchestrator,
    get_repository,
    get_user_repository,
)
from sherpi.interfaces.api.main import create_app

_SECRET = "test-secret-auth-longer-key-32bytes"
_EMAIL = "admin@sherpi.local"
_PASSWORD = "senha123"

_SUMMARY = PetitionSummary(
    court="Vara Cível",
    parties=[Parte(name="A", document="529.982.247-25", pole=Polo.ACTIVE)],
    facts="Fato.",
    legal_basis="CPC.",
    claims=[Pedido(description="Pagamento")],
    has_injunction=False,
    claim_amount="R$ 1.000,00",
    requests_evidence=False,
    hearing_option=False,
    cited_documents=[],
)


def _make_engine() -> object:
    return create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )


@pytest.fixture
def auth_setup() -> tuple[
    TestClient,
    SqlUserRepository,
    SqlAuditRepository,
    SqlAnalysisRepository,
    AnalyzePetition,
    Authenticate,
    User,
    JwtIssuer,
]:
    from sqlalchemy import Engine as _Engine

    engine: _Engine = _make_engine()  # type: ignore[assignment]
    create_all(engine)

    hasher = BcryptHasher()
    issuer = JwtIssuer(_SECRET, expire_minutes=60)
    user_repo = SqlUserRepository(engine)
    user = User(id="u-test", email=_EMAIL, hashed_password=hasher.hash(_PASSWORD), role=Role.ADMIN)
    user_repo.save(user)

    audit_repo = SqlAuditRepository(engine)
    analysis_repo = SqlAnalysisRepository(engine)
    orchestrator = AnalyzePetition(PyMuPDFParser(), ExtractPetition(FakeProvider(_SUMMARY)))
    authenticate = Authenticate(user_repo, hasher, issuer, max_attempts=5, lockout_minutes=15)
    return (
        TestClient(create_app()),
        user_repo,
        audit_repo,
        analysis_repo,
        orchestrator,
        authenticate,
        user,
        issuer,
    )


@pytest.fixture
def client(
    auth_setup: tuple[
        TestClient,
        SqlUserRepository,
        SqlAuditRepository,
        SqlAnalysisRepository,
        AnalyzePetition,
        Authenticate,
        User,
        JwtIssuer,
    ],
) -> Iterator[TestClient]:
    tc, user_repo, audit_repo, analysis_repo, orchestrator, authenticate, user, _issuer = auth_setup
    app = tc.app
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_repository] = lambda: analysis_repo
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_audit_repository] = lambda: audit_repo
    app.dependency_overrides[get_authenticate] = lambda: authenticate
    # Em testes: get_current_user retorna sempre o user de teste (auth é testado separadamente).
    app.dependency_overrides[get_current_user] = lambda: user
    yield tc
    app.dependency_overrides.clear()


def _login(client: TestClient, password: str = _PASSWORD) -> str:
    resp = client.post("/v1/auth/login", data={"username": _EMAIL, "password": password})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


def test_login_correct_credentials(client: TestClient) -> None:
    token = _login(client)
    assert token


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    resp = client.post("/v1/auth/login", data={"username": _EMAIL, "password": "errada"})
    assert resp.status_code == 401


def test_login_sets_cookie(client: TestClient) -> None:
    resp = client.post("/v1/auth/login", data={"username": _EMAIL, "password": _PASSWORD})
    assert "access_token" in resp.cookies


def test_analyze_without_token_returns_401() -> None:
    """Endpoint protegido — sem override de get_current_user → 401.

    Sobrescreve apenas as dependências pesadas (orquestrador/repositório): elas não
    têm relação com auth e, sem credenciais de LLM nem DB (como no CI), falhariam ao
    ser construídas, mascarando o 401 com um 500. get_current_user fica real.
    """
    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: None
    app.dependency_overrides[get_repository] = lambda: None
    unauth_client = TestClient(app, raise_server_exceptions=False)
    resp = unauth_client.post(
        "/v1/analyze", files={"file": ("p.pdf", build_clean(), "application/pdf")}
    )
    assert resp.status_code == 401
    app.dependency_overrides.clear()


def test_analyze_with_auth_returns_200(client: TestClient) -> None:
    resp = client.post(
        "/v1/analyze",
        files={"file": ("p.pdf", build_clean(), "application/pdf")},
    )
    assert resp.status_code == 200


def test_review_requires_auth() -> None:
    """Endpoint de revisão protegido — sem auth → 401."""
    app = create_app()
    unauth_client = TestClient(app, raise_server_exceptions=False)
    resp = unauth_client.post("/v1/analyses/x/review", json={"decision": "ACCEPT"})
    assert resp.status_code == 401


def test_review_flow(client: TestClient) -> None:
    created = client.post(
        "/v1/analyze",
        files={"file": ("p.pdf", build_clean(), "application/pdf")},
    ).json()
    analysis_id = created["id"]

    resp = client.post(
        f"/v1/analyses/{analysis_id}/review",
        json={"decision": "ACCEPT", "comment": "Tudo ok"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "ACCEPT"
    assert body["analysis_id"] == analysis_id

    resp2 = client.get(f"/v1/analyses/{analysis_id}/reviews")
    assert resp2.status_code == 200
    events = resp2.json()
    assert len(events) == 1
    assert events[0]["decision"] == "ACCEPT"


def test_review_unknown_analysis_returns_404(client: TestClient) -> None:
    resp = client.post(
        "/v1/analyses/inexistente/review",
        json={"decision": "REJECT"},
    )
    assert resp.status_code == 404


def test_lockout_after_max_attempts(
    auth_setup: tuple[
        TestClient,
        SqlUserRepository,
        SqlAuditRepository,
        SqlAnalysisRepository,
        AnalyzePetition,
        Authenticate,
        User,
        JwtIssuer,
    ],
) -> None:
    """Após N tentativas falhadas, a conta é bloqueada."""
    tc, user_repo, _audit_repo, _analysis_repo, _, _, user, issuer = auth_setup
    hasher = BcryptHasher()
    lock_auth = Authenticate(user_repo, hasher, issuer, max_attempts=3, lockout_minutes=15)
    app = tc.app
    app.dependency_overrides[get_authenticate] = lambda: lock_auth
    app.dependency_overrides[get_current_user] = lambda: user

    for _ in range(3):
        resp = tc.post("/v1/auth/login", data={"username": _EMAIL, "password": "errada"})
        assert resp.status_code == 401

    resp = tc.post("/v1/auth/login", data={"username": _EMAIL, "password": _PASSWORD})
    assert resp.status_code == 401
    assert "bloqueada" in resp.json()["detail"]

    app.dependency_overrides.clear()
