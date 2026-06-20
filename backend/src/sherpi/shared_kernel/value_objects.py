"""Value Objects transversais ao domínio do SHERPI.

São imutáveis e auto-validáveis. Não dependem de framework de I/O, banco ou LLM
— pertencem ao núcleo puro do domínio (linguagem ubíqua compartilhada).
"""

from __future__ import annotations

import re
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, field_validator
from validate_docbr import CPF as _CPFValidator  # noqa: N811 (classe, não constante)

_ONLY_DIGITS = re.compile(r"\D")

# CNPJs com todos os algarismos iguais são inválidos (regra explícita da RFB).
_CNPJ_HOMOGENEOS = {str(d) * 14 for d in range(10)}


def _calcular_digito_cnpj(seq: str, pesos: list[int]) -> int:
    """Módulo-11 para um dígito verificador do CNPJ (suporta base alfanumérica).

    Letras são convertidas pelo padrão RFB: A=10, B=11, …, Z=35.
    """
    soma = sum(
        (int(c) if c.isdigit() else ord(c) - 55) * p for c, p in zip(seq, pesos, strict=False)
    )
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def _validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ numérico *ou* alfanumérico (novo formato RFB, vigência jul/2026).

    Rejeita explicitamente sequências homogêneas (ex.: 00000000000000).
    pesos2 tem 13 elementos — inclui o peso do 1º dígito verificador.
    """
    limpo = "".join(c for c in cnpj if c.isalnum()).upper()
    if len(limpo) != 14 or limpo in _CNPJ_HOMOGENEOS:
        return False
    base = limpo[:12]
    dvs = limpo[12:]
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv1 = _calcular_digito_cnpj(base, pesos1)
    dv2 = _calcular_digito_cnpj(base + str(dv1), pesos2)
    return dvs == f"{dv1}{dv2}"


class RiskVerdict(StrEnum):
    """Veredito do firewall de integridade documental.

    PASS  — documento íntegro, segue para análise cognitiva.
    WARN  — anomalias de baixo risco; segue, mas sinaliza ao revisor humano.
    BLOCK — manipulação grave (ex.: prompt injection); interrompe o fluxo
            ANTES de qualquer chamada a LLM.
    """

    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"


class Rito(StrEnum):
    """Rito processual que define quais regras de admissibilidade se aplicam.

    O firewall e a extração são agnósticos ao rito; o que varia é a
    admissibilidade (e, futuramente, a taxonomia TPU). Ver ADR-0008.

    CIVEL        — CPC art. 319 (rito padrão do MVP).
    TRABALHISTA  — CLT art. 840 §1º (exige pedido líquido).

    Cresce por demanda (PREVIDENCIARIO, FISCAL, …) sem tocar nos ritos existentes.
    """

    CIVEL = "CIVEL"
    TRABALHISTA = "TRABALHISTA"


class CPF(BaseModel):
    """CPF de uma pessoa física, validado por dígitos verificadores."""

    model_config = {"frozen": True}

    value: str

    @field_validator("value")
    @classmethod
    def _validate(cls, raw: str) -> str:
        digits = _ONLY_DIGITS.sub("", raw)
        if not _CPFValidator().validate(digits):
            raise ValueError(f"CPF inválido: {raw!r}")
        return digits

    @property
    def formatted(self) -> str:
        d = self.value
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

    def masked(self) -> str:
        """Mascaramento para logs/UI sem expor o número completo (LGPD)."""
        return f"***.***.{self.value[6:9]}-**"


class CNPJ(BaseModel):
    """CNPJ de uma pessoa jurídica, validado por dígitos verificadores.

    Suporta o novo formato alfanumérico da RFB (vigência julho/2026) além do
    formato numérico tradicional. O valor é armazenado como 14 caracteres
    alfanuméricos em maiúsculas (sem pontuação).
    """

    model_config = {"frozen": True}

    value: str

    @field_validator("value")
    @classmethod
    def _validate(cls, raw: str) -> str:
        limpo = "".join(c for c in raw if c.isalnum()).upper()
        if not _validar_cnpj(limpo):
            raise ValueError(f"CNPJ inválido: {raw!r}")
        return limpo

    @property
    def formatted(self) -> str:
        d = self.value
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


class ClaimAmount(BaseModel):
    """Valor da causa (art. 291 do CPC), em reais."""

    model_config = {"frozen": True}

    amount: Decimal
    currency: str = "BRL"

    @field_validator("amount")
    @classmethod
    def _non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Valor da causa não pode ser negativo")
        return v

    @property
    def formatted(self) -> str:
        return f"R$ {self.amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
