from __future__ import annotations

import hashlib
from typing import Any

import numpy as np


class FakeEmbeddingModel:
    """Embeddings determinísticos baseados em hash do texto. Sem ML, sem rede."""

    DIM: int = 64

    def embed(self, texts: list[str]) -> np.ndarray:
        result = []
        for text in texts:
            seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(self.DIM).astype(np.float32)
            vec /= float(np.linalg.norm(vec)) + 1e-8
            result.append(vec)
        return np.stack(result)


class JurisbertEmbeddingModel:
    """Adapter sentence-transformers (JurisBERT). Requer `uv sync --extra ml`."""

    _model: Any

    def __init__(self, model_name: str = "juridics/jurisbert-base-portuguese-sts") -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
        except ImportError as exc:
            raise ImportError(f"Modelo {model_name!r} requer `uv sync --extra ml`.") from exc

    def embed(self, texts: list[str]) -> np.ndarray:
        raw: Any = self._model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        result: np.ndarray = raw.astype(np.float32)
        return result
