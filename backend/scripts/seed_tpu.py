"""Popula o índice TPU no banco (idempotente).

Fonte do catálogo (--source):
  synthetic  semente sintética de 30 entradas (padrão; usada por CI/eval)
  cnj        TUA real do CNJ (cível+trabalhista) — ver ADR-0016; requer o catálogo
             gerado antes por `scripts/fetch_tpu_cnj.py`

O embedder é o MESMO da busca (`dependencies._build_suggest_tpu`): build e search precisam
casar em dimensão. Com `uv sync --extra ml` usa JurisBERT; senão Fake (com WARNING).
"""

from __future__ import annotations

import argparse

from sqlmodel import Session, delete
from synthetic.tpu_cnj import DEFAULT_CATALOG, load_cnj_seed
from synthetic.tpu_seed import load_seed

from sherpi.config import get_settings
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.infrastructure.embedding import build_tpu_embedder
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import make_engine
from sherpi.infrastructure.persistence.models import TpuEntryRow


def main() -> None:
    ap = argparse.ArgumentParser(description="Popula o índice TPU.")
    ap.add_argument("--source", choices=("synthetic", "cnj"), default="synthetic")
    ap.add_argument("--catalog", default=DEFAULT_CATALOG, help="catálogo da TUA (--source cnj)")
    args = ap.parse_args()

    entries = load_cnj_seed(args.catalog) if args.source == "cnj" else load_seed()

    cfg = get_settings()
    engine = make_engine(cfg.database_url)
    with Session(engine) as s:
        s.exec(delete(TpuEntryRow))
        s.commit()

    embedder = build_tpu_embedder(cfg.tpu_embedding_model)
    n = BuildTpuIndex(embedder, SqlTpuIndex(engine)).run(entries)
    print(f"Índice TPU populado: {n} entradas ({args.source}) via {type(embedder).__name__}.")


if __name__ == "__main__":
    main()
