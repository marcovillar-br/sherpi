"""Modelos do laudo forense produzido pelo firewall."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from sherpi.shared_kernel.value_objects import RiskVerdict


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyType(StrEnum):
    """Vetores de manipulação mapeados na pesquisa (seção 2.3)."""

    WHITE_ON_WHITE = "WHITE_ON_WHITE"  # fonte na cor do fundo (invisível)
    TINY_FONT = "TINY_FONT"  # fonte microscópica (< 1pt)
    OFF_CROPBOX = "OFF_CROPBOX"  # texto fora da área visível da página
    ZERO_WIDTH_UNICODE = "ZERO_WIDTH_UNICODE"  # caracteres invisíveis (U+200B etc.)
    HIDDEN_OCG_LAYER = "HIDDEN_OCG_LAYER"  # camada de conteúdo desativada
    ACTUALTEXT_DIVERGENCE = "ACTUALTEXT_DIVERGENCE"  # /ActualText ≠ texto renderizado
    SUSPICIOUS_METADATA = "SUSPICIOUS_METADATA"  # comandos imperativos em metadados
    INJECTION_KEYWORDS = "INJECTION_KEYWORDS"  # comando à IA em texto oculto


# Peso de cada severidade no escore de risco.
_SEVERITY_WEIGHT: dict[Severity, float] = {
    Severity.LOW: 0.15,
    Severity.MEDIUM: 0.4,
    Severity.HIGH: 0.7,
    Severity.CRITICAL: 1.0,
}


class Anomaly(BaseModel):
    """Uma evidência de manipulação encontrada no documento."""

    model_config = {"frozen": True}

    type: AnomalyType
    severity: Severity
    detail: str
    page: int | None = None
    evidence: str | None = None  # trecho (já truncado) para o laudo do revisor


class ForensicsReport(BaseModel):
    """Laudo consolidado do firewall.

    `verdict` governa o orquestrador: BLOCK interrompe ANTES de qualquer LLM.
    """

    model_config = {"frozen": True}

    verdict: RiskVerdict
    risk_score: float  # 0.0 (íntegro) .. 1.0 (manipulação grave)
    anomalies: list[Anomaly]

    @property
    def blocked(self) -> bool:
        return self.verdict is RiskVerdict.BLOCK

    @classmethod
    def from_anomalies(cls, anomalies: list[Anomaly]) -> ForensicsReport:
        """Deriva escore e veredito a partir das anomalias encontradas.

        Regra: qualquer anomalia HIGH/CRITICAL ⇒ BLOCK; qualquer MEDIUM ⇒ WARN;
        só LOW ⇒ WARN; nenhuma ⇒ PASS. Escore = maior peso observado.
        """
        if not anomalies:
            return cls(verdict=RiskVerdict.PASS, risk_score=0.0, anomalies=[])

        score = max(_SEVERITY_WEIGHT[a.severity] for a in anomalies)
        worst = max((a.severity for a in anomalies), key=lambda s: _SEVERITY_WEIGHT[s])
        if worst in (Severity.HIGH, Severity.CRITICAL):
            verdict = RiskVerdict.BLOCK
        else:
            verdict = RiskVerdict.WARN
        return cls(verdict=verdict, risk_score=round(score, 3), anomalies=anomalies)
