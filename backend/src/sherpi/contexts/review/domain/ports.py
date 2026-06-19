from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.review.domain.events import AuditEvent


@runtime_checkable
class AuditRepository(Protocol):
    def append(self, event: AuditEvent) -> None: ...

    def list_by_analysis(self, analysis_id: str) -> list[AuditEvent]: ...
