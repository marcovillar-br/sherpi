"""Restauração reversível: anonimiza só p/ a LLM, restaura os valores reais."""

from __future__ import annotations

from sherpi.application.deanonymize import deanonymize_model, restore_text
from sherpi.contexts.petition_analysis.domain.summary import Parte, PetitionSummary, Polo
from sherpi.infrastructure.anonymization.regex import (
    MappedCompositeAnonymizer,
    MappedRegexAnonymizer,
    MappedRegexNameAnonymizer,
)


def test_restore_text_replaces_placeholders() -> None:
    out = restore_text("[NOME_1] tem CPF [CPF_1]", {"[NOME_1]": "João", "[CPF_1]": "111"})
    assert out == "João tem CPF 111"


def test_restore_text_longer_keys_first() -> None:
    # [CPF_1] não pode corromper [CPF_11].
    out = restore_text("[CPF_11]", {"[CPF_1]": "A", "[CPF_11]": "B"})
    assert out == "B"


def test_mapped_name_anonymizer_numbers_and_maps() -> None:
    masked, mapping = MappedRegexNameAnonymizer().anonymize_mapped(
        "MARIA DA SILVA, brasileira, e JOÃO LIMA, brasileiro"
    )
    assert "MARIA" not in masked and "JOÃO" not in masked
    assert "[NOME_1]" in masked and "[NOME_2]" in masked
    assert mapping["[NOME_1]"] == "MARIA DA SILVA"
    assert mapping["[NOME_2]"] == "JOÃO LIMA"


def test_roundtrip_restores_real_values_in_summary() -> None:
    anon = MappedCompositeAnonymizer([MappedRegexAnonymizer(), MappedRegexNameAnonymizer()])
    text = "FULANO DE TAL, brasileiro, inscrito no CPF sob o nº 529.982.247-25"
    masked, mapping = anon.anonymize_mapped(text)
    assert "FULANO" not in masked and "529.982" not in masked

    # Resumo como a LLM devolveria (com os placeholders).
    name_ph = next(k for k in mapping if k.startswith("[NOME"))
    cpf_ph = next(k for k in mapping if k.startswith("[CPF"))
    summary = PetitionSummary(
        parties=[Parte(name=name_ph, document=cpf_ph, pole=Polo.ACTIVE)],
        facts=f"{name_ph} cobra a dívida.",
        legal_basis="CPC.",
        has_injunction=False,
    )
    restored = deanonymize_model(summary, mapping)
    assert restored.parties[0].name == "FULANO DE TAL"
    assert restored.parties[0].document == "529.982.247-25"
    assert "[NOME" not in restored.facts


def test_deanonymize_model_noop_without_mapping() -> None:
    summary = PetitionSummary(
        parties=[Parte(name="João", document="111", pole=Polo.ACTIVE)],
        facts="x",
        legal_basis="y",
        has_injunction=False,
    )
    assert deanonymize_model(summary, {}) is summary
