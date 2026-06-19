"""Adapter SQLModel do port `AnalysisRepository`."""

from __future__ import annotations

from sqlalchemy import Engine, text
from sqlmodel import Session

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

    def ping(self) -> bool:
        try:
            with Session(self._engine) as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:  # qualquer falha de conexão = não pronto
            return False
