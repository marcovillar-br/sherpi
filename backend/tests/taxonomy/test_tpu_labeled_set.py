"""Validação estrutural do conjunto rotulado da TPU (evals/tpu_labeled_set.json).

Não roda o eval (precisa de JurisBERT/catálogo) — apenas garante a integridade dos
rótulos: campos presentes, rito válido, sem duplicatas. Guarda contra typos que só
apareceriam ao rodar `make eval-tpu`.
"""

from __future__ import annotations

import json
from pathlib import Path

_SET = Path(__file__).parents[2] / "evals" / "tpu_labeled_set.json"


def _load():
    return json.loads(_SET.read_text(encoding="utf-8"))


def test_labeled_set_is_non_empty():
    assert len(_load()) >= 5


def test_each_case_has_required_fields_and_valid_rito():
    for c in _load():
        assert set(c) >= {"name", "rito", "expect", "query"}, c
        assert c["rito"] in ("CIVEL", "TRABALHISTA"), c
        assert c["query"].strip() and c["expect"].strip() and c["name"].strip()


def test_case_names_are_unique():
    names = [c["name"] for c in _load()]
    assert len(names) == len(set(names))
