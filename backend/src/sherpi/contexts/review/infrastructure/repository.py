from __future__ import annotations

from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.review.domain.events import AuditEvent, ReviewDecision
from sherpi.infrastructure.persistence.models import AuditEventRow


class SqlAuditRepository:
    """Repositório append-only de eventos de auditoria — nunca atualiza nem deleta."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def append(self, event: AuditEvent) -> None:
        with Session(self._engine) as s:
            s.add(
                AuditEventRow(
                    id=event.id,
                    analysis_id=event.analysis_id,
                    user_id=event.user_id,
                    user_email=event.user_email,
                    decision=event.decision,
                    comment=event.comment,
                    created_at=event.created_at,
                )
            )
            s.commit()

    def list_by_analysis(self, analysis_id: str) -> list[AuditEvent]:
        with Session(self._engine) as s:
            rows = s.exec(
                select(AuditEventRow).where(AuditEventRow.analysis_id == analysis_id)
            ).all()
            return [
                AuditEvent(
                    id=r.id,
                    analysis_id=r.analysis_id,
                    user_id=r.user_id,
                    user_email=r.user_email,
                    decision=ReviewDecision(r.decision),
                    comment=r.comment,
                    created_at=r.created_at,
                )
                for r in rows
            ]
