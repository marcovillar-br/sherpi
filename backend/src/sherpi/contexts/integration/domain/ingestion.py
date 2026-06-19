from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel


class IngestStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class IngestJob(BaseModel):
    model_config = {"frozen": False}

    id: str
    source: str
    tribunal: str
    date_from: date
    date_to: date
    status: IngestStatus = IngestStatus.QUEUED
    total: int = 0
    processed: int = 0
    failed: int = 0
    created_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
