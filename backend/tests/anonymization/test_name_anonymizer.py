"""Testes do mascaramento de nomes por âncora (RegexNameAnonymizer) e composição."""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.anonymization.factory import build_anonymizer
from sherpi.infrastructure.anonymization.regex import (
    CompositeAnonymizer,
    MappedCompositeAnonymizer,
    MappedRegexAnonymizer,
    NoOpAnonymizer,
    RegexAnonymizer,
    RegexNameAnonymizer,
)

_NAMER = RegexNameAnonymizer()


def test_masks_person_name_before_qualification_cue() -> None:
    out = _NAMER.anonymize("FULANO DE TAL, brasileiro, solteiro, inscrito no CPF sob o nº X")
    assert out.startswith("[NOME], brasileiro")
    assert "FULANO" not in out


def test_masks_company_before_pessoa_juridica() -> None:
    out = _NAMER.anonymize("EMPRESA EXEMPLO LTDA., pessoa jurídica inscrita no CNPJ")
    assert out.startswith("[NOME], pessoa jurídica")
    assert "EMPRESA" not in out


def test_masks_name_after_em_face_de() -> None:
    out = _NAMER.anonymize("propor a presente ação em face de João da Silva, já qualificado")
    assert "em face de [NOME]" in out
    assert "João" not in out


def test_masks_titlecase_person_with_connectors() -> None:
    out = _NAMER.anonymize("Maria dos Santos Oliveira, brasileira, casada")
    assert out.startswith("[NOME], brasileira")


def test_does_not_mask_capitalized_non_names() -> None:
    # Sem cue de qualificação → não mascara (endereço, cidade, títulos).
    text = "residente na Rua das Flores, nº 100, São Paulo/SP, CEP 01310-100"
    assert _NAMER.anonymize(text) == text


def test_does_not_mask_heading() -> None:
    text = "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA VARA CÍVEL"
    assert _NAMER.anonymize(text) == text


def test_does_not_swallow_enderecamento_into_name() -> None:
    # Regressão: o nome abutta o endereçamento (juntados por espaço no visible_text).
    out = _NAMER.anonymize("JUIZ(A) DE DIREITO DA VARA CÍVEL FULANO DE TAL, brasileiro")
    assert "VARA CÍVEL" in out  # endereçamento preservado
    assert "[NOME], brasileiro" in out
    assert "FULANO" not in out


def test_masks_comma_separated_name_list() -> None:
    # Litisconsórcio: lista separada por vírgula/"e" antes do cue — nenhum vaza.
    out = _NAMER.anonymize("MARIA DA SILVA, JOÃO DOS SANTOS e PEDRO LIMA, brasileiros, casados")
    assert "MARIA" not in out
    assert "JOÃO" not in out
    assert "PEDRO" not in out
    assert "[NOME]" in out and "brasileiros" in out


def test_masks_multiple_reus_after_em_face_de() -> None:
    out = _NAMER.anonymize("em face de FULANO DE TAL e de SICRANO DE TAL, ambos brasileiros")
    assert "FULANO" not in out
    assert "SICRANO" not in out
    assert "TAL" not in out
    assert out.startswith("em face de [NOME]")


def test_masks_two_authors_each_with_own_qualification() -> None:
    out = _NAMER.anonymize(
        "FULANO DE TAL, brasileiro, solteiro, e BELTRANA DE SOUZA, brasileira, casada,"
    )
    assert "FULANO" not in out and "BELTRANA" not in out
    assert out.count("[NOME]") == 2


def test_name_does_not_cross_block_boundary() -> None:
    # Título e qualificação em blocos distintos (\n entre eles, via visible_text por
    # bloco). O nome não cruza a quebra — mesmo sem o título ser stopword.
    out = _NAMER.anonymize("RELATÓRIO FINAL\nFULANO DE TAL, brasileiro")
    assert out == "RELATÓRIO FINAL\n[NOME], brasileiro"


