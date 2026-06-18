"""Erros de domínio do SHERPI.

Erros de domínio são independentes de transporte (HTTP/SQL). A camada de
interface (`interfaces/api`) é responsável por traduzi-los em respostas HTTP,
sem vazar detalhes internos (ver seção Segurança do plano).
"""

from __future__ import annotations


class SherpiError(Exception):
    """Raiz de todos os erros de domínio do SHERPI."""


class DomainRuleViolationError(SherpiError):
    """Uma invariante de domínio foi violada."""


class InjectionDetectedError(SherpiError):
    """O firewall detectou manipulação que exige interrupção (veredito BLOCK)."""


class UntrustedDocumentError(SherpiError):
    """O documento submetido falhou nas validações de segurança de upload."""


class LLMProviderError(SherpiError):
    """Falha irrecuperável ao chamar o provedor de LLM (após retries)."""


class AuthenticationError(SherpiError):
    """Credenciais inválidas ou sessão não autenticada."""
