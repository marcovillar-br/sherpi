"""Testes do módulo de logging estruturado."""

from __future__ import annotations

from sherpi.infrastructure.logging import configure_logging, get_logger


def test_configure_logging_does_not_raise() -> None:
    configure_logging(log_level="INFO", json_logs=False)


def test_configure_logging_json_mode() -> None:
    configure_logging(log_level="DEBUG", json_logs=True)
    configure_logging()  # restaura o padrão para não poluir outros testes


def test_get_logger_is_callable() -> None:
    configure_logging()
    log = get_logger("test")
    # Independente do tipo interno (BoundLoggerLazyProxy ou BoundLogger),
    # deve suportar chamadas de log sem lançar exceção.
    assert callable(getattr(log, "info", None))


def test_get_logger_default_name_is_callable() -> None:
    configure_logging()
    log = get_logger()
    assert callable(getattr(log, "info", None))
