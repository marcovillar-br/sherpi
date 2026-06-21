"""Sinal léxico do ranking híbrido da TPU (_lexical_scores) — determinístico, sem ML."""

from __future__ import annotations

from sherpi.contexts.taxonomy.infrastructure.sql_index import _lexical_scores


def test_rewards_doc_with_rare_query_term():
    # O doc com o termo distintivo ("consignado") deve pontuar mais que o genérico.
    docs = [
        "Contratos de Consumo > Bancários > Empréstimo consignado. Débito no salário.",
        "Obrigações > Adimplemento e Extinção > Pagamento com Sub-rogação.",
    ]
    s = _lexical_scores("empréstimo consignado bancário fraudulento", docs)
    assert s[0] > s[1]


def test_distinctive_term_beats_common_overlap():
    # Query com "rescisão indireta": o alvo tem o termo raro "indireta"; o concorrente
    # compartilha só termos comuns ("rescisão", "contrato").
    docs = [
        "Rescisão do Contrato de Trabalho > Rescisão Indireta.",
        "Rescisão do Contrato de Trabalho > Justa Causa / Falta Grave.",
    ]
    s = _lexical_scores("rescisão indireta do contrato de trabalho", docs)
    assert s[0] > s[1]


def test_scores_in_unit_range_and_zero_without_query_terms():
    s = _lexical_scores("rescisão indireta", ["Rescisão Indireta", "Horas Extras"])
    assert float(s.min()) >= 0.0 and float(s.max()) <= 1.0
    # query sem termos significativos (só conectivos/curtos) → tudo zero
    z = _lexical_scores("de e a", ["qualquer", "outro"])
    assert list(z) == [0.0, 0.0]
