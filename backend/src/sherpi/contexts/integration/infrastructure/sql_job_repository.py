from __future__ import annotations

from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.integration.domain.ingestion import IngestJob, IngestStatus
from sherpi.infrastructure.persistence.models import IngestJobRow


class SqlIngestJobRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, job: IngestJob) -> None:
        with Session(self._engine) as s:
            existing = s.get(IngestJobRow, job.id)
            if existing:
                existing.status = job.status
                existing.total = job.total
                existing.processed = job.processed
                existing.failed = job.failed
                existing.finished_at = job.finished_at
                existing.error = job.error
                s.add(existing)
            else:
                s.add(
                    IngestJobRow(
                        id=job.id,
                        source=job.source,
                        tribunal=job.tribunal,
                        date_from=job.date_from,
                        date_to=job.date_to,
                        status=job.status,
                        total=job.total,
                        processed=job.processed,
                        failed=job.failed,
                        created_at=job.created_at,
                        finished_at=job.finished_at,
                        error=job.error,
                    )
                )
            s.commit()

    def get(self, job_id: str) -> IngestJob | None:
        with Session(self._engine) as s:
            row = s.get(IngestJobRow, job_id)
            return self._to_domain(row) if row else None

    def list_all(self) -> list[IngestJob]:
        with Session(self._engine) as s:
            rows = s.exec(select(IngestJobRow)).all()
            return [self._to_domain(r) for r in rows]

    def _to_domain(self, row: IngestJobRow) -> IngestJob:
        return IngestJob(
            id=row.id,
            source=row.source,
            tribunal=row.tribunal,
            date_from=row.date_from,
            date_to=row.date_to,
            status=IngestStatus(row.status),
            total=row.total,
            processed=row.processed,
            failed=row.failed,
            created_at=row.created_at,
            finished_at=row.finished_at,
            error=row.error,
        )