def test_nao_mascara_uf_como_nome() -> None:
    # Regressão: "DF" (UF) logo antes da deixa "inscrito no CPF" virava [NOME],
    # corrompendo o órgão expedidor "SSP/DF".
    out = _NAMER.anonymize("portador do RG 4.338.617 SSP/DF, inscrito no CPF sob o nº X")
    assert "SSP/DF" in out
    assert "[NOME]" not in out


def test_nao_mascara_letra_isolada_em_forma_societaria() -> None:
    # Regressão: o "A" de "S/A" (1 letra) antes de "pessoa jurídica" virava [NOME],
    # partindo a razão social em "... S/[NOME]".
    out = _NAMER.anonymize("em desfavor de DELTA COMUNICAÇÕES S/A, pessoa jurídica de direito")
    assert "S/A" in out
    assert "S/[NOME]" not in out


def test_ainda_mascara_razao_social_com_sufixo_multicaractere() -> None:
    # Garante que o ajuste de precisão não regrediu o masking de razão social legítima.
    out = _NAMER.anonymize("EMPRESA EXEMPLO LTDA., pessoa jurídica inscrita no CNPJ")
    assert "EMPRESA" not in out and out.startswith("[NOME],")


def test_masks_party_name_after_label_when_cue_is_separated() -> None:
    # Regressão (template TJDFT): o cue "brasileiro" fica separado do nome pelo rótulo
    # "nacionalidade:", então o anchor por cue não pega. O anchor por rótulo de polo sim.
    out = _NAMER.anonymize("PARTE REQUERENTE :  Daniel Almeida Rocha ,  nacionalidade: brasileiro(a)")
    assert "Daniel" not in out and "Rocha" not in out
    assert "[NOME]" in out
    assert "nacionalidade: brasileiro(a)" in out  # rótulo seguinte preservado


def test_masks_reu_after_party_label_with_intervening_label() -> None:
    out = _NAMER.anonymize("em face da PARTE REQUERIDA :  Igor Lima Costa ,  nacionalidade: brasileiro")
    assert "Igor" not in out and "Costa" not in out
    assert "PARTE REQUERIDA :" in out and "[NOME]" in out


def test_masks_trabalhista_labels() -> None:
    out = _NAMER.anonymize("RECLAMANTE: João Pereira, profissão: pedreiro")
    assert "João" not in out and "Pereira" not in out
    assert out.startswith("RECLAMANTE: [NOME]")


def test_party_label_does_not_match_autoridade() -> None:
    # "AUTOR" não pode disparar dentro de "AUTORIDADE:" (sem dois-pontos logo após).
    text = "encaminhado à AUTORIDADE: Delegacia de Polícia"
    # Não deve mascarar como nome de parte (não há rótulo de polo seguido de pessoa).
    assert _NAMER.anonymize(text) == text


def test_composite_applies_structured_then_names() -> None:
    comp = CompositeAnonymizer([RegexAnonymizer(), RegexNameAnonymizer()])
    out = comp.anonymize("FULANO DE TAL, brasileiro, CPF 529.982.247-25, e-mail a@b.com")
    assert "[NOME]" in out
    assert "[CPF]" in out
    assert "[EMAIL]" in out
    assert "FULANO" not in out and "529.982" not in out


def test_factory_external_with_names_is_composite() -> None:
    anon = build_anonymizer(Settings(llm_backend="gemini", anonymize_names=True))
    assert isinstance(anon, MappedCompositeAnonymizer)  # reversível (estruturado + nomes)


def test_factory_external_without_names_is_regex_only() -> None:
    anon = build_anonymizer(Settings(llm_backend="gemini", anonymize_names=False))
    assert isinstance(anon, MappedRegexAnonymizer)


def test_factory_local_llm_is_noop() -> None:
    anon = build_anonymizer(Settings(llm_backend="fake", anonymize_names=True))
    assert isinstance(anon, NoOpAnonymizer)
