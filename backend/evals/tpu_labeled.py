"""Eval rotulado da TPU: acurácia top-1/3/5 sobre a TUA real do CNJ (ADR-0016, item 5).

Mede se a classe correta aparece entre as sugestões para um conjunto curado de cenários
(petição → assunto esperado). Diferente do `eval_tpu` "over seed" do harness principal,
este avalia sobre o **catálogo real** com **JurisBERT** e é honesto sobre acurácia.

Por que medir por ÁREA DE ASSUNTO (marcador no caminho), não por código exato: a TUA é
hiper-granular e tem hierarquias paralelas (ex.: "Horas Extras" ocorre em ~28 folhas).
Exigir o cod_item exato seria arbitrário; o que importa é se a sugestão cai na área certa.
Um acerto@k = algum dos top-k tem o marcador esperado no seu caminho hierárquico.

Requer o catálogo (`scripts/fetch_tpu_cnj.py`) e o extra `ml` (JurisBERT). Sem eles, PULA
com mensagem — não é gate de CI (segue o padrão da extração no harness principal).

Uso:  PYTHONPATH=. uv run --extra ml python -m evals.tpu_labeled
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import StaticPool, create_engine
from synthetic.tpu_cnj import DEFAULT_CATALOG, load_cnj_seed

from sherpi.config import get_settings
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.application.suggest_tpu import SuggestTpu
from sherpi.contexts.taxonomy.infrastructure.embedding import build_tpu_embedder
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.shared_kernel.value_objects import Rito

_LABELED_SET = Path(__file__).parent / "tpu_labeled_set.json"
_TOP_K = 5


def _load_paths(catalog_path: str | Path) -> dict[str, str]:
    """code(str) -> caminho hierárquico, para checar a área de assunto da sugestão."""
    data = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    return {str(e["cod_item"]): e["path"] for e in data if e.get("is_leaf")}


def run(catalog_path: str | Path = DEFAULT_CATALOG) -> int:
    if not Path(catalog_path).exists():
        print("  (pulado — catálogo da TUA ausente: rode `make tpu-catalog`)")
        return 0

    _settings = get_settings()
    embedder = build_tpu_embedder(_settings.tpu_embedding_model, prefer=_settings.tpu_embedder)
    if type(embedder).__name__ == "FakeEmbeddingModel":
        print("  (pulado — JurisBERT indisponível; rode com `uv run --extra ml`)")
        return 0

    paths = _load_paths(catalog_path)
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    index = SqlTpuIndex(engine)
    BuildTpuIndex(embedder, index).run(load_cnj_seed(catalog_path))
    suggest = SuggestTpu(embedder, index, top_k=_TOP_K)

    cases = json.loads(_LABELED_SET.read_text(encoding="utf-8"))
    hits = {1: 0, 3: 0, 5: 0}
    for c in cases:
        marker = c["expect"].lower()
        results = suggest.run(c["query"], rito=Rito(c["rito"]))
        ranks = [i for i, s in enumerate(results, 1) if marker in paths.get(s.tpu_code, "").lower()]
        rank = ranks[0] if ranks else None
        for k in hits:
            if rank is not None and rank <= k:
                hits[k] += 1
        status = f"#{rank}" if rank else "—"
        print(f"    {'✓' if rank and rank <= 3 else '✗'} [{c['name']}] {c['expect']} → {status}")

    n = len(cases)
    print(f"  top-1={hits[1] / n:.3f}  top-3={hits[3] / n:.3f}  top-5={hits[5] / n:.3f}  (n={n})")
    return 0


if __name__ == "__main__":
    print("== TPU rotulado (TUA real do CNJ + JurisBERT) ==")
    raise SystemExit(run())
