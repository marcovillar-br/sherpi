from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ReviewDecision(StrEnum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    AMEND = "AMEND"


class AuditEvent(BaseModel):
    model_config = {"frozen": True}

    id: str
    analysis_id: str
    user_id: str
    user_email: str
    decision: ReviewDecision
    comment: str | None = None
    created_at: datetime
