"""Testes do use case Authenticate (credenciais, lockout)."""

from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine

from sherpi.contexts.identity.application.authenticate import Authenticate
from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.issuer import JwtIssuer
from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.identity.infrastructure.repository import SqlUserRepository
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.shared_kernel.errors import AuthenticationError

_SECRET = "test-secret-key-must-be-32-bytes!"
_EMAIL = "test@example.com"
_PASSWORD = "s3cr3t!"


def _make_repo() -> SqlUserRepository:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    return SqlUserRepository(engine)


def _make_auth(repo: SqlUserRepository, max_attempts: int = 5) -> Authenticate:
    hasher = BcryptHasher()
    issuer = JwtIssuer(_SECRET)
    return Authenticate(repo, hasher, issuer, max_attempts=max_attempts, lockout_minutes=15)


def _seed_user(repo: SqlUserRepository) -> User:
    hasher = BcryptHasher()
    user = User(
        id="u1",
        email=_EMAIL,
        hashed_password=hasher.hash(_PASSWORD),
        role=Role.REVISOR,
    )
    repo.save(user)
    return user


def test_correct_credentials_returns_token() -> None:
    repo = _make_repo()
    _seed_user(repo)
    auth = _make_auth(repo)
    token = auth.run(_EMAIL, _PASSWORD)
    assert isinstance(token, str)
    payload = JwtIssuer(_SECRET).verify(token)
    assert payload["sub"] == "u1"


def test_wrong_password_raises() -> None:
    repo = _make_repo()
    _seed_user(repo)
    auth = _make_auth(repo)
    with pytest.raises(AuthenticationError, match="Credenciais"):
        auth.run(_EMAIL, "wrong")


def test_unknown_email_raises() -> None:
    repo = _make_repo()
    auth = _make_auth(repo)
    with pytest.raises(AuthenticationError, match="Credenciais"):
        auth.run("nobody@x.com", _PASSWORD)


def test_lockout_after_max_attempts() -> None:
    repo = _make_repo()
    _seed_user(repo)
    auth = _make_auth(repo, max_attempts=3)
    for _ in range(3):
        with pytest.raises(AuthenticationError):
            auth.run(_EMAIL, "wrong")
    with pytest.raises(AuthenticationError, match="bloqueada"):
        auth.run(_EMAIL, _PASSWORD)


def test_success_resets_lockout_counter() -> None:
    repo = _make_repo()
    _seed_user(repo)
    auth = _make_auth(repo, max_attempts=3)
    for _ in range(2):
        with pytest.raises(AuthenticationError):
            auth.run(_EMAIL, "wrong")
    auth.run(_EMAIL, _PASSWORD)  # deve ter sucesso e resetar
    # não deve estar bloqueado agora
    token = auth.run(_EMAIL, _PASSWORD)
    assert token
