"""Ingestão da Tabela Única de Assuntos (TUA/TPU) do CNJ via webservice SGT.

Protótipo dos passos 1-2 do plano de TPU 1.0 (ver discussão/ADR): baixa a árvore
oficial de assuntos do CNJ, filtra os ramos no escopo do SHERPI (cível, consumidor,
trabalhista, previdenciário) e emite um catálogo JSON com, para cada assunto:

    cod_item, nome, rito, is_leaf, path (cadeia de ancestrais "A > B > C")

O `path` é o insumo do passo 3 (texto de embedding): rótulo seco embeda mal; o caminho
hierárquico dá contexto. Numa fase seguinte, enriquece-se cada assunto de alta frequência
com 1-2 frases descritivas (geração LLM) antes de indexar.

Fonte: SGT/CNJ — webservice SOAP público em https://www.cnj.jus.br/sgt/sgt_ws.php
(WSDL: ?wsdl). Sem dependências novas: urllib + ElementTree (stdlib).

Uso:
    PYTHONPATH=. uv run python scripts/fetch_tpu_cnj.py            # escopo padrão
    PYTHONPATH=. uv run python scripts/fetch_tpu_cnj.py --all      # tabela inteira
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

_WS = "https://www.cnj.jus.br/sgt/sgt_ws.php"
_TIMEOUT = 90

# Ramos de topo da TUA por rito do SHERPI (seq_elemento estável do CNJ).
# Cível abrange civil/consumidor/previdenciário; trabalhista é seu próprio ramo.
_SCOPE: dict[int, tuple[str, str]] = {
    899: ("DIREITO CIVIL", "CIVEL"),
    1156: ("DIREITO DO CONSUMIDOR", "CIVEL"),
    195: ("DIREITO PREVIDENCIÁRIO", "CIVEL"),
    864: ("DIREITO DO TRABALHO", "TRABALHISTA"),
}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _fetch_all_assuntos() -> list[tuple[int, int | None, str]]:
    """Retorna [(cod_item, cod_item_pai|None, nome)] de TODA a tabela de assuntos.

    O `pesquisarItemPublicoWS` (tipoTabela=A) devolve a tabela inteira para qualquer
    termo suficientemente longo (a filtragem textual do WS é ampla); usamos "direito".
    """
    envelope = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"'
        ' xmlns:ns="https://www.cnj.jus.br/sgt/sgt_ws.php"><SOAP-ENV:Body>'
        "<ns:pesquisarItemPublicoWS><tipoTabela>A</tipoTabela>"
        "<tipoPesquisa>D</tipoPesquisa><valorPesquisa>direito</valorPesquisa>"
        "</ns:pesquisarItemPublicoWS></SOAP-ENV:Body></SOAP-ENV:Envelope>"
    )
    req = urllib.request.Request(
        _WS,
        data=envelope.encode("utf-8"),
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f"{_WS}#pesquisarItemPublicoWS",
            "User-Agent": "sherpi-tpu-ingest/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        root = ET.fromstring(resp.read())

    out: list[tuple[int, int | None, str]] = []
    for it in root.iter():
        if _local(it.tag) != "Item":
            continue
        f = {_local(c.tag): (c.text or "") for c in it}
        pai = f.get("cod_item_pai", "").strip()
        out.append((int(f["cod_item"]), int(pai) if pai else None, f.get("nome", "").strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingestão da TUA/TPU do CNJ (SGT).")
    ap.add_argument(
        "--all", action="store_true", help="exporta a tabela inteira, sem filtro de escopo"
    )
    ap.add_argument("--out", default="data/cnj/tpu_assuntos.json", help="arquivo de saída")
    args = ap.parse_args()

    print(f"Baixando TUA do CNJ ({_WS}) …", file=sys.stderr)
    rows = _fetch_all_assuntos()
    name: dict[int, str] = {c: n for c, p, n in rows}
    parent: dict[int, int | None] = {c: p for c, p, n in rows}
    children: dict[int | None, list[int]] = {}
    for c, p, _ in rows:
        children.setdefault(p, []).append(c)
    roots = [c for c in name if parent[c] is None]
    print(f"  {len(rows)} assuntos, {len(roots)} ramos de topo.", file=sys.stderr)

    def top_branch(cod: int) -> int:
        cur = cod
        while parent[cur] is not None:
            cur = parent[cur]  # type: ignore[assignment]
        return cur

    def path_str(cod: int) -> str:
        chain, cur = [], cod
        while cur is not None:
            chain.append(name[cur])
            cur = parent[cur]
        return " > ".join(reversed(chain))

    targets = set(name) if args.all else {c for c in name if top_branch(c) in _SCOPE}
    catalog = []
    for cod in sorted(targets):
        tb = top_branch(cod)
        rito = _SCOPE[tb][1] if tb in _SCOPE else None
        catalog.append(
            {
                "cod_item": cod,
                "nome": name[cod],
                "rito": rito,
                "is_leaf": not children.get(cod),
                "path": path_str(cod),
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    leaves = sum(1 for e in catalog if e["is_leaf"])
    print(f"Catálogo: {len(catalog)} assuntos ({leaves} folhas) → {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
