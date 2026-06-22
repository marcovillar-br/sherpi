"""Testes do MappedRegexAnonymizer."""

from __future__ import annotations

from sherpi.infrastructure.anonymization.regex import MappedRegexAnonymizer
from sherpi.shared_kernel.ports import Anonymizer


def test_implements_anonymizer_port() -> None:
    assert isinstance(MappedRegexAnonymizer(), Anonymizer)


def test_anonymize_cpf() -> None:
    anon = MappedRegexAnonymizer()
    result, mapping = anon.anonymize_mapped("CPF: 529.982.247-25")
    assert "529.982.247-25" not in result
    assert "[CPF_1]" in result
    assert mapping["[CPF_1]"] == "529.982.247-25"


def test_anonymize_multiple_cpfs_numbered() -> None:
    anon = MappedRegexAnonymizer()
    _, mapping = anon.anonymize_mapped("A: 529.982.247-25 e B: 529.982.247-25")
    # Os dois CPFs são numerados
    assert len([k for k in mapping if k.startswith("[CPF_")]) == 2


def test_anonymize_via_port_method() -> None:
    anon = MappedRegexAnonymizer()
    text = "email: foo@bar.com"
    result = anon.anonymize(text)
    assert "foo@bar.com" not in result
    assert "[EMAIL_1]" in result


def test_no_pii_unchanged() -> None:
    anon = MappedRegexAnonymizer()
    text = "Petição cível sem dados pessoais estruturados."
    result, mapping = anon.anonymize_mapped(text)
    assert result == text
    assert mapping == {}


def test_mixed_types() -> None:
    anon = MappedRegexAnonymizer()
    text = "CPF 529.982.247-25 email foo@bar.com CNPJ 11.222.333/0001-81"
    result, mapping = anon.anonymize_mapped(text)
    assert "529.982.247-25" not in result
    assert "foo@bar.com" not in result
    assert "11.222.333/0001-81" not in result
    assert len(mapping) == 3
