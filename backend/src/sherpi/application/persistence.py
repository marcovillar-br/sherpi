"""Port de persistência de análises (hexagonal).

O `AnalysisRecord` é o agregado persistido (resultado + metadados). O port
`AnalysisRepository` é implementado por um adapter SQLModel na infraestrutura;
nos testes, por SQLite in-memory. O domínio/aplicação não conhece SQL.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from sherpi.application.analyze_petition import AnalysisResult


class AnalysisRecord(BaseModel):
    """Uma análise persistida (resultado consolidado + metadados)."""

    model_config = {"frozen": True}

    id: str
    created_at: datetime
    filename: str | None
    result: AnalysisResult


@runtime_checkable
class AnalysisRepository(Protocol):
    """Port de armazenamento das análises."""

    def save(self, record: AnalysisRecord) -> None: ...

    def get(self, analysis_id: str) -> AnalysisRecord | None: ...

    def ping(self) -> bool:
        """True se o armazenamento está acessível (usado por /ready)."""
        ...
