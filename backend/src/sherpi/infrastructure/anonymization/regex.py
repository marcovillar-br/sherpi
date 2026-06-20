"""Anonimização de PII por expressões regulares (LGPD).

Mascara identificadores estruturados (CPF, CNPJ, e-mail, telefone, CEP) **antes**
de enviar o texto a um LLM externo. Determinístico e local.

Nomes das partes são mascarados pelo `RegexNameAnonymizer` (por âncora, best-effort,
sem NER) — ver classe. NER pleno (Presidio/spaCy) continua a opção robusta da Fase 4.
A estratégia *synthetic-first* permanece a principal salvaguarda.

Os placeholders são tipados (`[CPF]`, `[CNPJ]`...) para o LLM ainda entender a
estrutura do documento. A validação determinística de CPF/CNPJ roda sobre o texto
ORIGINAL (não anonimizado), então o mascaramento não degrada a admissibilidade.
"""

from __future__ import annotations

import re

from sherpi.shared_kernel.ports import Anonymizer

# Ordem importa: padrões mais longos/específicos primeiro (CNPJ antes de CPF; CEP por último).
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("[EMAIL]", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("[CNPJ]", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("[CPF]", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("[TELEFONE]", re.compile(r"\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}\b")),
    ("[CEP]", re.compile(r"\b\d{5}-?\d{3}\b")),
)

# --- Mascaramento de nomes por ÂNCORA (LGPD, best-effort, sem NER/dependências) ---
# Sequência de nome próprio: tokens iniciando em maiúscula + conectivos (da/de/dos/e).
_NAME = (
    r"[A-ZÀ-Ý][A-Za-zÀ-ÿ&.'-]*"
    r"(?:\s+(?:d[aeo]s?|e|&|[A-ZÀ-Ý][A-Za-zÀ-ÿ&.'-]*)){0,6}"
)
# Nome ANTES de um marcador de qualificação (pessoa física/jurídica).
_NAME_BEFORE_CUE = re.compile(
    _NAME + r"(?=\s*,?\s*(?:[Bb]rasileir|[Ee]strangeir|[Pp]ortugu|[Pp]ortador"
    r"|[Ii]nscrit[oa]\s+no\s+CPF|[Pp]essoa\s+jur|[Pp]essoa\s+f[ií]sica))"
)
# Nome DEPOIS de "em face de/da" ou "em desfavor de" (tipicamente o réu).
_NAME_AFTER_PARTY = re.compile(r"((?:[Ee]m face d[ea]|[Ee]m desfavor de)\s+)(" + _NAME + r")")


class RegexAnonymizer:
    """Implementação do port `Anonymizer` baseada em regex."""

    def anonymize(self, text: str) -> str:
        for placeholder, pattern in _PATTERNS:
            text = pattern.sub(placeholder, text)
        return text


class RegexNameAnonymizer:
    """Mascara nomes das partes por ÂNCORA — sem NER, O(n), determinístico.

    Pega o nome na qualificação: imediatamente antes de "brasileiro/pessoa
    jurídica/inscrito no CPF…" ou logo após "em face de". É **best-effort**: pode
    não pegar nomes citados livremente nos fatos, e raramente pode mascarar a mais.
    NER (Presidio) continua a opção robusta da Fase 4. Não altera o veredito nem a
    admissibilidade (que usam o texto original).
    """

    def anonymize(self, text: str) -> str:
        text = _NAME_BEFORE_CUE.sub("[NOME]", text)
        text = _NAME_AFTER_PARTY.sub(lambda m: m.group(1) + "[NOME]", text)
        return text


class CompositeAnonymizer:
    """Aplica vários anonimizadores em sequência (ex.: estruturado + nomes)."""

    def __init__(self, anonymizers: list[Anonymizer]) -> None:
        self._anonymizers = anonymizers

    def anonymize(self, text: str) -> str:
        for anonymizer in self._anonymizers:
            text = anonymizer.anonymize(text)
        return text


class NoOpAnonymizer:
    """Não altera o texto (usado quando o LLM é local/on-prem)."""

    def anonymize(self, text: str) -> str:
        return text


class MappedRegexAnonymizer:
    """RegexAnonymizer com mapeamento reversível (LGPD — anonimização rastreável).

    Numera cada ocorrência: [CPF_1], [CPF_2]... permitindo reverter a substituição
    dentro da mesma sessão se necessário (ex.: para exibição ao magistrado autenticado).
    """

    def anonymize(self, text: str) -> str:
        return self.anonymize_mapped(text)[0]

    def anonymize_mapped(self, text: str) -> tuple[str, dict[str, str]]:
        """Retorna (texto_anonimizado, mapeamento placeholder→valor_original)."""
        mapping: dict[str, str] = {}
        counters: dict[str, int] = {}
        result = text
        for placeholder_base, pattern in _PATTERNS:
            base = placeholder_base.strip("[]")
            # reversed para manter offsets válidos ao substituir da direita para a esquerda
            for match in reversed(list(pattern.finditer(result))):
                counters[base] = counters.get(base, 0) + 1
                key = f"[{base}_{counters[base]}]"
                mapping[key] = match.group()
                result = result[: match.start()] + key + result[match.end() :]
        return result, mapping
