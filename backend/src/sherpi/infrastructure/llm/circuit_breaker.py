"""CircuitBreakerLLMProvider — circuit breaker simples sobre um LLMProvider.

Complementa o retry/backoff do adapter (que cobre falhas *transitórias*):
quando o provedor falha de forma *sustentada*, o breaker abre e passa a falhar
rápido, sem martelar a API em pane nem gastar tempo/custo. É um decorator —
não toca no domínio nem no adapter concreto.

Estados:
  - CLOSED: chamadas passam. `failure_threshold` falhas consecutivas abrem o circuito.
  - OPEN: chamadas falham na hora (`CircuitOpenError`) por `reset_timeout` segundos.
  - HALF_OPEN: após o cooldown, UMA chamada de teste é permitida; sucesso fecha o
    circuito, falha reabre.

MVP simples: sem locking (o app é um event loop single-thread; coroutines
concorrentes podem interlaçar, o que apenas torna a contagem aproximada — aceitável).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Literal

from sherpi.shared_kernel.errors import CircuitOpenError
from sherpi.shared_kernel.ports import ChatMessage, LLMProvider, TModel

_State = Literal["closed", "open", "half_open"]


class CircuitBreakerLLMProvider:
    """Decorator que aplica um circuit breaker simples a um `LLMProvider`."""

    def __init__(
        self,
        inner: LLMProvider,
        *,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._inner = inner
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._clock = clock
        self._state: _State = "closed"
        self._failures = 0
        self._opened_at = 0.0

    @property
    def model(self) -> str | None:
        """Delega o nome do modelo do provedor interno (para auditoria/logs)."""
        return getattr(self._inner, "model", None)

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        if self._state == "open":
            if self._clock() - self._opened_at < self._reset_timeout:
                raise CircuitOpenError(
                    "Circuit breaker aberto: provedor de LLM indisponível, tente mais tarde."
                )
            self._state = "half_open"  # cooldown expirou: libera uma tentativa de teste

        try:
            result = await self._inner.complete(
                messages, response_schema, temperature=temperature, max_tokens=max_tokens
            )
        except Exception:
            self._record_failure()
            raise
        self._record_success()
        return result

    def _record_failure(self) -> None:
        self._failures += 1
        # Em half_open, qualquer falha reabre imediatamente; em closed, ao atingir o limite.
        if self._state == "half_open" or self._failures >= self._failure_threshold:
            self._state = "open"
            self._opened_at = self._clock()

    def _record_success(self) -> None:
        self._failures = 0
        self._state = "closed"
