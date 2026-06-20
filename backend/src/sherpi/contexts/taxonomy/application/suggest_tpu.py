from __future__ import annotations

from sherpi.contexts.taxonomy.domain.ports import EmbeddingModel, TpuIndex
from sherpi.contexts.taxonomy.domain.tpu import TpuSuggestion
from sherpi.shared_kernel.value_objects import Rito


class SuggestTpu:
    def __init__(self, embedder: EmbeddingModel, index: TpuIndex, top_k: int = 3) -> None:
        self._embedder = embedder
        self._index = index
        self._top_k = top_k

    def run(self, text: str, *, rito: Rito = Rito.CIVEL) -> list[TpuSuggestion]:
        if self._index.count() == 0:
            return []
        embedding = self._embedder.embed([text])[0]
        return self._index.search(embedding, self._top_k, rito)
