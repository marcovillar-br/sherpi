"""Testes do use case RecordReview e SqlAuditRepository."""

from __future__ import annotations

from sqlalchemy import StaticPool, create_engine

from sherpi.contexts.identity.domain.user import Role, User
from sherpi.contexts.review.application.record_review import RecordReview
from sherpi.contexts.review.domain.events import ReviewDecision
from sherpi.contexts.review.infrastructure.repository import SqlAuditRepository
from sherpi.infrastructure.persistence.engine import create_all

_USER = User(id="u1", email="rev@example.com", hashed_password="x", role=Role.REVISOR)


def _make_repo() -> SqlAuditRepository:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    return SqlAuditRepository(engine)


def test_event_is_persisted() -> None:
    repo = _make_repo()
    use_case = RecordReview(repo)
    event = use_case.run("analysis-1", _USER, ReviewDecision.ACCEPT, comment="Ok")
    assert event.analysis_id == "analysis-1"
    assert event.user_id == "u1"
    assert event.decision == ReviewDecision.ACCEPT
    assert event.comment == "Ok"


def test_list_by_analysis_returns_events() -> None:
    repo = _make_repo()
    use_case = RecordReview(repo)
    use_case.run("a1", _USER, ReviewDecision.ACCEPT)
    use_case.run("a1", _USER, ReviewDecision.AMEND, comment="ver art. 319")
    use_case.run("a2", _USER, ReviewDecision.REJECT)

    events_a1 = repo.list_by_analysis("a1")
    assert len(events_a1) == 2
    assert {e.decision for e in events_a1} == {ReviewDecision.ACCEPT, ReviewDecision.AMEND}

    events_a2 = repo.list_by_analysis("a2")
    assert len(events_a2) == 1


def test_append_only_no_update() -> None:
    """Append-only: não existe método de update; dois appends criam dois registros."""
    repo = _make_repo()
    use_case = RecordReview(repo)
    use_case.run("a1", _USER, ReviewDecision.ACCEPT)
    use_case.run("a1", _USER, ReviewDecision.REJECT)
    assert len(repo.list_by_analysis("a1")) == 2
