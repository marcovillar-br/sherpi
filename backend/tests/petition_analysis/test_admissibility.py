"""Testes do domain service CheckAdmissibility (puro)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from sherpi.contexts.petition_analysis.domain.admissibility import (
    CheckAdmissibility,
    Requisito,
    Semaforo,
    parse_valor_causa,
)
from sherpi.contexts.petition_analysis.domain.summary import (
    Parte,
    Pedido,
    PetitionSummary,
    Polo,
)


def _summary(**overrides: object) -> PetitionSummary:
    base = {
        "juizo": "Vara Cível de São Paulo",
        "partes": [
            Parte(nome="Autor", documento="529.982.247-25", polo=Polo.ATIVO),
            Parte(nome="Ré Ltda", documento="11.222.333/0001-81", polo=Polo.PASSIVO),
        ],
        "fato_gerador": "Contrato inadimplido.",
        "fundamentacao": "Arts. 319 e 320 do CPC.",
        "pedidos": [Pedido(descricao="Pagamento")],
        "tem_liminar": False,
        "valor_causa": "R$ 15.000,00",
        "requer_provas": True,
        "opcao_audiencia": True,
        "documentos_mencionados": ["procuração", "contrato"],
    }
    base.update(overrides)
    return PetitionSummary(**base)  # type: ignore[arg-type]


def test_complete_petition_is_green() -> None:
    report = CheckAdmissibility().run(_summary())
    assert report.semaforo is Semaforo.VERDE
    assert report.requer_emenda is False


def test_missing_essential_requires_emenda_and_is_red() -> None:
    report = CheckAdmissibility().run(_summary(pedidos=[]))
    assert report.requer_emenda is True
    assert report.semaforo is Semaforo.VERMELHO
    item = next(i for i in report.itens if i.requisito is Requisito.PEDIDOS)
    assert item.presente is False


def test_missing_nonessential_is_yellow() -> None:
    # Procuração ausente (semântico, não essencial) → amarelo, sem emenda.
    report = CheckAdmissibility().run(_summary(documentos_mencionados=["contrato"]))
    assert report.semaforo is Semaforo.AMARELO
    assert report.requer_emenda is False


def test_juizo_provas_audiencia_sao_verificados() -> None:
    report = CheckAdmissibility().run(_summary())
    for req in (Requisito.JUIZO, Requisito.PROVAS, Requisito.AUDIENCIA):
        item = next(i for i in report.itens if i.requisito is req)
        assert item.presente is True


def test_missing_juizo_provas_audiencia_e_amarelo_sem_emenda() -> None:
    report = CheckAdmissibility().run(
        _summary(juizo=None, requer_provas=False, opcao_audiencia=None)
    )
    assert report.semaforo is Semaforo.AMARELO
    assert report.requer_emenda is False
    ausentes = {i.requisito for i in report.itens if not i.presente}
    assert {Requisito.JUIZO, Requisito.PROVAS, Requisito.AUDIENCIA} <= ausentes


def test_invalid_cpf_fails_qualificacao() -> None:
    report = CheckAdmissibility().run(
        _summary(partes=[Parte(nome="X", documento="111.111.111-11", polo=Polo.ATIVO)])
    )
    item = next(i for i in report.itens if i.requisito is Requisito.QUALIFICACAO)
    assert item.presente is False


def test_valor_causa_provenance_is_normalized() -> None:
    report = CheckAdmissibility().run(_summary(valor_causa="R$ 15.000,00"))
    item = next(i for i in report.itens if i.requisito is Requisito.VALOR_CAUSA)
    assert item.presente is True
    assert item.evidencia == "R$ 15.000,00"


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
def test_parse_valor_causa(texto: str | None, esperado: Decimal | None) -> None:
    result = parse_valor_causa(texto)
    assert (result.amount if result else None) == esperado
