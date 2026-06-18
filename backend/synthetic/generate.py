"""Gera o corpus de petições sintéticas em disco (data/synthetic/).

Uso:
    uv run python -m synthetic.generate [--out DIR]

Cada PDF vem acompanhado de um manifesto `labels.json` com o *ground truth*
(malicioso? qual vetor?), consumido pelo eval harness.
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
        labels[filename] = {"is_malicious": petition.is_malicious, "vector": petition.vector}

    (out / "labels.json").write_text(json.dumps(labels, indent=2, ensure_ascii=False))
    print(f"{len(labels)} PDFs + labels.json gerados em {out}/")


if __name__ == "__main__":
    main()
