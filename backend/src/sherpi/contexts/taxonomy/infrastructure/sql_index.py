from __future__ import annotations

import logging
import math
import re
import unicodedata
from collections import Counter

import numpy as np
from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.taxonomy.domain.tpu import TpuEntry, TpuSuggestion
from sherpi.infrastructure.persistence.models import TpuEntryRow
from sherpi.shared_kernel.value_objects import Rito

logger = logging.getLogger(__name__)

# Peso do sinal LÉXICO no ranking híbrido (denso + esparso). O cosseno (JurisBERT) erra
# quando o assunto certo tem o termo distintivo (ex.: "consignado", "indireta") mas perde
# para vizinhos semânticos; o léxico ponderado por IDF resgata o match do termo raro.
_LEXICAL_WEIGHT = 0.5
# Conectivos/preposições que não distinguem assunto (além do corte por tamanho < 4).
_STOPWORDS = frozenset(
    {"para", "pelo", "pela", "como", "sobre", "este", "esta", "esse", "essa", "aos", "que"}
)


def _terms(text: str) -> set[str]:
    """Termos significativos (minúsculo, sem acento, ≥4 chars, sem conectivos)."""
    norm = unicodedata.normalize("NFKD", text.lower())
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]+", norm) if len(w) >= 4 and w not in _STOPWORDS}


def _lexical_scores(query_text: str, docs: list[str]) -> np.ndarray:
    """Sobreposição de termos entre query e doc, ponderada por IDF (termo raro pesa +), ∈ [0,1].

    IDF calculado sobre o conjunto candidato; cada doc recebe a fração do "peso de
    informação" da query (soma de IDF dos termos) que ele cobre."""
    qterms = _terms(query_text)
    if not qterms:
        return np.zeros(len(docs), dtype=np.float32)
    doc_terms = [_terms(d) for d in docs]
    df: Counter[str] = Counter()
    for dt in doc_terms:
        df.update(dt)
    n = len(docs)
    idf = {t: math.log(1 + n / c) for t, c in df.items()}
    q_weight = sum(idf.get(t, 0.0) for t in qterms) or 1.0
    return np.array(
        [sum(idf.get(t, 0.0) for t in (qterms & dt)) / q_weight for dt in doc_terms],
        dtype=np.float32,
    )


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
        self,
        query_embedding: np.ndarray,
        k: int,
        rito: Rito | None = None,
        *,
        query_text: str | None = None,
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
        if matrix.shape[1] != q.shape[0]:
            # Índice e query em dimensões diferentes → embedders distintos no seed e na
            # busca (ex.: trocou para JurisBERT sem re-semear). Não casa; re-semeie.
            logger.warning(
                "Dimensão do índice TPU (%d) ≠ da query (%d) — re-semeie o índice com o "
                "mesmo embedder (scripts/seed_tpu.py).",
                matrix.shape[1],
                q.shape[0],
            )
            return []
        cosine: np.ndarray = matrix @ q
        # Ranking HÍBRIDO: cosseno + peso·léxico(IDF). O léxico resgata o assunto cujo termo
        # distintivo aparece na query mas perde no cosseno puro. confidence = score híbrido.
        if query_text:
            lex = _lexical_scores(query_text, [r.text_excerpt for r in rows])
            ranking = cosine + _LEXICAL_WEIGHT * lex
        else:
            ranking = cosine
        # Top-k por CÓDIGO distinto: o índice tem várias entradas por tpu_code (âncoras
        # diferentes do mesmo assunto); sem dedupe, o mesmo código repetiria no top-k.
        # Mantém a entrada de maior score de cada código, na ordem do ranking.
        idxs: list[int] = []
        seen: set[str] = set()
        for i in (int(j) for j in np.argsort(ranking)[::-1]):
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
                confidence=float(min(1.0, ranking[i])),
                anchor_excerpt=rows[i].text_excerpt,
            )
            for i in idxs
        ]

    def count(self) -> int:
        with Session(self._engine) as s:
            return len(list(s.exec(select(TpuEntryRow)).all()))

    def embedding_dim(self) -> int | None:
        """Dimensão dos vetores indexados (de uma linha qualquer); None se vazio.

        Usado para validar, no startup, que o embedder da busca casa com o índice —
        caso contrário a busca zeraria silenciosamente (Fake=64 vs JurisBERT=768)."""
        with Session(self._engine) as s:
            row = s.exec(select(TpuEntryRow)).first()
        return int(row.embedding_dim) if row else None
