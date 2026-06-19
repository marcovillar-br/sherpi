"""Gera o corpus de petições sintéticas em disco (data/synthetic/).

Uso:
    uv run python -m synthetic.generate [--out DIR]

Cada PDF vem acompanhado de um manifesto `labels.json` com o *ground truth*
(malicioso? qual vetor? rito? semáforo esperado?), para inspeção humana e
ferramentas externas. O eval harness NÃO lê este arquivo: ele reconstrói o
corpus em memória via `build_corpus()`, que já carrega os mesmos rótulos.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from synthetic.builder import build_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera petições sintéticas rotuladas.")
    parser.add_argument("--out", default="data/synthetic", help="diretório de saída")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    labels: dict[str, dict[str, object]] = {}
    for petition in build_corpus():
        filename = f"{petition.name}.pdf"
        (out / filename).write_bytes(petition.content)
        labels[filename] = {
            "category": petition.category,
            "description": petition.description,
            "is_malicious": petition.is_malicious,
            "expected_verdict": petition.expected_verdict,
            "vector": petition.vector,
            "rito": petition.rito,
            "expect_liminar": petition.expect_liminar,
            "expect_semaforo": petition.expect_semaforo,
            "expect_requer_emenda": petition.expect_requer_emenda,
            "expect_hearing_option": petition.expect_hearing_option,
            "expect_requests_evidence": petition.expect_requests_evidence,
            "expect_cited_docs": petition.expect_cited_docs,
            "expect_subsidiary_claim": petition.expect_subsidiary_claim,
        }

    (out / "labels.json").write_text(json.dumps(labels, indent=2, ensure_ascii=False))
    by_cat: dict[str, int] = {}
    for p in labels.values():
        by_cat[str(p["category"])] = by_cat.get(str(p["category"]), 0) + 1
    print(f"{len(labels)} PDFs + labels.json gerados em {out}/  {by_cat}")


if __name__ == "__main__":
    main()
