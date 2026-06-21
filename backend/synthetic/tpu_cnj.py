"""Carrega o catálogo real da TUA/TPU do CNJ como entradas indexáveis (ADR-0016).

Lê o JSON produzido por `scripts/fetch_tpu_cnj.py` (assuntos cível+trabalhista, com
`nome`, `path`, `glossario`, `rito`, `is_leaf`) e o converte em `TpuEntry` para o índice
k-NN, aplicando a estratégia de **texto de embedding híbrido**:

- quando há **glossário oficial** do CNJ (≈37% das folhas): `"<nome>. <glossário>"` — texto
  rico e discriminativo (descreve o que o assunto abrange);
- caso contrário: o **caminho hierárquico** sem o ramo de topo (ex.: "Responsabilidade
  Civil > Indenização por Dano Material > Acidente de Trânsito") — baseline com contexto.

(O passo seguinte do ADR-0016 enriquece via LLM as folhas de alta frequência sem glossário.)
Indexamos apenas **folhas** (assuntos classificáveis). `tpu_code` = `cod_item` do CNJ.
"""

from __future__ import annotations

import json
from pathlib import Path

from sherpi.contexts.taxonomy.domain.tpu import TpuEntry
from sherpi.shared_kernel.value_objects import Rito

DEFAULT_CATALOG = "data/cnj/tpu_assuntos.json"
_MIN_GLOSS = 15  # glossário curto demais não acrescenta sinal; usa o caminho


def _embedding_text(nome: str, path: str, glossario: str) -> str:
    gloss = (glossario or "").strip()
    if len(gloss) >= _MIN_GLOSS:
        return f"{nome}. {gloss}"
    # fallback: caminho hierárquico sem o ramo de topo ("DIREITO X > ...").
    return " > ".join(path.split(" > ")[1:]) or nome


def load_cnj_seed(path: str | Path = DEFAULT_CATALOG) -> list[TpuEntry]:
    """Lê o catálogo da TUA e retorna as folhas cível/trabalhista como `TpuEntry`."""
    catalog_path = Path(path)
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Catálogo da TUA não encontrado em {catalog_path}. "
            "Rode antes: PYTHONPATH=. uv run python scripts/fetch_tpu_cnj.py"
        )
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries: list[TpuEntry] = []
    for e in data:
        if not e.get("is_leaf") or e.get("rito") not in ("CIVEL", "TRABALHISTA"):
            continue
        entries.append(
            TpuEntry(
                id=f"cnj-{e['cod_item']}",
                tpu_code=str(e["cod_item"]),
                description=e["nome"],
                rito=Rito(e["rito"]),
                text_excerpt=_embedding_text(e["nome"], e["path"], e.get("glossario", "")),
            )
        )
    return entries
