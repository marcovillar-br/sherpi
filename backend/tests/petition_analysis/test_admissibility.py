"""Testes do domain service CheckAdmissibility (puro)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from sherpi.contexts.petition_analysis.domain.admissibility import (
    AdmissibilityStatus,
    CheckAdmissibility,
    Requirement,
    parse_claim_amount,
)
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)
from sherpi.shared_kernel.value_objects import Rito


def _summary(**overrides: object) -> PetitionSummary:
    base = {
        "court": "Vara Cível de São Paulo",
        "parties": [
            Parte(name="Autor", document="529.982.247-25", pole=Polo.ACTIVE),
            Parte(name="Ré Ltda", document="11.222.333/0001-81", pole=Polo.PASSIVE),
        ],
        "facts": "Contrato inadimplido.",
        "legal_basis": "Arts. 319 e 320 do CPC.",
        "claims": [Pedido(description="Pagamento")],
        "has_injunction": False,
        "claim_amount": "R$ 15.000,00",
        "requests_evidence": True,
        "hearing_option": True,
        "cited_documents": ["procuração", "contrato"],
    }
    base.update(overrides)
    return PetitionSummary(**base)  # type: ignore[arg-type]


def test_complete_petition_is_green() -> None:
    report = CheckAdmissibility().run(_summary())
    assert report.status is AdmissibilityStatus.GREEN
    assert report.requires_amendment is False


def test_missing_essential_requires_emenda_and_is_red() -> None:
    report = CheckAdmissibility().run(_summary(claims=[]))
    assert report.requires_amendment is True
    assert report.status is AdmissibilityStatus.RED
    item = next(i for i in report.items if i.requirement is Requirement.CLAIMS)
    assert item.present is False


def test_missing_nonessential_is_yellow() -> None:
    # Procuração ausente (semântico, não essencial) → amarelo, sem emenda.
    report = CheckAdmissibility().run(_summary(cited_documents=["contrato"]))
    assert report.status is AdmissibilityStatus.YELLOW
    assert report.requires_amendment is False


def test_court_evidence_hearing_are_checked() -> None:
    report = CheckAdmissibility().run(_summary())
    for req in (Requirement.COURT, Requirement.EVIDENCE, Requirement.HEARING):
        item = next(i for i in report.items if i.requirement is req)
        assert item.present is True


def test_missing_court_evidence_hearing_is_yellow_no_amendment() -> None:
    report = CheckAdmissibility().run(
        _summary(court=None, requests_evidence=False, hearing_option=None)
    )
    assert report.status is AdmissibilityStatus.YELLOW
    assert report.requires_amendment is False
    missing = {i.requirement for i in report.items if not i.present}
    assert {Requirement.COURT, Requirement.EVIDENCE, Requirement.HEARING} <= missing


def test_invalid_cpf_fails_qualification() -> None:
    report = CheckAdmissibility().run(
        _summary(parties=[Parte(name="X", document="111.111.111-11", pole=Polo.ACTIVE)])
    )
    item = next(i for i in report.items if i.requirement is Requirement.QUALIFICATION)
    assert item.present is False


def test_claim_amount_provenance_is_normalized() -> None:
    report = CheckAdmissibility().run(_summary(claim_amount="R$ 15.000,00"))
    item = next(i for i in report.items if i.requirement is Requirement.CLAIM_VALUE)
    assert item.present is True
    assert item.evidence == "R$ 15.000,00"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("R$ 15.000,00", Decimal("15000.00")),
        ("1.234.567,89", Decimal("1234567.89")),
        ("5000", Decimal("5000")),
        ("", None),
        (None, None),
        ("abc", None),
    ],
)
def test_parse_claim_amount(texto: str | None, esperado: Decimal | None) -> None:
    result = parse_claim_amount(texto)
    assert (result.amount if result else None) == esperado


# --- Despacho por rito (rito-aware, ADR-0008) ------------------------------------


def test_default_rito_e_civel() -> None:
    # Sem rito explícito == cível: petição completa segue verde.
    assert CheckAdmissibility().run(_summary()).status is AdmissibilityStatus.GREEN
    assert CheckAdmissibility().run(_summary(), Rito.CIVEL).status is AdmissibilityStatus.GREEN


def test_civel_nao_exige_pedido_liquido() -> None:
    # Pedido sem valor é admissível no cível (não há requisito LIQUID_CLAIM).
    report = CheckAdmissibility().run(_summary(), Rito.CIVEL)
    assert report.status is AdmissibilityStatus.GREEN
    assert all(i.requirement is not Requirement.LIQUID_CLAIM for i in report.items)


def test_trabalhista_pedido_liquido_e_verde() -> None:
    report = CheckAdmissibility().run(
        _summary(claims=[Pedido(description="Aviso prévio", amount="R$ 2.500,00")]),
        Rito.TRABALHISTA,
    )
    assert report.status is AdmissibilityStatus.GREEN
    assert report.requires_amendment is False
    item = next(i for i in report.items if i.requirement is Requirement.LIQUID_CLAIM)
    assert item.present is True


def test_trabalhista_pedido_iliquido_exige_emenda() -> None:
    # Pedido sem valor (default do _summary) viola CLT 840 §1º no rito trabalhista.
    report = CheckAdmissibility().run(_summary(), Rito.TRABALHISTA)
    assert report.status is AdmissibilityStatus.RED
    assert report.requires_amendment is True
    item = next(i for i in report.items if i.requirement is Requirement.LIQUID_CLAIM)
    assert item.present is False
    assert item.evidence == "Pagamento"  # descrição do pedido ilíquido


def test_trabalhista_cumulacao_liquida_e_verde() -> None:
    claims = [
        Pedido(description="Aviso prévio", amount="R$ 2.500,00"),
        Pedido(description="Férias + 1/3", amount="R$ 1.111,00"),
        Pedido(description="13º proporcional", amount="R$ 833,00"),
    ]
    report = CheckAdmissibility().run(_summary(claims=claims), Rito.TRABALHISTA)
    assert report.status is AdmissibilityStatus.GREEN
    assert report.requires_amendment is False
