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

LLMBackend = Literal["gemini", "openai_compat", "fake"]


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
    llm_base_url: str | None = None  # usado por openai_compat (Maritaca/OpenAI/Ollama)
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    # Guarda de custo: corta requisições acima deste nº estimado de tokens de entrada.
    llm_max_input_tokens: int = 200_000
    # Temperatura da geração; 0.0 = determinístico (recomendado p/ extração jurídica).
    llm_temperature: float = 0.0

    # --- Anonimização (LGPD) ---
    anonymize_before_llm: bool = True

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

    # --- CORS (frontend Next.js) ---
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_external_llm(self) -> bool:
        """True quando o LLM é um serviço externo (exige anonimização de PII)."""
        return self.llm_backend in ("gemini", "openai_compat")


@lru_cache
def get_settings() -> Settings:
    return Settings()
