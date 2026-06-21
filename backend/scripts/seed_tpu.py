"""Popula o índice TPU no banco com os dados da semente sintética (idempotente)."""

from sqlmodel import Session, delete
from synthetic.tpu_seed import load_seed

from sherpi.config import get_settings
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.infrastructure.embedding import build_tpu_embedder
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import make_engine
from sherpi.infrastructure.persistence.models import TpuEntryRow

cfg = get_settings()
engine = make_engine(cfg.database_url)

with Session(engine) as s:
    s.exec(delete(TpuEntryRow))
    s.commit()

# MESMO embedder da busca (dependencies._build_suggest_tpu): build e search precisam
# casar em dimensão. Com `uv sync --extra ml` usa JurisBERT; senão Fake (com WARNING).
embedder = build_tpu_embedder(cfg.tpu_embedding_model)
n = BuildTpuIndex(embedder, SqlTpuIndex(engine)).run(load_seed())
print(f"Índice TPU populado: {n} entradas via {type(embedder).__name__}.")
