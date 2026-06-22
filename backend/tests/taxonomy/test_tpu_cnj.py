"""Testes do loader do catálogo real da TUA/TPU do CNJ (synthetic.tpu_cnj)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from synthetic.tpu_cnj import DEFAULT_CATALOG, load_cnj_seed

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
    {  # par que difere SÓ por espaços/pontuação: ramo plano "Salário / Diferença Salarial"
        "cod_item": 13405,
        "nome": "Diferenças por Desvio de Função",
        "rito": "TRABALHISTA",
        "is_leaf": True,
        "path": "DIREITO DO TRABALHO > Salário / Diferença Salarial > Diferenças por Desvio de Função",
        "glossario": "",
    },
    {  # ...vs cópia sob wrapper "Salário/Diferença Salarial" (sem espaços) — deve deduplicar
        "cod_item": 13922,
        "nome": "Diferenças por Desvio de Função",
        "rito": "TRABALHISTA",
        "is_leaf": True,
        "path": "DIREITO DO TRABALHO > Direito Individual do Trabalho > Salário/Diferença Salarial > Diferenças por Desvio de Função",
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
    # ramo e fora-de-escopo descartados; duplicatas (13968 sob wrapper; 13922 por
    # formatação) são deduplicadas → sobram 13405 (flat) e os demais
    assert codes == {"10441", "9999", "2435", "13405"}


def test_dedupes_pairs_differing_only_by_whitespace_punctuation(catalog_file):
    entries = {e.tpu_code: e for e in load_cnj_seed(catalog_file)}
    # "Salário / Diferença Salarial" (plano, 13405) e "Salário/Diferença Salarial"
    # (sob wrapper, 13922) são o MESMO assunto → uma só entrada (a plana vence).
    assert "13405" in entries and "13922" not in entries


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


def test_real_catalog_leaf_count_within_expected_band():
    """Guarda de regressão sobre o catálogo real da TUA (data/cnj/tpu_assuntos.json).

    O número de folhas pós-dedup é calculado em runtime (não fica gravado no código),
    então uma quebra silenciosa no escopo/dedup passaria despercebida: se o dedup
    parar de colapsar a hierarquia paralela trabalhista, salta para ~1326; se o filtro
    de escopo vazar, dispara. Baseline documentado no ADR-0016: **1007 folhas**
    (de 1326 brutas / 1569 nós). A banda 950-1100 tolera re-sync da TUA pelo CNJ mas
    pega regressão real. Se a TUA mudar de fato, ajuste a banda *e* o ADR-0016 juntos.

    Pulado quando o catálogo não foi baixado (ex.: ambiente sem `make tpu-catalog`).
    """
    catalog = Path(DEFAULT_CATALOG)
    if not catalog.exists():
        pytest.skip(f"catálogo da TUA ausente ({DEFAULT_CATALOG}); rode `make tpu-catalog`")
    n = len(load_cnj_seed(catalog))
    assert 950 <= n <= 1100, (
        f"folhas pós-dedup = {n}, fora da banda 950-1100 (baseline ADR-0016: 1007). "
        "Escopo/dedup pode ter regredido — ou a TUA do CNJ mudou (ajuste a banda e o ADR)."
    )
