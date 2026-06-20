"""Persistência de auditoria das chamadas ao LLM (prompt + resposta).

`PersistingLLMProvider` é um decorator (como o `LoggingLLMProvider`) que grava
cada chamada num `LLMCallRepository`. Diferente do log em stdout (efêmero), isto
é durável e consultável por análise. O conteúdo já chega anonimizado (LGPD).

A gravação é **best-effort**: uma falha de persistência da auditoria NÃO derruba
a análise (a extração é a função primária).
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

import structlog
from pydantic import BaseModel

from sherpi.infrastructure.logging import get_logger
from sherpi.shared_kernel.ports import ChatMessage, LLMProvider, TModel

_log = get_logger("sherpi.llm.audit")


class LLMCall(BaseModel):
    """Registro durável de uma chamada ao LLM."""

    model_config = {"frozen": True}

    id: str
    analysis_id: str | None
    call_type: str
    model: str | None
    prompt: str  # mensagens de entrada (JSON: role + content)
    response: str  # saída estruturada (JSON)
    prompt_chars: int
    response_chars: int
    duration_ms: int
    created_at: datetime


@runtime_checkable
class LLMCallRepository(Protocol):
    def append(self, call: LLMCall) -> None: ...

    def list_by_analysis(self, analysis_id: str) -> list[LLMCall]: ...


class PersistingLLMProvider:
    """Decorator que persiste cada chamada ao LLM (prompt + resposta)."""

    def __init__(
        self, inner: LLMProvider, repository: LLMCallRepository, *, label: str = "llm"
    ) -> None:
        self._inner = inner
        self._repository = repository
        self._label = label

    @property
    def model(self) -> str | None:
        """Delega o nome do modelo (para o LoggingLLMProvider externo)."""
        return getattr(self._inner, "model", None)

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

        prompt = json.dumps(
            [{"role": m.role, "content": m.content} for m in messages], ensure_ascii=False
        )
        response = result.model_dump_json()
        analysis_id = structlog.contextvars.get_contextvars().get("analysis_id")
        call = LLMCall(
            id=uuid.uuid4().hex,
            analysis_id=analysis_id if isinstance(analysis_id, str) else None,
            call_type=self._label,
            model=getattr(self._inner, "model", None),
            prompt=prompt,
            response=response,
            prompt_chars=len(prompt),
            response_chars=len(response),
            duration_ms=elapsed_ms,
            created_at=datetime.now(UTC),
        )
        try:
            self._repository.append(call)
        except Exception as exc:  # auditoria não pode derrubar a análise
            _log.warning("llm.audit.persist_failed", error=str(exc))
        return result
