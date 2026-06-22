from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine

from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.application.suggest_tpu import SuggestTpu
from sherpi.contexts.taxonomy.domain.tpu import TpuEntry
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.shared_kernel.value_objects import Rito

_CIVEL_ENTRIES = [
    TpuEntry(
        id="c1",
        tpu_code="1116",
        description="Indenização por Dano Moral",
        rito=Rito.CIVEL,
        text_excerpt="inscrição indevida no SPC causou constrangimento e abalo moral ao consumidor",
    ),
    TpuEntry(
        id="c2",
        tpu_code="11176",
        description="Cobrança",
        rito=Rito.CIVEL,
        text_excerpt="débito de contrato de prestação de serviços não pago após notificação extrajudicial",
    ),
    TpuEntry(
        id="c3",
        tpu_code="10398",
        description="Rescisão do Contrato",
        rito=Rito.CIVEL,
        text_excerpt="rescisão de contrato de compra e venda por inadimplemento da construtora",
    ),
    TpuEntry(
        id="t1",
        tpu_code="9583",
        description="Verbas Rescisórias",
        rito=Rito.TRABALHISTA,
        text_excerpt="verbas rescisórias não quitadas aviso prévio indenizado FGTS décimo terceiro férias",
    ),
]


@pytest.fixture
def populated_index():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(eng)
    embedder = FakeEmbeddingModel()
    idx = SqlTpuIndex(eng)
    BuildTpuIndex(embedder, idx).run(_CIVEL_ENTRIES)
    return embedder, idx


def test_empty_index_returns_empty(populated_index):
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(eng)
    embedder = FakeEmbeddingModel()
    empty_idx = SqlTpuIndex(eng)
    suggest = SuggestTpu(embedder, empty_idx, top_k=3)
    assert suggest.run("qualquer texto") == []


def test_returns_up_to_top_k(populated_index):
    embedder, idx = populated_index
    suggest = SuggestTpu(embedder, idx, top_k=3)
    results = suggest.run("texto qualquer sobre processo civil")
    assert len(results) <= 3


def test_suggestion_fields_populated(populated_index):
    embedder, idx = populated_index
    suggest = SuggestTpu(embedder, idx, top_k=1)
    results = suggest.run("inscrição indevida SPC dano moral consumidor")
    assert len(results) == 1
    s = results[0]
    assert s.tpu_code
    assert s.description
    assert 0.0 <= s.confidence <= 1.0
    assert s.anchor_excerpt


def test_confidence_ordered_descending(populated_index):
    embedder, idx = populated_index
    suggest = SuggestTpu(embedder, idx, top_k=4)
    results = suggest.run("débito cobrança contrato prestação de serviços")
    confidences = [r.confidence for r in results]
    assert confidences == sorted(confidences, reverse=True)


def test_own_text_returns_highest_confidence(populated_index):
    embedder, idx = populated_index
    target = _CIVEL_ENTRIES[0]
    suggest = SuggestTpu(embedder, idx, top_k=4)
    results = suggest.run(target.text_excerpt)
    assert results[0].tpu_code == target.tpu_code


def test_build_tpu_embedder_falls_back_to_fake_without_ml():
    # Sem o extra `ml` (caso da CI/dev), a factory cai no FakeEmbeddingModel — nunca
    # quebra o import; o WARNING avisa que as sugestões não são semânticas.
    from sherpi.contexts.taxonomy.infrastructure.embedding import build_tpu_embedder

    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        assert isinstance(build_tpu_embedder(), FakeEmbeddingModel)


def test_search_returns_empty_on_dimension_mismatch(populated_index):
    # Índice em DIM=64 (Fake) consultado com query de outra dimensão → não casa, não
    # quebra: retorna [] (sinaliza re-seed necessário).
    import numpy as np

    _, idx = populated_index
    bad_query = np.ones(768, dtype=np.float32)
    assert idx.search(bad_query, k=3, rito=Rito.CIVEL) == []


def test_dedupes_repeated_tpu_code_in_top_k():
    # O índice tem 2 entradas (âncoras distintas) do MESMO código: o top-k não deve
    # repetir o código — uma sugestão por código, a de maior confiança.
    from sqlalchemy import StaticPool, create_engine

    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(eng)
    embedder = FakeEmbeddingModel()
    idx = SqlTpuIndex(eng)
    BuildTpuIndex(embedder, idx).run(
        [
            TpuEntry(
                id="a1",
                tpu_code="10674",
                description="Obrigação de Fazer",
                rito=Rito.CIVEL,
                text_excerpt="obrigação de fazer concluir obras de reforma",
            ),
            TpuEntry(
                id="a2",
                tpu_code="10674",
                description="Obrigação de Fazer",
                rito=Rito.CIVEL,
                text_excerpt="obrigação de fazer entrega de documentos do veículo",
            ),
            TpuEntry(
                id="b1",
                tpu_code="1116",
                description="Indenização por Dano Moral",
                rito=Rito.CIVEL,
                text_excerpt="dano moral inscrição indevida no SPC",
            ),
        ]
    )
    results = SuggestTpu(embedder, idx, top_k=3).run("obrigação de fazer obras reforma")
    codes = [r.tpu_code for r in results]
    assert len(codes) == len(set(codes)), f"código repetido no top-k: {codes}"


def test_min_confidence_filters_weak_suggestions(populated_index):
    embedder, idx = populated_index
    # limiar acima de qualquer score possível → nada passa → "nenhuma classe próxima"
    suggest = SuggestTpu(embedder, idx, top_k=3, min_confidence=1.01)
    assert suggest.run("texto qualquer") == []


def test_min_confidence_zero_keeps_suggestions(populated_index):
    embedder, idx = populated_index
    suggest = SuggestTpu(embedder, idx, top_k=3, min_confidence=0.0)
    assert len(suggest.run("débito cobrança contrato prestação de serviços")) >= 1
