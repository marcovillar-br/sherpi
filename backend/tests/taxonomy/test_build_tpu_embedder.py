"""Seleção explícita do embedder da TPU (`build_tpu_embedder` / SHERPI_TPU_EMBEDDER)."""

from __future__ import annotations

import pytest

from sherpi.contexts.taxonomy.infrastructure.embedding import (
    FakeEmbeddingModel,
    build_tpu_embedder,
)


def _ml_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401

        return True
    except ImportError:
        return False


def test_prefer_fake_always_returns_fake():
    assert isinstance(build_tpu_embedder(prefer="fake"), FakeEmbeddingModel)


def test_prefer_jurisbert_fails_loud_without_ml():
    # Sem o extra `ml`, "jurisbert" deve PROPAGAR o ImportError (falha alto), em vez de
    # cair no fake e zerar as sugestões em silêncio.
    if _ml_available():
        pytest.skip("extra ml instalado; este teste cobre o ambiente sem ML")
    with pytest.raises(ImportError):
        build_tpu_embedder(prefer="jurisbert")


def test_prefer_auto_falls_back_to_fake_without_ml():
    if _ml_available():
        pytest.skip("extra ml instalado; auto usaria JurisBERT")
    assert isinstance(build_tpu_embedder(prefer="auto"), FakeEmbeddingModel)
