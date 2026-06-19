"""Criação de engine SQLAlchemy/SQLModel."""

from __future__ import annotations

from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

# Importa os modelos para registrá-los no metadata (create_all / Alembic).
from sherpi.infrastructure.persistence import models  # noqa: F401


def make_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def create_all(engine: Engine) -> None:
    """Cria as tabelas (uso em dev/testes; em produção usa-se Alembic)."""
    SQLModel.metadata.create_all(engine)
