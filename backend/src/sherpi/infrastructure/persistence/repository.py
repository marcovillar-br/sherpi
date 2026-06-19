"""Adapter SQLModel do port `AnalysisRepository`."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text
from sqlmodel import Session, select

from sherpi.application.analyze_petition import AnalysisResult
from sherpi.application.persistence import AnalysisRecord
from sherpi.infrastructure.persistence.models import AnalysisRow


class SqlAnalysisRepository:
    """Implementa `AnalysisRepository` sobre SQLModel/SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, record: AnalysisRecord) -> None:
        row = AnalysisRow(
            id=record.id,
            created_at=record.created_at,
            filename=record.filename,
            verdict=record.result.forensics.verdict.value,
            result_json=record.result.model_dump_json(),
        )
        with Session(self._engine) as session:
            session.add(row)
            session.commit()

    def get(self, analysis_id: str) -> AnalysisRecord | None:
        with Session(self._engine) as session:
            row = session.get(AnalysisRow, analysis_id)
            if row is None:
                return None
            return AnalysisRecord(
                id=row.id,
                created_at=row.created_at,
                filename=row.filename,
                result=AnalysisResult.model_validate_json(row.result_json),
            )

    def delete(self, analysis_id: str) -> bool:
        with Session(self._engine) as session:
            row = session.get(AnalysisRow, analysis_id)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    def list_older_than(self, cutoff: datetime) -> list[str]:
        with Session(self._engine) as session:
            rows = session.exec(select(AnalysisRow).where(AnalysisRow.created_at < cutoff)).all()
            return [r.id for r in rows]

    def ping(self) -> bool:
        try:
            with Session(self._engine) as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:  # qualquer falha de conexão = não pronto
            return False
