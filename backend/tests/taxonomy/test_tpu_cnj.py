"""Testes do loader do catálogo real da TUA/TPU do CNJ (synthetic.tpu_cnj)."""

from __future__ import annotations

import json

import pytest
from synthetic.tpu_cnj import load_cnj_seed

from sherpi.shared_kernel.value_objects import Rito

_CATALOG = [
    {  # folha com glossário → texto = "nome. glossário"
        "cod_item": 10441,
        "nome": "Acidente de Trânsito",
        "rito": "CIVEL",
        "is_leaf": True,
        "path": "DIREITO CIVIL > Responsabilidade Civil > Indenização por Dano Material > Acidente de Trânsito",
        "glossario": "Ações de reparação por danos materiais decorrentes de acidente de trânsito.",
    },
    {  # folha SEM glossário → fallback para o caminho sem o ramo de topo
        "cod_item": 9999,
        "nome": "Assunto Sem Glossário",
        "rito": "TRABALHISTA",
        "is_leaf": True,
        "path": "DIREITO DO TRABALHO > Categoria > Assunto Sem Glossário",
        "glossario": "",
    },
    {  # nó-ramo (não folha) → ignorado
        "cod_item": 100,
        "nome": "Responsabilidade Civil",
        "rito": "CIVEL",
        "is_leaf": False,
        "path": "DIREITO CIVIL > Responsabilidade Civil",
        "glossario": "ramo",
    },
    {  # fora de escopo (rito None) → ignorado
        "cod_item": 200,
        "nome": "Algo Penal",
        "rito": None,
        "is_leaf": True,
        "path": "DIREITO PENAL > Algo Penal",
        "glossario": "x",
    },
]


@pytest.fixture
def catalog_file(tmp_path):
    p = tmp_path / "tpu.json"
    p.write_text(json.dumps(_CATALOG, ensure_ascii=False), encoding="utf-8")
    return p


def test_loads_only_leaves_in_scope(catalog_file):
    entries = load_cnj_seed(catalog_file)
    codes = {e.tpu_code for e in entries}
    assert codes == {"10441", "9999"}  # ramo e fora-de-escopo descartados


def test_glossario_becomes_embedding_text(catalog_file):
    e = next(x for x in load_cnj_seed(catalog_file) if x.tpu_code == "10441")
    assert e.text_excerpt.startswith("Acidente de Trânsito. ")
    assert "danos materiais" in e.text_excerpt
    assert e.rito is Rito.CIVEL
    assert e.id == "cnj-10441"


def test_fallback_to_path_without_top_branch(catalog_file):
    e = next(x for x in load_cnj_seed(catalog_file) if x.tpu_code == "9999")
    # sem glossário → caminho sem "DIREITO DO TRABALHO >"
    assert e.text_excerpt == "Categoria > Assunto Sem Glossário"


def test_missing_catalog_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_cnj_seed(tmp_path / "inexistente.json")
