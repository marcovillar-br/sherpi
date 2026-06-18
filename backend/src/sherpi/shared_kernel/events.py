"""Base de Domain Events.

Eventos registram fatos relevantes do domínio (ex.: injeção detectada, análise
concluída, revisão registrada). No MVP são usados para a trilha de auditoria
append-only (Res. CNJ 615/2025); na Fase 4 podem alimentar um message bus.

O timestamp é injetado por quem cria o evento (a camada de aplicação), nunca
gerado dentro do domínio puro — isso mantém o domínio determinístico e testável.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DomainEvent(BaseModel):
    """Fato imutável ocorrido no domínio."""

    model_config = {"frozen": True}

    occurred_at: datetime
    """Momento em que o fato ocorreu (UTC), fornecido pela camada de aplicação."""
