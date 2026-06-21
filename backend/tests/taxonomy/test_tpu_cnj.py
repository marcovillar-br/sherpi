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
    {  # mesmo assunto, ramo PLANO (com glossário) — deve vencer a duplicata
        "cod_item": 2435,
        "nome": "Rescisão Indireta",
        "rito": "TRABALHISTA",
        "is_leaf": True,
        "path": "DIREITO DO TRABALHO > Rescisão do Contrato de Trabalho > Rescisão Indireta",
        "glossario": "Ações com pedido expresso de reconhecimento de rescisão indireta do contrato.",
    },
    {  # mesmo assunto, cópia sob wrapper, SEM glossário — deve ser deduplicada
        "cod_item": 13968,
        "nome": "Rescisão Indireta",
        "rito": "TRABALHISTA",
        "is_leaf": True,
        "path": "DIREITO DO TRABALHO > Direito Individual do Trabalho > Rescisão do Contrato de Trabalho > Rescisão Indireta",
        "glossario": "",
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
    # ramo e fora-de-escopo descartados; a duplicata sob wrapper (13968) é deduplicada
    assert codes == {"10441", "9999", "2435"}


def test_dedupes_parallel_hierarchy_preferring_glossario(catalog_file):
    entries = {e.tpu_code: e for e in load_cnj_seed(catalog_file)}
    # 2435 (plano, com glossário) vence; 13968 (cópia sob wrapper) some
    assert "2435" in entries and "13968" not in entries
    txt = entries["2435"].text_excerpt
    assert "Direito Individual do Trabalho" not in txt  # segmento wrapper removido
    assert txt.startswith("Rescisão do Contrato de Trabalho > Rescisão Indireta")
    assert "rescisão indireta" in txt.lower()  # glossário presente


def test_embedding_text_combines_path_and_glossario(catalog_file):
    e = next(x for x in load_cnj_seed(catalog_file) if x.tpu_code == "10441")
    # caminho (sem o ramo de topo) SEMPRE + glossário oficial ao final
    assert (
        "Responsabilidade Civil > Indenização por Dano Material > Acidente de Trânsito"
        in e.text_excerpt
    )
    assert "DIREITO CIVIL" not in e.text_excerpt  # ramo de topo removido
    assert "danos materiais" in e.text_excerpt  # glossário presente
    assert e.rito is Rito.CIVEL
    assert e.id == "cnj-10441"


def test_fallback_to_path_without_top_branch(catalog_file):
    e = next(x for x in load_cnj_seed(catalog_file) if x.tpu_code == "9999")
    # sem glossário → caminho sem "DIREITO DO TRABALHO >"
    assert e.text_excerpt == "Categoria > Assunto Sem Glossário"


def test_missing_catalog_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_cnj_seed(tmp_path / "inexistente.json")
