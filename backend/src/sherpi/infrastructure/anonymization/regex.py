"""Anonimização de PII por expressões regulares (LGPD).

Mascara identificadores estruturados (CPF, CNPJ, e-mail, telefone, CEP) e, por âncora
de contexto, identificadores que só são PII pelo rótulo (RG/CNH, conta/agência bancária,
nº de benefício do INSS, nº de B.O.) **antes** de enviar o texto a um LLM externo.
Determinístico e local.

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

# --- Identificadores que só são PII pelo CONTEXTO (rótulo/âncora) ------------------
# RG, conta bancária, nº de benefício do INSS e nº de B.O. não têm forma autossuficiente
# (um "9179" isolado é inócuo; ao lado de "agência", é dado bancário). Por isso cada
# padrão tem DOIS grupos: (1) o rótulo/âncora a PRESERVAR e (2) o valor a mascarar — só
# o grupo 2 é substituído, mantendo a estrutura do documento legível pelo LLM. O `?`
# após os quantificadores de prefixo é preguiçoso: o valor é o PRIMEIRO número após o
# rótulo. Roda DEPOIS de `_PATTERNS` (CPF/CNPJ/etc. já mascarados não colidem).
_ANCHORED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # RG / Carteira de Identidade / CNH (formato livre: "1.234.567", "12.345.678-9").
    (
        "[RG]",
        re.compile(
            r"((?:RG|R\.G\.|C\.?N\.?H\.?|[Cc]arteira de [Ii]dentidade(?:/CNH)?)[^\n\d]{0,25}?)"
            r"(\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX]?)\b"
        ),
    ),
    # Nº de benefício do INSS (NB): forma de CPF, mas com 1 só dígito verificador → o
    # regex de CPF (que exige \d{2} final) não o pega, e ele vazaria sem esta âncora.
    (
        "[BENEFICIO]",
        re.compile(r"(benef[íi]cio[^\n\d]{0,20}?)(\d{3}\.?\d{3}\.?\d{3}[-.]?\d)\b"),
    ),
    # Dados bancários: código do banco, agência e conta.
    ("[BANCO]", re.compile(r"(\bBanco[^\S\n]+)(\d{3,4})\b")),
    ("[AGENCIA]", re.compile(r"([Aa]g[êe]ncia[^\n\d]{0,5}?)(\d{3,5}-?[\dxX]?)\b")),
    ("[CONTA]", re.compile(r"([Cc]onta(?:[^\S\n]+corrente)?[^\n\d]{0,12}?)(\d{3,8}-?[\dxX])\b")),
    # Nº de boletim/registro de ocorrência policial (B.O.).
    (
        "[OCORRENCIA]",
        re.compile(
            r"((?:[Oo]corr[êe]ncia|boletim de ocorr[êe]ncia|B\.?O\.?)[^\n\d]{0,15}?)(\d{4,})\b"
        ),
    ),
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
    # Rótulos de polo processual — nunca são nomes próprios (impede que "em face da
    # PARTE REQUERIDA: Fulano" mascare o rótulo em vez do nome). O nome real ainda é
    # pego pelo anchor de rótulo `_NAME_AFTER_LABEL`.
    r"|PARTE|REQUERENTES?|REQUERID[OA]S?|RECLAMANTES?|RECLAMAD[OA]S?|AUTOR[AES]?"
    r"|R[ÉE]US?|RÉS?|EXEQUENTES?|EXECUTAD[OA]S?|IMPETRANTES?|IMPETRAD[OA]S?"
    r"|EMBARGANTES?|EMBARGAD[OA]S?"
    # UFs — não são nomes próprios. Evitam que o token curto antes de uma deixa de
    # qualificação seja mascarado (ex.: "DF" em "SSP/DF, inscrito no CPF" → [NOME]).
    # Nenhuma colide com sobrenome BR comum ("Sá" é acentuado, não casa com "SA").
    r"|AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO"
)
# Token de nome: início de palavra (\b evita começar no meio, ex.: o "Í" de
# "CÍVEL") + maiúscula inicial, exceto se for um stopword. Exige **2+ caracteres**
# (`+`): um token de 1 letra nunca é nome e gerava falso-positivo (o "A" de "S/A"
# logo antes de "pessoa jurídica" virava [NOME], partindo a razão social).
_TOKEN = r"\b(?!(?:" + _STOPWORDS + r")\b)[A-ZÀ-Ý][A-Za-zÀ-ÿ&.'-]+"
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
# Rótulo de polo processual (cível + trabalhista). É a posição MAIS ancorada de um
# nome na inicial — logo após "REQUERENTE:", "PARTE REQUERIDA :", "AUTOR:",
# "RECLAMANTE:", "RÉU:"... Pega o nome quando o cue de qualificação ("brasileiro"...)
# está separado dele por OUTRO rótulo (ex.: "REQUERENTE: Fulano, nacionalidade:
# brasileiro" — comum nos modelos do TJDFT), caso em que o anchor por cue falha.
_PARTY_LABEL = (
    r"(?:PARTE[^\S\n]+)?(?:REQUERENTES?|REQUERID[OA]S?|RECLAMANTES?|RECLAMAD[OA]S?"
    r"|AUTOR(?:ES|AS|A)?|R[ÉE]US?|RÉS?|EXEQUENTES?|EXECUTAD[OA]S?"
    r"|IMPETRANTES?|IMPETRAD[OA]S?|EMBARGANTES?|EMBARGAD[OA]S?)"
)
# Rótulo (grupo 1, preservado) + ":" + nome(s) no mesmo bloco (grupo 2, mascarado).
# Suporta litisconsórcio (lista separada por vírgula/"e"). O comma após o nome (antes
# de "nacionalidade:"/"CPF:") encerra o nome — não há over-mask do rótulo seguinte.
# Tolera um parêntese de papel entre o rótulo e os ":" (ex.: "REQUERENTE (proprietário):",
# "REQUERIDA (condutor) :"), comum nos modelos do TJDFT com duas partes por polo.
_NAME_AFTER_LABEL = re.compile(
    r"(\b(?:" + _PARTY_LABEL + r")[^\S\n]*(?:\([^)\n]{0,40}\)[^\S\n]*)?:[^\S\n]*)"
    r"(" + _NAME + r"(?:" + _NAME_SEP + _NAME + r")*)"
)
# Para remascarar cada nome dentro de uma lista, preservando os separadores.
_NAME_SOLO = re.compile(_NAME)


class RegexAnonymizer:
    """Implementação do port `Anonymizer` baseada em regex."""

    def anonymize(self, text: str) -> str:
        for placeholder, pattern in _PATTERNS:
            text = pattern.sub(placeholder, text)
        for placeholder, pattern in _ANCHORED_PATTERNS:
            # Preserva o rótulo (grupo 1, via \g<1>) e mascara só o valor (grupo 2).
            text = pattern.sub(r"\g<1>" + placeholder, text)
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
        # Âncora por rótulo de polo primeiro (mais específica): "REQUERENTE: Fulano".
        text = _NAME_AFTER_LABEL.sub(
            lambda m: m.group(1) + _NAME_SOLO.sub("[NOME]", m.group(2)), text
        )
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

    def anonymize_mapped(self, text: str) -> tuple[str, dict[str, str]]:
        return text, {}


class MappedRegexAnonymizer:
    """RegexAnonymizer com mapeamento reversível → **pseudonimização** sob a LGPD.

    O mapa retido (placeholder→valor) torna o masking reversível: juridicamente é
    pseudonimização (art. 5º XI), **não** anonimização — o dado continua pessoal e no
    escopo da LGPD (ver ADR-0012). O nome da classe é mantido por estabilidade.
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
        # Identificadores ancorados: mascara só o grupo 2 (o valor), preservando o rótulo.
        for placeholder_base, pattern in _ANCHORED_PATTERNS:
            base = placeholder_base.strip("[]")
            for match in reversed(list(pattern.finditer(result))):
                counters[base] = counters.get(base, 0) + 1
                key = f"[{base}_{counters[base]}]"
                mapping[key] = match.group(2)
                result = result[: match.start(2)] + key + result[match.end(2) :]
        return result, mapping


