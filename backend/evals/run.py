"""Eval harness — executa as avaliações e reporta métricas.

Uso:
    uv run python -m evals.run          # imprime as métricas
    uv run python -m evals.run --ci     # idem, e sai com código != 0 se abaixo do limiar

Hoje cobre o **firewall** (Sprint 1) sobre o corpus sintético rotulado. À medida
que as capacidades evoluem (extração, admissibilidade, TPU), novas avaliações são
adicionadas aqui e ao gate do CI.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from synthetic.builder import build_corpus

from sherpi.contexts.document_integrity.application.analyze import AnalyzeDocumentIntegrity
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.shared_kernel.value_objects import RiskVerdict

# Limiares mínimos para o corpus sintético (ground truth determinístico):
# o firewall deve pegar TODAS as injeções plantadas e não sinalizar a peça limpa.
MIN_PRECISION = 1.0
MIN_RECALL = 1.0


@dataclass
class Metrics:
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    tn: int

    def passed(self) -> bool:
        return self.precision >= MIN_PRECISION and self.recall >= MIN_RECALL


def eval_firewall() -> Metrics:
    """Avalia a detecção de manipulação (malicioso vs. limpo) do firewall."""
    firewall = AnalyzeDocumentIntegrity(PyMuPDFParser())
    tp = fp = fn = tn = 0
    for petition in build_corpus():
        report = firewall.run(petition.content, max_pages=300)
        flagged = report.verdict in (RiskVerdict.BLOCK, RiskVerdict.WARN)
        if petition.is_malicious and flagged:
            tp += 1
        elif petition.is_malicious and not flagged:
            fn += 1
        elif not petition.is_malicious and flagged:
            fp += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return Metrics(precision, recall, f1, tp, fp, fn, tn)


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval harness do SHERPI.")
    parser.add_argument("--ci", action="store_true", help="sai com código != 0 se abaixo do limiar")
    args = parser.parse_args()

    fw = eval_firewall()
    print("== Firewall (document_integrity) ==")
    print(f"  precision={fw.precision:.3f}  recall={fw.recall:.3f}  f1={fw.f1:.3f}")
    print(f"  tp={fw.tp} fp={fw.fp} fn={fw.fn} tn={fw.tn}")
    print(f"  limiar: precision>={MIN_PRECISION} recall>={MIN_RECALL} -> "
          f"{'OK' if fw.passed() else 'FALHOU'}")

    if args.ci and not fw.passed():
        print("\nEval gate: FALHOU — métrica abaixo do limiar.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
