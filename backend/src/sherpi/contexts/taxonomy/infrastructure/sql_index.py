from __future__ import annotations

import numpy as np
from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.taxonomy.domain.tpu import TpuEntry, TpuSuggestion
from sherpi.infrastructure.persistence.models import TpuEntryRow


class SqlTpuIndex:
    """Índice k-NN em Python/numpy; embeddings guardados como bytes em SQLite/Postgres."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add(self, entry: TpuEntry, embedding: np.ndarray) -> None:
        vec = embedding.astype(np.float32)
        row = TpuEntryRow(
            id=entry.id,
            tpu_code=entry.tpu_code,
            description=entry.description,
            rito=str(entry.rito),
            text_excerpt=entry.text_excerpt,
            embedding=vec.tobytes(),
            embedding_dim=len(vec),
        )
        with Session(self._engine) as s:
            s.add(row)
            s.commit()

    def search(self, query_embedding: np.ndarray, k: int) -> list[TpuSuggestion]:
        with Session(self._engine) as s:
            rows = list(s.exec(select(TpuEntryRow)).all())
        if not rows:
            return []
        matrix = np.stack(
            [np.frombuffer(r.embedding, dtype=np.float32).reshape(r.embedding_dim) for r in rows]
        )
        q = query_embedding.astype(np.float32)
        scores: np.ndarray = matrix @ q
        top_k = min(k, len(rows))
        idxs: list[int] = list(np.argsort(scores)[::-1][:top_k])
        return [
            TpuSuggestion(
                tpu_code=rows[i].tpu_code,
                description=rows[i].description,
                confidence=float(scores[i]),
                anchor_excerpt=rows[i].text_excerpt[:200],
            )
            for i in idxs
        ]

    def count(self) -> int:
        with Session(self._engine) as s:
            return len(list(s.exec(select(TpuEntryRow)).all()))
