from __future__ import annotations

import numpy as np
from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.taxonomy.domain.tpu import TpuEntry, TpuSuggestion
from sherpi.infrastructure.persistence.models import TpuEntryRow
from sherpi.shared_kernel.value_objects import Rito


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

    def search(
        self, query_embedding: np.ndarray, k: int, rito: Rito | None = None
    ) -> list[TpuSuggestion]:
        with Session(self._engine) as s:
            rows = list(s.exec(select(TpuEntryRow)).all())
        if rito is not None:
            rows = [r for r in rows if r.rito == str(rito)]
        if not rows:
            return []
        matrix = np.stack(
            [np.frombuffer(r.embedding, dtype=np.float32).reshape(r.embedding_dim) for r in rows]
        )
        q = query_embedding.astype(np.float32)
        scores: np.ndarray = matrix @ q
        # Top-k por CÓDIGO distinto: o índice tem várias entradas por tpu_code (âncoras
        # diferentes do mesmo assunto); sem dedupe, o mesmo código repetiria no top-k.
        # Mantém a entrada de maior confiança de cada código, na ordem de score.
        idxs: list[int] = []
        seen: set[str] = set()
        for i in (int(j) for j in np.argsort(scores)[::-1]):
            if rows[i].tpu_code in seen:
                continue
            seen.add(rows[i].tpu_code)
            idxs.append(i)
            if len(idxs) == k:
                break
        return [
            TpuSuggestion(
                tpu_code=rows[i].tpu_code,
                description=rows[i].description,
                confidence=float(scores[i]),
                anchor_excerpt=rows[i].text_excerpt,
            )
            for i in idxs
        ]

    def count(self) -> int:
        with Session(self._engine) as s:
            return len(list(s.exec(select(TpuEntryRow)).all()))