class MappedRegexNameAnonymizer:
    """Versão reversível do `RegexNameAnonymizer`: numera cada nome (`[NOME_1]`,
    `[NOME_2]`...) e devolve o mapa placeholder→nome, para restaurar os nomes reais
    no resumo exibido ao revisor (a LGPD exige proteger o LLM externo, não o humano)."""

    def anonymize(self, text: str) -> str:
        return self.anonymize_mapped(text)[0]

    def anonymize_mapped(self, text: str) -> tuple[str, dict[str, str]]:
        mapping: dict[str, str] = {}
        counter = 0

        def _placeholder(name: str) -> str:
            nonlocal counter
            counter += 1
            key = f"[NOME_{counter}]"
            mapping[key] = name
            return key

        # Âncora por rótulo de polo primeiro (mais específica): "REQUERENTE: Fulano".
        text = _NAME_AFTER_LABEL.sub(
            lambda m: m.group(1) + _NAME_SOLO.sub(lambda mm: _placeholder(mm.group()), m.group(2)),
            text,
        )
        # Lista antes do cue: cada nome vira um placeholder numerado distinto.
        text = _NAME_LIST_BEFORE_CUE.sub(
            lambda m: _NAME_SOLO.sub(lambda mm: _placeholder(mm.group()), m.group(0)), text
        )
        # Nome após "em face de/da" / "em desfavor de".
        text = _NAME_AFTER_PARTY.sub(lambda m: m.group(1) + _placeholder(m.group(2)), text)
        return text, mapping


class MappedCompositeAnonymizer:
    """Encadeia anonimizadores **reversíveis** acumulando o mapa combinado."""

    def __init__(
        self, anonymizers: list[MappedRegexAnonymizer | MappedRegexNameAnonymizer]
    ) -> None:
        self._anonymizers = anonymizers

    def anonymize(self, text: str) -> str:
        return self.anonymize_mapped(text)[0]

    def anonymize_mapped(self, text: str) -> tuple[str, dict[str, str]]:
        mapping: dict[str, str] = {}
        for anonymizer in self._anonymizers:
            text, partial = anonymizer.anonymize_mapped(text)
            mapping.update(partial)
        return text, mapping
