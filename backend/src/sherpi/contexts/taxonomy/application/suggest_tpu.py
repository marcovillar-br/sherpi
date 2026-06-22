from __future__ import annotations

from sherpi.contexts.taxonomy.domain.ports import EmbeddingModel, TpuIndex
from sherpi.contexts.taxonomy.domain.tpu import TpuSuggestion
from sherpi.shared_kernel.value_objects import Rito


class SuggestTpu:
    def __init__(
        self,
        embedder: EmbeddingModel,
        index: TpuIndex,
        top_k: int = 3,
        min_confidence: float = 0.0,
    ) -> None:
        self._embedder = embedder
        self._index = index
        self._top_k = top_k
        # Abaixo deste limiar, a sugestão é fraca demais — descartada (lista vazia sinaliza
        # "nenhuma classe próxima" à UI, em vez de empurrar um palpite ruim ao revisor).
        self._min_confidence = min_confidence

    def run(self, text: str, *, rito: Rito = Rito.CIVEL) -> list[TpuSuggestion]:
        if self._index.count() == 0:
            return []
        embedding = self._embedder.embed([text])[0]
        # Passa o texto da query para o ranking híbrido (cosseno + léxico/IDF no índice).
        results = self._index.search(embedding, self._top_k, rito, query_text=text)
        return [s for s in results if s.confidence >= self._min_confidence]
