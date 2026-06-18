"""Ports transversais (hexagonal) usados por mais de um bounded context.

Ports são interfaces definidas pelo núcleo; os adapters concretos vivem em
`infrastructure/`. É o que torna o SHERPI agnóstico a LLM, a storage e a
estratégia de anonimização: trocar de tecnologia = trocar um adapter.
"""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


class ChatMessage(BaseModel):
    """Mensagem de uma conversa com o LLM (papel + conteúdo)."""

    role: str  # "system" | "user" | "assistant"
    content: str


@runtime_checkable
class LLMProvider(Protocol):
    """Port agnóstico de LLM.

    O adapter default é Gemini Flash; Maritaca Sabiá/OpenAI/Ollama são adapters
    alternativos; `FakeProvider` é usado em testes (sem rede). Implementações
    DEVEM forçar saída estruturada validada contra `response_schema` e aplicar
    timeout/retry (ver resiliência no plano).
    """

    async def complete(
        self,
        messages: list[ChatMessage],
        response_schema: type[TModel],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> TModel:
        """Retorna uma instância validada de `response_schema`."""
        ...


@runtime_checkable
class BlobStorage(Protocol):
    """Port de armazenamento de blobs (PDFs originais).

    Adapter LocalFS no MVP; S3/MinIO na Fase 4. A chave é o hash de conteúdo
    (deduplicação/idempotência).
    """

    def put(self, content: bytes, *, content_hash: str) -> str:
        """Persiste o blob e retorna sua chave/URI."""
        ...

    def get(self, key: str) -> bytes:
        """Recupera o blob pela chave."""
        ...


@runtime_checkable
class Anonymizer(Protocol):
    """Port de anonimização de PII antes de enviar texto a um LLM externo.

    Mascara CPF/CNPJ/nomes/endereços para conformidade com a LGPD quando o
    provedor é externo (ex.: Gemini). No-op quando o provedor é local/on-prem.
    """

    def anonymize(self, text: str) -> str:
        """Retorna o texto com PII mascarada."""
        ...
