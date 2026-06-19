"""Modelos de persistência (SQLModel).

Todos os modelos de tabela vivem aqui para que `engine.py` os registre em
`SQLModel.metadata` com uma única importação — sem risco de ciclos de importação.
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


class UserRow(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str
    is_active: bool = True


class AuditEventRow(SQLModel, table=True):
    __tablename__ = "audit_events"

    id: str = Field(primary_key=True)
    analysis_id: str = Field(index=True)
    user_id: str
    user_email: str
    decision: str
    comment: str | None = None
    created_at: datetime


class TpuEntryRow(SQLModel, table=True):
    __tablename__ = "tpu_entries"

    id: str = Field(primary_key=True)
    tpu_code: str = Field(index=True)
    description: str
    rito: str
    text_excerpt: str
    embedding: bytes
    embedding_dim: int
