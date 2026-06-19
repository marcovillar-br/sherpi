from __future__ import annotations

from sherpi.contexts.taxonomy.domain.ports import EmbeddingModel, TpuIndex
from sherpi.contexts.taxonomy.domain.tpu import TpuEntry


class BuildTpuIndex:
    def __init__(self, embedder: EmbeddingModel, index: TpuIndex) -> None:
        self._embedder = embedder
        self._index = index

    def run(self, entries: list[TpuEntry]) -> int:
        if not entries:
            return 0
        texts = [e.text_excerpt for e in entries]
        embeddings = self._embedder.embed(texts)
        for entry, emb in zip(entries, embeddings, strict=True):
            self._index.add(entry, emb)
        return len(entries)
