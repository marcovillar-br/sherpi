"""Anonimização de PII por expressões regulares (LGPD).

Mascara identificadores estruturados (CPF, CNPJ, e-mail, telefone, CEP) **antes**
de enviar o texto a um LLM externo. Determinístico e local.

Limitação conhecida (MVP): não anonimiza **nomes** de pessoas (exige NER —
ex.: Presidio/spaCy, previsto para a Fase 4). Por isso a estratégia *synthetic-first*
permanece a principal salvaguarda; este adapter é a defesa estrutural complementar.

Os placeholders são tipados (`[CPF]`, `[CNPJ]`...) para o LLM ainda entender a
estrutura do documento. A validação determinística de CPF/CNPJ roda sobre o texto
ORIGINAL (não anonimizado), então o mascaramento não degrada a admissibilidade.
"""

from __future__ import annotations

import re

# Ordem importa: padrões mais longos/específicos primeiro (CNPJ antes de CPF; CEP por último).
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("[EMAIL]", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("[CNPJ]", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("[CPF]", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("[TELEFONE]", re.compile(r"\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}\b")),
    ("[CEP]", re.compile(r"\b\d{5}-?\d{3}\b")),
)


class RegexAnonymizer:
    """Implementação do port `Anonymizer` baseada em regex."""

    def anonymize(self, text: str) -> str:
        for placeholder, pattern in _PATTERNS:
            text = pattern.sub(placeholder, text)
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
