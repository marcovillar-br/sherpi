"""Adapter SQLModel do port `AnalysisRepository`."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text
from sqlmodel import Session, col, select

from sherpi.application.analyze_petition import AnalysisResult
from sherpi.application.persistence import AnalysisRecord, AnalysisSummary
from sherpi.infrastructure.llm.audit_store import LLMCall
from sherpi.infrastructure.persistence.models import AnalysisRow, LLMCallRow


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

    def list_recent(self, limit: int = 50) -> list[AnalysisSummary]:
        with Session(self._engine) as session:
            rows = session.exec(
                select(AnalysisRow).order_by(col(AnalysisRow.created_at).desc()).limit(limit)
            ).all()
            summaries: list[AnalysisSummary] = []
            for row in rows:
                result = AnalysisResult.model_validate_json(row.result_json)
                summaries.append(
                    AnalysisSummary(
                        id=row.id,
                        created_at=row.created_at,
                        filename=row.filename,
                        verdict=row.verdict,
                        rito=result.rito.value,
                        admissibility_status=(
                            result.admissibility.status.value if result.admissibility else None
                        ),
                        has_injunction=(result.summary.has_injunction if result.summary else None),
                    )
                )
            return summaries

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


class SqlLLMCallRepository:
    """Implementa `LLMCallRepository` sobre SQLModel/SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def append(self, call: LLMCall) -> None:
        row = LLMCallRow(
            id=call.id,
            analysis_id=call.analysis_id,
            call_type=call.call_type,
            model=call.model,
            prompt=call.prompt,
            response=call.response,
            prompt_chars=call.prompt_chars,
            response_chars=call.response_chars,
            duration_ms=call.duration_ms,
            created_at=call.created_at,
        )
        with Session(self._engine) as session:
            session.add(row)
            session.commit()

    def list_by_analysis(self, analysis_id: str) -> list[LLMCall]:
        with Session(self._engine) as session:
            rows = session.exec(
                select(LLMCallRow)
                .where(LLMCallRow.analysis_id == analysis_id)
                .order_by(col(LLMCallRow.created_at))
            ).all()
            return [
                LLMCall(
                    id=r.id,
                    analysis_id=r.analysis_id,
                    call_type=r.call_type,
                    model=r.model,
                    prompt=r.prompt,
                    response=r.response,
                    prompt_chars=r.prompt_chars,
                    response_chars=r.response_chars,
                    duration_ms=r.duration_ms,
                    created_at=r.created_at,
                )
                for r in rows
            ]
