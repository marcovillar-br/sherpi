"""Popula o índice TPU no banco com os dados da semente sintética."""

from synthetic.tpu_seed import load_seed

from sherpi.config import get_settings
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.persistence.engine import make_engine

cfg = get_settings()
engine = make_engine(cfg.database_url)
BuildTpuIndex(FakeEmbeddingModel(), SqlTpuIndex(engine)).run(load_seed())
print("Índice TPU populado.")
