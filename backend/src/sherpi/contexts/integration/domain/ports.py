from __future__ import annotations

from typing import Protocol, runtime_checkable

from .ingestion import IngestJob


@runtime_checkable
class IngestJobRepository(Protocol):
    def save(self, job: IngestJob) -> None: ...
    def get(self, job_id: str) -> IngestJob | None: ...
    def list_all(self) -> list[IngestJob]: ...
