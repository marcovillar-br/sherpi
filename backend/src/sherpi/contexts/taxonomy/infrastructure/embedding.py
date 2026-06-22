from __future__ import annotations

import hashlib
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


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


def build_tpu_embedder(
    model_name: str = "juridics/jurisbert-base-portuguese-sts",
    *,
    prefer: str = "auto",
) -> JurisbertEmbeddingModel | FakeEmbeddingModel:
    """Embedder da TPU, conforme a escolha explícita `prefer` (`SHERPI_TPU_EMBEDDER`):

    - `"fake"`: `FakeEmbeddingModel` (hash, NÃO-semântico) — dev/CI sem ML.
    - `"jurisbert"`: exige o JurisBERT; se faltar o extra `ml`, **propaga o ImportError**
      (falha alto, em vez de cair no fake e zerar as sugestões em silêncio).
    - `"auto"` (default): tenta JurisBERT e cai no fake com WARNING.

    Use o MESMO embedder no seed e na busca: dimensões diferentes (Fake=64, JurisBERT=768)
    não casam — após trocar, RE-SEMEAR o índice (`scripts/seed_tpu.py`).
    """
    if prefer == "fake":
        return FakeEmbeddingModel()
    if prefer == "jurisbert":
        return JurisbertEmbeddingModel(model_name)  # ImportError sobe → falha explícita
    try:
        return JurisbertEmbeddingModel(model_name)
    except ImportError:
        logger.warning(
            "JurisBERT indisponível (instale `uv sync --extra ml` ou rode com `--extra ml`); "
            "TPU usando FakeEmbeddingModel (hash, NÃO-semântico) — sugestões não confiáveis. "
            "Para falhar alto em vez de degradar, defina SHERPI_TPU_EMBEDDER=jurisbert."
        )
        return FakeEmbeddingModel()
