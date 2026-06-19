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
import asyncio
import sys
from dataclasses import dataclass

from sqlalchemy import StaticPool, create_engine
from synthetic.builder import build_clean, build_corpus
from synthetic.tpu_seed import load_seed

from sherpi.config import get_settings
from sherpi.contexts.document_integrity.application.analyze import AnalyzeDocumentIntegrity
from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import PyMuPDFParser
from sherpi.contexts.petition_analysis.application.extract import ExtractPetition
from sherpi.contexts.taxonomy.application.build_index import BuildTpuIndex
from sherpi.contexts.taxonomy.application.suggest_tpu import SuggestTpu
from sherpi.contexts.taxonomy.infrastructure.embedding import FakeEmbeddingModel
from sherpi.contexts.taxonomy.infrastructure.sql_index import SqlTpuIndex
from sherpi.infrastructure.llm.factory import build_llm_provider
from sherpi.infrastructure.persistence.engine import create_all
from sherpi.shared_kernel.errors import LLMProviderError
from sherpi.shared_kernel.ports import LLMProvider
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


async def eval_extraction(provider: LLMProvider) -> float:
    """Acurácia de campo da extração sobre a petição sintética limpa (gold conhecido).

    Não é F1 rigoroso (exige um conjunto anotado maior — Fase 4); é uma medida de
    campo honesta para acompanhar regressões com um LLM real.
    """
    doc = PyMuPDFParser().parse(build_clean(), max_pages=300)
    summary = await ExtractPetition(provider).run(doc.visible_text())
    # Gold da peça sintética limpa (ver synthetic/builder.py).
    checks = {
        "parties>=2": len(summary.parties) >= 2,
        "claim_amount~15.000": bool(summary.claim_amount and "15.000" in summary.claim_amount),
        "no_injunction": summary.has_injunction is False,
        "claims>=1": len(summary.claims) >= 1,
    }
    acertos = sum(1 for ok in checks.values() if ok)
    for nome, ok in checks.items():
        print(f"    {'✓' if ok else '✗'} {nome}")
    return acertos / len(checks)


def eval_tpu() -> tuple[float, float]:
    """Acurácia top-1 e top-3 do índice TPU sobre o próprio seed.

    AVISO: avaliação over seed — os dados de treino e teste são os mesmos.
    O número serve de sanidade (k-NN reproduzível), não de performance real em
    dados não vistos. Expansão com conjunto de teste próprio fica para a Fase 4.
    """
    entries = load_seed()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_all(engine)
    embedder = FakeEmbeddingModel()
    index = SqlTpuIndex(engine)
    BuildTpuIndex(embedder, index).run(entries)
    suggest = SuggestTpu(embedder, index, top_k=3)

    top1_hits = top3_hits = 0
    for entry in entries:
        suggestions = suggest.run(entry.text_excerpt)
        codes = [s.tpu_code for s in suggestions]
        if codes and codes[0] == entry.tpu_code:
            top1_hits += 1
        if entry.tpu_code in codes:
            top3_hits += 1

    n = len(entries)
    return top1_hits / n, top3_hits / n


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval harness do SHERPI.")
    parser.add_argument("--ci", action="store_true", help="sai com código != 0 se abaixo do limiar")
    args = parser.parse_args()

    fw = eval_firewall()
    print("== Firewall (document_integrity) ==")
    print(f"  precision={fw.precision:.3f}  recall={fw.recall:.3f}  f1={fw.f1:.3f}")
    print(f"  tp={fw.tp} fp={fw.fp} fn={fw.fn} tn={fw.tn}")
    print(
        f"  limiar: precision>={MIN_PRECISION} recall>={MIN_RECALL} -> "
        f"{'OK' if fw.passed() else 'FALHOU'}"
    )

    # Extração: requer LLM real (rede). Sem chave/backend externo, é pulada — por
    # isso NÃO faz parte do gate de CI (que valida só o firewall determinístico).
    print("\n== Extração (petition_analysis) ==")
    try:
        provider = build_llm_provider(get_settings())
    except LLMProviderError as exc:
        print(f"  (pulada — sem LLM configurado: {exc})")
    else:
        acc = asyncio.run(eval_extraction(provider))
        print(f"  acurácia de campo = {acc:.3f}")

    top1, top3 = eval_tpu()
    print("\n== TPU (taxonomy) ==")
    print(f"  top-1 accuracy = {top1:.3f}  top-3 accuracy = {top3:.3f}")
    print("  (avaliação over seed — sanidade, não performance em dados não vistos)")

    if args.ci and not fw.passed():
        print("\nEval gate: FALHOU — métrica abaixo do limiar.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
