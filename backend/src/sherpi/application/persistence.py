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


class AnalysisSummary(BaseModel):
    """Resumo leve de uma análise, para a listagem do histórico.

    Deriva do `result` os sinais que o revisor lê de relance (veredito do
    firewall, status de admissibilidade, liminar) sem carregar o resultado inteiro.
    `admissibility_status`/`has_injunction` são None quando o firewall bloqueou
    (não houve análise cognitiva).
    """

    model_config = {"frozen": True}

    id: str
    created_at: datetime
    filename: str | None
    verdict: str  # firewall: PASS / WARN / BLOCK
    rito: str
    admissibility_status: str | None  # GREEN / YELLOW / RED
    has_injunction: bool | None


@runtime_checkable
class AnalysisRepository(Protocol):
    """Port de armazenamento das análises."""

    def save(self, record: AnalysisRecord) -> None: ...

    def get(self, analysis_id: str) -> AnalysisRecord | None: ...

    def list_recent(self, limit: int = 50) -> list[AnalysisSummary]:
        """Resumos das análises mais recentes (ordem decrescente por data)."""
        ...

    def delete(self, analysis_id: str) -> bool:
        """Remove a análise. Retorna True se existia."""
        ...

    def list_older_than(self, cutoff: datetime) -> list[str]:
        """IDs de análises criadas antes de `cutoff` (LGPD — retenção)."""
        ...

    def ping(self) -> bool:
        """True se o armazenamento está acessível (usado por /ready)."""
        ...
