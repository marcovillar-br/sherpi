"""Testes das entidades ANCORADAS por contexto (RG/CNH, benefício INSS, dados
bancários, nº de B.O.) — identificadores que só são PII pelo rótulo e que, antes,
vazavam em claro ao LLM externo.

Os valores usados aqui são os que de fato vazaram numa petição sintética auditada
(`from_template`), servindo de regressão para aquele incidente.
"""

from __future__ import annotations

from sherpi.infrastructure.anonymization.regex import (
    MappedRegexAnonymizer,
    RegexAnonymizer,
)


def test_mascara_rg_preservando_rotulo() -> None:
    texto = "portador da Carteira de Identidade/CNH nº: 4.338.617 SSP/DF"
    out = RegexAnonymizer().anonymize(texto)
    assert "4.338.617" not in out
    assert "[RG]" in out
    assert "Carteira de Identidade/CNH" in out  # rótulo preservado
    assert "SSP/DF" in out  # órgão expedidor não é mascarado


def test_mascara_beneficio_inss_com_cara_de_cpf() -> None:
    # 997.835.422-3: forma de CPF, mas com 1 só DV → o regex de CPF não pega.
    texto = "é aposentada/pensionista do INSS, sob o benefício nº 997.835.422-3 ."
    out = RegexAnonymizer().anonymize(texto)
    assert "997.835.422-3" not in out
    assert "[BENEFICIO]" in out
    assert "[CPF]" not in out  # não foi confundido com CPF


def test_mascara_dados_bancarios() -> None:
    texto = "na conta bancária, a saber: Banco 001, agência 9179, conta 61856-7 ."
    out = RegexAnonymizer().anonymize(texto)
    for valor in ("001", "9179", "61856-7"):
        assert valor not in out
    assert "[BANCO]" in out and "[AGENCIA]" in out and "[CONTA]" in out


def test_mascara_ocorrencia_policial() -> None:
    texto = "comunicou o fato à autoridade policial, sob a Ocorrência de nº 694731 ,"
    out = RegexAnonymizer().anonymize(texto)
    assert "694731" not in out
    assert "[OCORRENCIA]" in out


def test_banco_do_brasil_nao_e_mascarado_como_codigo() -> None:
    # "Banco do Brasil" não tem dígitos → o padrão de código bancário não dispara.
    out = RegexAnonymizer().anonymize("mantém conta no Banco do Brasil há anos")
    assert "Banco do Brasil" in out
    assert "[BANCO]" not in out


def test_mapeamento_reversivel_das_entidades_ancoradas() -> None:
    anon = MappedRegexAnonymizer()
    texto = (
        "Carteira de Identidade/CNH nº: 4.338.617 SSP/DF, benefício nº 997.835.422-3, "
        "Banco 001, agência 9179, conta 61856-7, Ocorrência de nº 694731."
    )
    result, mapping = anon.anonymize_mapped(texto)

    # nenhum valor sensível remanesce no texto enviado ao LLM
    for valor in ("4.338.617", "997.835.422-3", "9179", "61856-7", "694731"):
        assert valor not in result
    # e o mapa reverte cada placeholder ao valor original (ADR-0012)
    assert mapping["[RG_1]"] == "4.338.617"
    assert mapping["[BENEFICIO_1]"] == "997.835.422-3"
    assert mapping["[AGENCIA_1]"] == "9179"
    assert mapping["[CONTA_1]"] == "61856-7"
    assert mapping["[OCORRENCIA_1]"] == "694731"


def test_numero_solto_sem_rotulo_nao_e_mascarado() -> None:
    # Sem âncora, um número qualquer é inócuo e não deve ser tocado (evita falso-positivo).
    out = RegexAnonymizer().anonymize("o processo levou 9179 dias para tramitar")
    assert "9179" in out
    assert "[AGENCIA]" not in out
