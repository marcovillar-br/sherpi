"""Checagem de admissibilidade da petição inicial (arts. 319/321 do CPC).

Domain service **puro**: opera sobre o `PetitionSummary` extraído e produz um
`AdmissibilityReport`. Separa explicitamente:
- **validadores determinísticos** (checksum de CPF/CNPJ, parsing do valor da causa,
  presença de campos) — confiáveis e exatos;
- **checagem semântica** (menção a documentos essenciais) — proveniente da extração.

Cada item carrega o método e a evidência (proveniência), atendendo à
interpretabilidade exigida.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from pydantic import BaseModel

from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary, Polo
from sherpi.shared_kernel.value_objects import CNPJ, CPF, ValorCausa


class Semaforo(StrEnum):
    VERDE = "VERDE"  # apto a prosseguir
    AMARELO = "AMARELO"  # vícios sanáveis menores
    VERMELHO = "VERMELHO"  # requer emenda (art. 321)


class MetodoCheck(StrEnum):
    DETERMINISTICO = "DETERMINISTICO"
    SEMANTICO = "SEMANTICO"


class Requisito(StrEnum):
    JUIZO = "juizo"  # art. 319, I
    PARTES = "partes"  # art. 319, II
    QUALIFICACAO = "qualificacao"  # art. 319, II
    FATOS = "fatos"  # art. 319, III
    FUNDAMENTACAO = "fundamentacao"  # art. 319, III
    PEDIDOS = "pedidos"  # art. 319, IV
    VALOR_CAUSA = "valor_causa"  # art. 319, V
    PROVAS = "provas"  # art. 319, VI
    AUDIENCIA = "audiencia"  # art. 319, VII
    DOCUMENTOS = "documentos"  # art. 320 (procuração etc.)


# Requisitos essenciais cuja ausência exige emenda (art. 321) → VERMELHO.
_ESSENCIAIS = {Requisito.PARTES, Requisito.FATOS, Requisito.PEDIDOS, Requisito.VALOR_CAUSA}

# Documentos essenciais cuja menção é checada semanticamente.
_DOCS_ESSENCIAIS = ("procuração", "procuracao")

# Candidatos a CPF/CNPJ no texto bruto (validação por checksum vem depois).
_CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


class ChecklistItem(BaseModel):
    model_config = {"frozen": True}

    requisito: Requisito
    presente: bool
    metodo: MetodoCheck
    evidencia: str | None = None
    detalhe: str | None = None


class AdmissibilityReport(BaseModel):
    model_config = {"frozen": True}

    itens: list[ChecklistItem]
    semaforo: Semaforo
    requer_emenda: bool

    @classmethod
    def from_items(cls, itens: list[ChecklistItem]) -> AdmissibilityReport:
        ausentes = {i.requisito for i in itens if not i.presente}
        requer_emenda = bool(ausentes & _ESSENCIAIS)
        if requer_emenda:
            semaforo = Semaforo.VERMELHO
        elif ausentes:
            semaforo = Semaforo.AMARELO
        else:
            semaforo = Semaforo.VERDE
        return cls(itens=itens, semaforo=semaforo, requer_emenda=requer_emenda)


def parse_valor_causa(texto: str | None) -> ValorCausa | None:
    """Converte 'R$ 15.000,00' (ou variações) em `ValorCausa`. None se não parseável."""
    if not texto:
        return None
    raw = re.sub(r"[^0-9,.]", "", texto)
    if not raw:
        return None
    # Formato brasileiro: '.' separa milhar e ',' separa decimal.
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    try:
        return ValorCausa(amount=amount)
    except ValueError:
        return None


def _valid_documento(value: str | None) -> str | None:
    """Retorna o documento formatado se for CPF ou CNPJ válido; senão None."""
    if not value:
        return None
    for vo in (CPF, CNPJ):
        try:
            return vo(value=value).formatted
        except ValueError:
            continue
    return None


def _scan_valid_documento(text: str) -> str | None:
    """Procura no texto bruto o primeiro CPF/CNPJ com checksum válido."""
    for pattern in (_CNPJ_RE, _CPF_RE):
        for match in pattern.finditer(text):
            doc = _valid_documento(match.group())
            if doc:
                return doc
    return None


class CheckAdmissibility:
    """Domain service: avalia a admissibilidade de um `PetitionSummary`."""

    def run(self, summary: PetitionSummary, *, raw_text: str | None = None) -> AdmissibilityReport:
        """Avalia a admissibilidade.

        Se `raw_text` (texto ORIGINAL, não anonimizado) for fornecido, a validação
        de CPF/CNPJ roda sobre ele — assim o mascaramento de PII para o LLM não
        degrada a checagem determinística.
        """
        return AdmissibilityReport.from_items(
            [
                self._check_juizo(summary),
                self._check_partes(summary),
                self._check_qualificacao(summary, raw_text),
                self._check_texto(Requisito.FATOS, summary.fato_gerador),
                self._check_texto(Requisito.FUNDAMENTACAO, summary.fundamentacao),
                self._check_pedidos(summary),
                self._check_valor_causa(summary),
                self._check_provas(summary),
                self._check_audiencia(summary),
                self._check_documentos(summary),
            ]
        )

    @staticmethod
    def _det(req: Requisito, presente: bool, evid: str | None, detalhe: str) -> ChecklistItem:
        return ChecklistItem(
            requisito=req,
            presente=presente,
            metodo=MetodoCheck.DETERMINISTICO,
            evidencia=evid,
            detalhe=detalhe,
        )

    def _check_partes(self, s: PetitionSummary) -> ChecklistItem:
        tem_ativo = any(p.polo is Polo.ATIVO for p in s.partes)
        tem_passivo = any(p.polo is Polo.PASSIVO for p in s.partes)
        presente = tem_ativo and tem_passivo
        return self._det(
            Requisito.PARTES,
            presente,
            evid=f"{len(s.partes)} parte(s)",
            detalhe="Polos ativo e passivo identificados."
            if presente
            else "Falta polo ativo/passivo.",
        )

    def _check_qualificacao(self, s: PetitionSummary, raw_text: str | None) -> ChecklistItem:
        # Preferir o texto ORIGINAL (robusto ao mascaramento de PII no resumo do LLM).
        if raw_text is not None:
            doc = _scan_valid_documento(raw_text)
            detalhe = "CPF/CNPJ válido no documento (checksum)." if doc else "Sem CPF/CNPJ válido."
            return self._det(Requisito.QUALIFICACAO, doc is not None, doc, detalhe)
        for parte in s.partes:
            if parte.polo is Polo.ATIVO:
                doc = _valid_documento(parte.documento)
                if doc:
                    return self._det(
                        Requisito.QUALIFICACAO, True, doc, "CPF/CNPJ do autor válido (checksum)."
                    )
        return self._det(Requisito.QUALIFICACAO, False, None, "Autor sem CPF/CNPJ válido.")

    def _check_texto(self, req: Requisito, valor: str) -> ChecklistItem:
        presente = bool(valor and valor.strip())
        return self._det(
            req, presente, evid=None, detalhe="Campo presente." if presente else "Ausente."
        )

    def _check_pedidos(self, s: PetitionSummary) -> ChecklistItem:
        presente = len(s.pedidos) > 0
        return self._det(
            Requisito.PEDIDOS,
            presente,
            evid=f"{len(s.pedidos)} pedido(s)",
            detalhe="Pedidos formulados." if presente else "Nenhum pedido identificado.",
        )

    def _check_valor_causa(self, s: PetitionSummary) -> ChecklistItem:
        valor = parse_valor_causa(s.valor_causa)
        presente = valor is not None
        return self._det(
            Requisito.VALOR_CAUSA,
            presente,
            evid=valor.formatted if valor else s.valor_causa,
            detalhe="Valor da causa válido." if presente else "Valor da causa ausente/ilegível.",
        )

    @staticmethod
    def _sem(req: Requisito, presente: bool, evid: str | None, detalhe: str) -> ChecklistItem:
        return ChecklistItem(
            requisito=req,
            presente=presente,
            metodo=MetodoCheck.SEMANTICO,
            evidencia=evid,
            detalhe=detalhe,
        )

    def _check_juizo(self, s: PetitionSummary) -> ChecklistItem:
        presente = bool(s.juizo and s.juizo.strip())
        return self._sem(
            Requisito.JUIZO,
            presente,
            evid=s.juizo,
            detalhe="Endereçamento ao juízo presente."
            if presente
            else "Sem endereçamento (art. 319, I).",
        )

    def _check_provas(self, s: PetitionSummary) -> ChecklistItem:
        return self._sem(
            Requisito.PROVAS,
            s.requer_provas,
            evid=None,
            detalhe="Indica provas a produzir."
            if s.requer_provas
            else "Não indica provas (art. 319, VI).",
        )

    def _check_audiencia(self, s: PetitionSummary) -> ChecklistItem:
        presente = s.opcao_audiencia is not None
        return self._sem(
            Requisito.AUDIENCIA,
            presente,
            evid=("opta por audiência" if s.opcao_audiencia else "dispensa audiência")
            if presente
            else None,
            detalhe="Manifestou opção sobre audiência."
            if presente
            else "Omisso quanto à audiência (art. 319, VII).",
        )

    def _check_documentos(self, s: PetitionSummary) -> ChecklistItem:
        mencionados = " ".join(s.documentos_mencionados).lower()
        presente = any(doc in mencionados for doc in _DOCS_ESSENCIAIS)
        return ChecklistItem(
            requisito=Requisito.DOCUMENTOS,
            presente=presente,
            metodo=MetodoCheck.SEMANTICO,
            evidencia=", ".join(s.documentos_mencionados) or None,
            detalhe="Procuração mencionada." if presente else "Procuração não mencionada.",
        )
