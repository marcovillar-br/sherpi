"""Testes do RegexAnonymizer e do factory de anonimização."""

from __future__ import annotations

from sherpi.config import Settings
from sherpi.infrastructure.anonymization.factory import build_anonymizer
from sherpi.infrastructure.anonymization.regex import (
    MappedRegexAnonymizer,
    NoOpAnonymizer,
    RegexAnonymizer,
)


def test_masks_cpf_cnpj_email_phone_cep() -> None:
    texto = (
        "Autor CPF 529.982.247-25, ré CNPJ 11.222.333/0001-81, "
        "e-mail a@b.com, tel (11) 98765-4321, CEP 01310-100."
    )
    out = RegexAnonymizer().anonymize(texto)
    assert "529.982.247-25" not in out
    assert "11.222.333/0001-81" not in out
    assert "a@b.com" not in out
    assert "[CPF]" in out and "[CNPJ]" in out and "[EMAIL]" in out
    assert "[TELEFONE]" in out and "[CEP]" in out


def test_noop_keeps_text() -> None:
    assert NoOpAnonymizer().anonymize("CPF 529.982.247-25") == "CPF 529.982.247-25"


def test_factory_uses_regex_for_external_llm() -> None:
    # anonymize_names desligado isola o caminho regex-only (estruturado).
    # O default composto (estruturado + nomes) é coberto em test_name_anonymizer.py.
    settings = Settings(llm_backend="gemini", anonymize_before_llm=True, anonymize_names=False)
    assert isinstance(build_anonymizer(settings), MappedRegexAnonymizer)


def test_factory_noop_when_disabled() -> None:
    settings = Settings(llm_backend="gemini", anonymize_before_llm=False)
    assert isinstance(build_anonymizer(settings), NoOpAnonymizer)


def test_factory_noop_for_non_external_backend() -> None:
    # backend 'fake' não é externo → não precisa anonimizar.
    settings = Settings(llm_backend="fake", anonymize_before_llm=True)
    assert isinstance(build_anonymizer(settings), NoOpAnonymizer)
