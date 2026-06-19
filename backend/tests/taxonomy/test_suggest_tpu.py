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
