"""Testes dos Value Objects do shared kernel."""

from __future__ import annotations

from decimal import Decimal

import pytest

from sherpi.shared_kernel.value_objects import CNPJ, CPF, ClaimAmount, RiskVerdict


def test_valid_cpf_normalizes_and_formats() -> None:
    cpf = CPF(value="529.982.247-25")
    assert cpf.value == "52998224725"
    assert cpf.formatted == "529.982.247-25"
    assert cpf.masked() == "***.***.247-**"


def test_invalid_cpf_rejected() -> None:
    with pytest.raises(ValueError):
        CPF(value="111.111.111-11")


def test_valid_cnpj() -> None:
    cnpj = CNPJ(value="11.222.333/0001-81")
    assert cnpj.value == "11222333000181"
    assert cnpj.formatted == "11.222.333/0001-81"


def test_invalid_cnpj_rejected() -> None:
    with pytest.raises(ValueError):
        CNPJ(value="00.000.000/0000-00")


def test_invalid_cnpj_homogeneous_rejected() -> None:
    with pytest.raises(ValueError):
        CNPJ(value="11.111.111/1111-11")


def test_cnpj_pesos2_correctness() -> None:
    """pesos2 deve ter 13 elementos (inclui o peso do 1º DV); regressão contra bug de 12."""
    from sherpi.shared_kernel.value_objects import _calcular_digito_cnpj

    base = "112223330001"
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2_13 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv1 = _calcular_digito_cnpj(base, pesos1)
    dv2 = _calcular_digito_cnpj(base + str(dv1), pesos2_13)
    assert f"{dv1}{dv2}" == "81"


def test_claim_amount_formats_brl() -> None:
    assert ClaimAmount(amount=Decimal("15000.50")).formatted == "R$ 15.000,50"


def test_claim_amount_rejects_negative() -> None:
    with pytest.raises(ValueError):
        ClaimAmount(amount=Decimal("-1"))


def test_risk_verdict_values() -> None:
    assert {v.value for v in RiskVerdict} == {"PASS", "WARN", "BLOCK"}
