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

# Segmentos "wrapper" que RE-ANINHAM o ramo trabalhista (TUA tem a árvore plana E uma cópia
# sob estes nós). Removê-los do caminho (a) encurta paths longos demais que dominavam o
# ranking por mero volume de tokens, e (b) colapsa as duplicatas para deduplicação.
_WRAPPER_SEGMENTS = frozenset({"Direito Individual do Trabalho", "Direito Coletivo do Trabalho"})


def _canonical_leaf_path(path: str) -> str:
    """Caminho sem o ramo de topo ("DIREITO X >") e sem os segmentos wrapper."""
    segs = path.split(" > ")[1:]  # tira o ramo de topo
    segs = [s for s in segs if s not in _WRAPPER_SEGMENTS]
    return " > ".join(segs)


def _embedding_text(leaf_path: str, nome: str, glossario: str) -> str:
    """Caminho canônico SEMPRE + glossário oficial quando houver.

    Combinar (em vez de escolher um ou outro) é melhor que ambas as variantes isoladas:
    o caminho carrega os tokens discriminativos do assunto (ex.: "Rescisão Indireta",
    "Bancários > Empréstimo consignado") e o glossário acrescenta a semântica do mérito.
    Glossário sozinho falha quando é um one-liner fraco (embeda pior que o próprio path);
    path sozinho falha quando assuntos irmãos compartilham o caminho (precisa da descrição).
    """
    base = leaf_path or nome
    gloss = (glossario or "").strip()
    return f"{base}. {gloss}" if len(gloss) >= _MIN_GLOSS else base


def _is_better(cand: dict, cur: dict) -> bool:
    """Ao deduplicar assuntos idênticos (mesmo caminho canônico), escolhe o melhor:
    glossário vence sem-glossário; depois caminho original mais curto (versão plana,
    não a aninhada sob wrapper); por fim menor cod_item (determinístico)."""
    ck = (len((cand.get("glossario") or "")) >= _MIN_GLOSS, -len(cand["path"]), -cand["cod_item"])
    rk = (len((cur.get("glossario") or "")) >= _MIN_GLOSS, -len(cur["path"]), -cur["cod_item"])
    return ck > rk


def load_cnj_seed(path: str | Path = DEFAULT_CATALOG) -> list[TpuEntry]:
    """Lê o catálogo da TUA e retorna as folhas cível/trabalhista como `TpuEntry`.

    Deduplica assuntos que aparecem em dois caminhos (árvore plana + cópia sob os wrappers
    "Direito Individual/Coletivo do Trabalho"): mantém um por caminho canônico.
    """
    catalog_path = Path(path)
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Catálogo da TUA não encontrado em {catalog_path}. "
            "Rode antes: PYTHONPATH=. uv run python scripts/fetch_tpu_cnj.py"
        )
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    chosen: dict[tuple[str, str], dict] = {}
    for e in data:
        if not e.get("is_leaf") or e.get("rito") not in ("CIVEL", "TRABALHISTA"):
            continue
        key = (e["rito"], _canonical_leaf_path(e["path"]))
        if key not in chosen or _is_better(e, chosen[key]):
            chosen[key] = e
    return [
        TpuEntry(
            id=f"cnj-{e['cod_item']}",
            tpu_code=str(e["cod_item"]),
            description=e["nome"],
            rito=Rito(e["rito"]),
            text_excerpt=_embedding_text(_canonical_leaf_path(e["path"]), e["nome"], e.get("glossario", "")),
        )
        for e in chosen.values()
    ]
