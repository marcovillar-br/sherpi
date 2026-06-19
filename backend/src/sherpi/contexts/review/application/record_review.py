from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sherpi.contexts.identity.domain.user import User
from sherpi.contexts.review.domain.events import AuditEvent, ReviewDecision
from sherpi.contexts.review.domain.ports import AuditRepository


class RecordReview:
    def __init__(self, repo: AuditRepository) -> None:
        self._repo = repo

    def run(
        self,
        analysis_id: str,
        user: User,
        decision: ReviewDecision,
        comment: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=uuid.uuid4().hex,
            analysis_id=analysis_id,
            user_id=user.id,
            user_email=user.email,
            decision=decision,
            comment=comment,
            created_at=datetime.now(UTC),
        )
        self._repo.append(event)
        return event
