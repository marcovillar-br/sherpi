from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import numpy as np

from .tpu import TpuEntry, TpuSuggestion

if TYPE_CHECKING:
    pass


@runtime_checkable
class EmbeddingModel(Protocol):
    """Port de geração de embeddings de texto."""

    def embed(self, texts: list[str]) -> np.ndarray:
        """Retorna matriz (N, D) de embeddings L2-normalizados."""
        ...


@runtime_checkable
class TpuIndex(Protocol):
    """Port do índice k-NN de TPU."""

    def add(self, entry: TpuEntry, embedding: np.ndarray) -> None: ...

    def search(self, query_embedding: np.ndarray, k: int) -> list[TpuSuggestion]: ...

    def count(self) -> int: ...
