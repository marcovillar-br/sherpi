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
# Termos de endereçamento/cabeçalho que NÃO fazem parte de um nome: impedem que o
# match guloso "atravesse" o endereçamento (ex.: "...VARA CÍVEL FULANO DE TAL").
_STOPWORDS = (
    # Endereçamento / juízo
    r"EXCELENT[IÍ]SSIMO|SENHOR|SENHORA|DOUTOR|DOUTORA|JUIZ|JU[IÍ]ZA|DIREITO|VARA"
    r"|C[IÍ]VEL|COMARCA|FORO|TRIBUNAL|JUSTI[CÇ]A|TRABALHO|EXMO"
    # Termos de cabeçalho/ação (substantivos jurídicos — não são nomes próprios)
    r"|A[CÇ][AÃ]O|RECLAMA[CÇ][AÃ]O|COBRAN[CÇ]A|INDENIZA[CÇ][AÃ]O|OBRIGA[CÇ][AÃ]O"
    r"|DECLARAT[OÓ]RIA|REPETI[CÇ][AÃ]O|IND[EÉ]BITO|INEXIGIBILIDADE|D[EÉ]BITO"
    r"|RESCIS[AÃ]O|RESOLU[CÇ][AÃ]O|CONTRATUAL|RESTITUI[CÇ][AÃ]O|VALORES|PAGOS"
    r"|DANOS|MORAIS|URG[EÊ]NCIA|TUTELA|PEDIDO|FAZER|CONSUMO|RELA[CÇ][AÃ]O"
    r"|RITO|ORDIN[AÁ]RIO|VERBAS|SUBSIDI[AÁ]RIO|CUMULA[CÇ][AÃ]O|REPARA[CÇ][AÃ]O"
    r"|EXECU[CÇ][AÃ]O|MONIT[OÓ]RIA|DESPEJO"
)
# Token de nome: início de palavra (\b evita começar no meio, ex.: o "Í" de
# "CÍVEL") + maiúscula inicial, exceto se for um stopword.
_TOKEN = r"\b(?!(?:" + _STOPWORDS + r")\b)[A-ZÀ-Ý][A-Za-zÀ-ÿ&.'-]*"
# Sequência de nome próprio: token + conectivos (da/de/dos/e) ou mais tokens.
# `[^\S\n]` = espaço/tab mas NÃO quebra de linha: o nome não cruza fronteira de
# bloco/parágrafo (o visible_text separa blocos por \n). Cap alto p/ nomes longos
# e composições "A e de B" (litisconsórcio dentro de um mesmo nome/run).
_NAME = _TOKEN + r"(?:[^\S\n]+(?:d[aeo]s?|e|&|" + _TOKEN + r")){0,10}"
# Marcador de qualificação (cue) que vem após o(s) nome(s).
_CUE = (
    r"(?:[Bb]rasileir|[Ee]strangeir|[Pp]ortugu|[Pp]ortador"
    r"|[Ii]nscrit[oa][^\S\n]+no[^\S\n]+CPF|[Pp]essoa[^\S\n]+jur|[Pp]essoa[^\S\n]+f[ií]sica)"
)
# Separador entre nomes numa lista (litisconsórcio): vírgula ou " e ".
_NAME_SEP = r"(?:[^\S\n]*,[^\S\n]*|[^\S\n]+e[^\S\n]+)"
# Lista de 1+ nomes (separados por vírgula/"e") terminando num cue, no mesmo bloco.
_NAME_LIST_BEFORE_CUE = re.compile(
    r"(?:" + _NAME + _NAME_SEP + r")*" + _NAME + r"(?=[^\S\n]*,?[^\S\n]*" + _CUE + r")"
)
# Nome(s) DEPOIS de "em face de/da" ou "em desfavor de" (tipicamente o réu).
_NAME_AFTER_PARTY = re.compile(r"((?:[Ee]m face d[ea]|[Ee]m desfavor de)\s+)(" + _NAME + r")")
# Para remascarar cada nome dentro de uma lista, preservando os separadores.
_NAME_SOLO = re.compile(_NAME)


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
        # Lista antes do cue: mascara CADA nome, preservando os separadores
        # (ex.: "A, B e C, brasileiros" → "[NOME], [NOME] e [NOME], brasileiros").
        text = _NAME_LIST_BEFORE_CUE.sub(lambda m: _NAME_SOLO.sub("[NOME]", m.group(0)), text)
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
