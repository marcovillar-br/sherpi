"""Configuração central do SHERPI (pydantic-settings).

Carrega de variáveis de ambiente / `.env`. Falha rápido se faltar configuração
obrigatória. Segredos NUNCA têm default em código — apenas `.env.example`
documenta as chaves.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMBackend = Literal["gemini", "grok", "anthropic", "fake"]
TpuEmbedder = Literal["auto", "jurisbert", "fake"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SHERPI_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # --- Ambiente ---
    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"

    # --- LLM (port + adapter) ---
    llm_backend: LLMBackend = "gemini"
    llm_model: str = "gemini-2.5-flash"
    llm_api_key: str | None = None
    llm_base_url: str | None = None  # sobrescreve o endpoint (grok/anthropic têm default)
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    # Circuit breaker: nº de falhas consecutivas que abre o circuito e cooldown (s)
    # durante o qual as chamadas falham rápido antes de uma tentativa de teste.
    llm_circuit_breaker_threshold: int = 5
    llm_circuit_breaker_reset_seconds: float = 30.0
    # Guarda de custo: corta requisições acima deste nº estimado de tokens de entrada.
    llm_max_input_tokens: int = 200_000
    # Temperatura da geração; 0.0 = determinístico (recomendado p/ extração jurídica).
    llm_temperature: float = 0.0

    # --- Anonimização (LGPD) ---
    anonymize_before_llm: bool = True
    # Mascarar nomes das partes (regex por âncora, sem NER): pega o nome na
    # qualificação (antes de "brasileiro/pessoa jurídica/CPF" ou após "em face de").
    # Best-effort e O(n); NER (Presidio) continua a opção robusta da Fase 4.
    anonymize_names: bool = True

    # --- Firewall (Document Integrity) ---
    max_upload_mb: int = 25
    max_pdf_pages: int = 300
    pdf_parse_timeout_seconds: float = 15.0

    # --- Persistência ---
    database_url: str = "postgresql+psycopg://sherpi:sherpi@localhost:5432/sherpi"
    blob_storage_dir: str = "./data/uploads"

    # --- Taxonomia (TPU) ---
    tpu_embedding_model: str = "juridics/jurisbert-base-portuguese-sts"
    tpu_top_k: int = 3
    # Embedder da TPU (escolha explícita, evita "fake silencioso"):
    #   jurisbert  semântico (requer extra `ml`); falha alto se indisponível
    #   fake       hash, NÃO-semântico (dev/CI sem ML)
    #   auto       tenta JurisBERT, cai no fake com WARNING
    tpu_embedder: TpuEmbedder = "auto"
    # Confiança mínima da sugestão de TPU; abaixo dela a sugestão é descartada (lista
    # vazia → "nenhuma classe próxima" na UI). Calibrado: top-1 legítimo ≥ 0.77 no eval.
    tpu_min_confidence: float = 0.65

    # --- Auth ---
    jwt_secret: str = Field(default="change-me-in-dev-only")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15
    # Usuário único semeado (perfil único). Hash gerado no bootstrap.
    seed_user_email: str = "gabinete@sherpi.local"
    seed_user_password: str | None = None

    # --- Observabilidade ---
    sentry_dsn: str | None = None  # None = Sentry desabilitado

    # --- Retenção (LGPD — direito ao esquecimento) ---
    retention_days: int = 90  # análises mais antigas são elegíveis para exclusão

    # --- Ingestão judicial ---
    ingest_max_pages: int = 300
    ingest_batch_limit: int = 50

    # --- CORS (frontend Next.js) ---
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_external_llm(self) -> bool:
        """True quando o LLM é um serviço externo (exige anonimização de PII)."""
        return self.llm_backend in ("gemini", "grok", "anthropic")

    @property
    def cookie_secure(self) -> bool:
        """Flag `Secure` do cookie de sessão: ativa em produção.

        dev e test rodam local em HTTP (onde um cookie `Secure` não seria
        enviado pelo navegador); só prod serve em HTTPS, e é lá que a flag
        protege o token contra vazamento em canal não cifrado.
        """
        return self.env == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
