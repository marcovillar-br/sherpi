from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.review.domain.events import AuditEvent


@runtime_checkable
class AuditRepository(Protocol):
    def append(self, event: AuditEvent) -> None: ...

    def list_by_analysis(self, analysis_id: str) -> list[AuditEvent]: ...

    def latest_by_analyses(self, analysis_ids: list[str]) -> dict[str, AuditEvent]:
        """Para cada id, o evento de revisão mais recente (para o histórico)."""
        ...
