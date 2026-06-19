from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine

from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.domain.tpu import TpuEntry
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.shared_kernel.value_objects import Rito


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(eng)
    return eng


@pytest.fixture
def index(engine):
    return SqlTpuIndex(engine)


@pytest.fixture
def embedder():
    return FakeEmbeddingModel()


_ENTRIES = [
    TpuEntry(
        id=f"e{i}",
        tpu_code="1116",
        description="Dano Moral",
        rito=Rito.CIVEL,
        text_excerpt=f"texto da petição cível número {i} sobre indenização por dano moral",
    )
    for i in range(5)
]


def test_build_empty_returns_zero(embedder, index):
    assert BuildTpuIndex(embedder, index).run([]) == 0


def test_build_returns_count(embedder, index):
    n = BuildTpuIndex(embedder, index).run(_ENTRIES)
    assert n == len(_ENTRIES)


def test_index_count_after_build(embedder, index):
    BuildTpuIndex(embedder, index).run(_ENTRIES)
    assert index.count() == len(_ENTRIES)


def test_build_idempotent_entries_have_different_ids(embedder, index):
    entries_a = [_ENTRIES[0]]
    entries_b = [_ENTRIES[1]]
    BuildTpuIndex(embedder, index).run(entries_a)
    BuildTpuIndex(embedder, index).run(entries_b)
    assert index.count() == 2
