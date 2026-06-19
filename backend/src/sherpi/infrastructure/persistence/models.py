"""Modelos de persistência (SQLModel).

A análise consolidada é guardada como JSON (`result_json`), preservando a
estrutura rica do resultado; colunas dedicadas (`verdict`, `created_at`)
permitem consulta/filtragem. Portável entre SQLite (testes) e Postgres (prod).
"""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class AnalysisRow(SQLModel, table=True):
    __tablename__ = "analyses"

    id: str = Field(primary_key=True)
    created_at: datetime
    filename: str | None = Field(default=None)
    verdict: str = Field(index=True)
    result_json: str
