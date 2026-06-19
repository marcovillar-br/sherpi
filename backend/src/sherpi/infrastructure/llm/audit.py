"""LoggingLLMProvider — decorator de auditoria para chamadas ao LLM.

Envolve qualquer LLMProvider e registra cada chamada via structlog.
Os contextvars (analysis_id, correlation_id) injetados pelo middleware e
pela rota de análise são automaticamente incluídos em todos os log entries.

O texto que chega aqui já foi anonimizado pelo Anonymizer (LGPD) — é seguro
logar o conteúdo completo.
"""

from __future__ import annotations

import time

from sherpi.infrastructure.logging import get_logger
from sherpi.shared_kernel.ports import ChatMessage, LLMProvider, TModel

_log = get_logger("sherpi.llm")


class LoggingLLMProvider:
    """Decorator sobre LLMProvider que emite logs de auditoria por chamada.

    Nível INFO: metadados (tipo de chamada, modelo, chars, latência).
    Nível DEBUG: conteúdo completo dos messages e da resposta.
    """

    def __init__(self, inner: LLMProvider, *, label: str = "llm") -> None:
        self._inner = inner
        self._label = label

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        t0 = time.monotonic()
        result = await self._inner.complete(
            messages, response_schema, temperature=temperature, max_tokens=max_tokens
        )
        elapsed_ms = round((time.monotonic() - t0) * 1000)

        prompt_chars = sum(len(m.content) for m in messages)
        response_json = result.model_dump_json()

        _log.info(
            "llm.call",
            call_type=self._label,
            model=getattr(self._inner, "model", None),
            prompt_chars=prompt_chars,
            response_chars=len(response_json),
            duration_ms=elapsed_ms,
        )
        _log.debug(
            "llm.call.detail",
            call_type=self._label,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            response=result.model_dump(),
        )
        return result
