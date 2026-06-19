"""Estratégias de admissibilidade por rito processual (ADR-0008).

Cada rito implementa `AdmissibilityStrategy`. O cível (CPC art. 319) é a estratégia
base; o trabalhista (CLT art. 840 §1º) **reaproveita** a checagem do art. 319 e
**acrescenta** a exigência de pedido líquido. Um registro (`DEFAULT_STRATEGIES`)
mapeia `Rito → estratégia`; `CheckAdmissibility` apenas despacha.

Os tipos compartilhados (`ChecklistItem`, `AdmissibilityReport`, `Requisito`, …) e os
helpers determinísticos (`parse_valor_causa`, validação de CPF/CNPJ) vivem em
`admissibility.py` — este módulo os importa, evitando ciclo.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.petition_analysis.domain.admissibility import (
    AdmissibilityReport,
    ChecklistItem,
    MetodoCheck,
    Requisito,
    _scan_valid_documento,
    _valid_documento,
    parse_valor_causa,
)
from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary, Polo
from sherpi.shared_kernel.value_objects import Rito

# Documentos essenciais cuja menção é checada semanticamente.
_DOCS_ESSENCIAIS = ("procuração", "procuracao")


@runtime_checkable
class AdmissibilityStrategy(Protocol):
    """Conjunto de regras de admissibilidade de um rito.

    `raw_text` é o texto ORIGINAL (não anonimizado), usado nas checagens
    determinísticas de CPF/CNPJ (robusto ao mascaramento de PII feito para o LLM).
    """

    def run(
        self, summary: PetitionSummary, *, raw_text: str | None = None
    ) -> AdmissibilityReport: ...


class CivelStrategy:
    """Admissibilidade do rito cível (CPC art. 319/320/321)."""

    def run(self, summary: PetitionSummary, *, raw_text: str | None = None) -> AdmissibilityReport:
        return AdmissibilityReport.from_items(self._itens_art319(summary, raw_text))

    def _itens_art319(self, s: PetitionSummary, raw_text: str | None) -> list[ChecklistItem]:
        """Checklist do art. 319 do CPC — comum a todos os ritos."""
        return [
            self._check_juizo(s),
            self._check_partes(s),
            self._check_qualificacao(s, raw_text),
            self._check_texto(Requisito.FATOS, s.fato_gerador),
            self._check_texto(Requisito.FUNDAMENTACAO, s.fundamentacao),
            self._check_pedidos(s),
            self._check_valor_causa(s),
            self._check_provas(s),
            self._check_audiencia(s),
            self._check_documentos(s),
        ]

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


class TrabalhistaStrategy(CivelStrategy):
    """Admissibilidade do rito trabalhista (CLT art. 840 §1º).

    Herda o checklist do art. 319 (partes, fatos, pedidos, valor, etc.) e acrescenta
    a exigência de **pedido líquido**: cada pedido deve vir com valor (certo e
    determinado). Pedido ilíquido → requisito essencial ausente → emenda (VERMELHO).
    """

    def run(self, summary: PetitionSummary, *, raw_text: str | None = None) -> AdmissibilityReport:
        itens = self._itens_art319(summary, raw_text)
        itens.append(self._check_pedido_liquido(summary))
        return AdmissibilityReport.from_items(itens)

    def _check_pedido_liquido(self, s: PetitionSummary) -> ChecklistItem:
        iliquidos = [p for p in s.pedidos if parse_valor_causa(p.valor) is None]
        presente = bool(s.pedidos) and not iliquidos
        if not s.pedidos:
            evid, detalhe = None, "Sem pedidos para aferir liquidez (CLT art. 840 §1º)."
        elif presente:
            evid = f"{len(s.pedidos)} pedido(s) com valor"
            detalhe = "Todos os pedidos são líquidos (com valor)."
        else:
            evid = "; ".join(p.descricao for p in iliquidos)
            detalhe = "Pedido(s) ilíquido(s): CLT art. 840 §1º exige valor por pedido."
        return self._det(Requisito.PEDIDO_LIQUIDO, presente, evid, detalhe)


# Registro padrão Rito → estratégia. Novo rito = nova entrada (open/closed).
DEFAULT_STRATEGIES: dict[Rito, AdmissibilityStrategy] = {
    Rito.CIVEL: CivelStrategy(),
    Rito.TRABALHISTA: TrabalhistaStrategy(),
}
