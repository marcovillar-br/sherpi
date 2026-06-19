from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ReviewDecision(StrEnum):
    ACEITAR = "ACEITAR"
    REJEITAR = "REJEITAR"
    CORRIGIR = "CORRIGIR"


class AuditEvent(BaseModel):
    model_config = {"frozen": True}

    id: str
    analysis_id: str
    user_id: str
    user_email: str
    decision: ReviewDecision
    comment: str | None = None
    created_at: datetime
