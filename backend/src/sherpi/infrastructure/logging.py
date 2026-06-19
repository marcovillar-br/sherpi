"""Configuração central de logging estruturado (structlog).

Chamar `configure_logging()` uma vez no startup da aplicação.
`get_logger()` devolve um BoundLogger pronto para uso em qualquer módulo.

Nunca logar PII (CPF, JWT, senhas, conteúdo de PDF).
"""

from __future__ import annotations

import logging

import structlog


def configure_logging(log_level: str = "INFO", *, json_logs: bool = False) -> None:
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    if json_logs:
        processors: list[structlog.types.Processor] = [
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [*shared_processors, structlog.dev.ConsoleRenderer()]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "sherpi") -> structlog.BoundLogger:
    return structlog.get_logger(name)  # type: ignore[no-any-return]
