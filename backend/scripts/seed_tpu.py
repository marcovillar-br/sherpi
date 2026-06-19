"""Popula o índice TPU no banco com os dados da semente sintética (idempotente)."""

from sqlmodel import Session, delete
from synthetic.tpu_seed import load_seed

from sherpi.config import get_settings
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import make_engine
from sherpi.infrastructure.persistence.models import TpuEntryRow

cfg = get_settings()
engine = make_engine(cfg.database_url)

with Session(engine) as s:
    s.exec(delete(TpuEntryRow))
    s.commit()

BuildTpuIndex(FakeEmbeddingModel(), SqlTpuIndex(engine)).run(load_seed())
print("Índice TPU populado.")
