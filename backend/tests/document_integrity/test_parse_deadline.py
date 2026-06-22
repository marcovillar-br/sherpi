"""Testes da guarda de tempo do parser (mitigação de DoS por parsing lento).

A guarda usa SIGALRM (Unix, main thread). Estes testes rodam na main thread do
pytest, então o caminho real é exercitado — não o no-op de fallback.
"""

from __future__ import annotations

import signal
import time

import pytest

from sherpi.contexts.document_integrity.infrastructure.pymupdf_parser import _parse_deadline
from sherpi.shared_kernel.errors import UntrustedDocumentError


def test_deadline_aborts_overrun() -> None:
    """Trabalho que estoura o prazo vira UntrustedDocumentError."""
    with pytest.raises(UntrustedDocumentError, match="excedeu"), _parse_deadline(0.05):
        time.sleep(1.0)


def test_deadline_allows_fast_work() -> None:
    """Trabalho dentro do prazo não é interrompido."""
    with _parse_deadline(1.0):
        time.sleep(0.01)


def test_deadline_disabled_is_noop() -> None:
    """`seconds <= 0` desativa a guarda (default de testes/evals)."""
    with _parse_deadline(0.0):
        time.sleep(0.05)


def test_deadline_restores_previous_handler() -> None:
    """O handler/itimer anteriores são restaurados ao sair do contexto."""
    before = signal.getsignal(signal.SIGALRM)
    with _parse_deadline(1.0):
        pass
    assert signal.getsignal(signal.SIGALRM) is before
    # Nenhum alarme remanescente armado.
    assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)
