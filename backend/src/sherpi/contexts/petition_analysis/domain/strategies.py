"""Estratégias de admissibilidade por rito processual (ADR-0008).

Cada rito implementa `AdmissibilityStrategy`. O cível (CPC art. 319) é a estratégia
base; o trabalhista (CLT art. 840 §1º) **reaproveita** a checagem do art. 319 e
**acrescenta** a exigência de pedido líquido. Um registro (`DEFAULT_STRATEGIES`)
mapeia `Rito → estratégia`; `CheckAdmissibility` apenas despacha.

Os tipos compartilhados (`ChecklistItem`, `AdmissibilityReport`, `Requirement`, …) e os
helpers determinísticos (`parse_claim_amount`, validação de CPF/CNPJ) vivem em
`admissibility.py` — este módulo os importa, evitando ciclo.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.petition_analysis.domain.admissibility import (
    AdmissibilityReport,
    ChecklistItem,
    CheckMethod,
    Requirement,
    _scan_valid_document,
    _valid_document,
    parse_claim_amount,
)
from sherpi.contexts.petition_analysis.domain.summary import PetitionSummary, Polo
from sherpi.shared_kernel.value_objects import Rito

# Documentos essenciais cuja menção é checada semanticamente.
_ESSENTIAL_DOCS = ("procuração", "procuracao")

# Marcadores formais buscados no TEXTO BRUTO para detectar quando a extração pode ter
# RECUPERADO da narrativa um elemento que a peça não traz formalmente (limitação
# conhecida — ver backlog). Basta UM marcador presente (peças BR quase sempre têm
# "requer"/"ante o exposto"/"valor da causa"), o que mantém o falso-positivo baixo.
_CLAIMS_MARKERS = (
    "dos pedidos",
    "do pedido",
    "requer",
    "postula",
    "pugna",
    "ante o exposto",
    "isto posto",
    "pede deferimento",
)
_CLAIM_VALUE_MARKERS = (
    "valor da causa",
    "dá-se à causa",
    "da-se a causa",
    "dá à causa",
    "atribui-se à causa",
    "atribui à causa",
)
_CAVEAT_CLAIMS = (
    "Pedidos possivelmente inferidos da narrativa — seção formal de pedidos não "
    "localizada no texto. Confirme na peça original."
)
_CAVEAT_CLAIM_VALUE = (
    "Valor da causa possivelmente inferido — declaração formal do valor da causa não "
    "localizada no texto. Confirme na peça original."
)


def _missing_marker(raw_text: str | None, markers: tuple[str, ...]) -> bool:
    """True se há texto bruto e NENHUM marcador formal aparece nele (case-insensitive).

    Sem texto bruto, não há como cross-checar → retorna False (sem caveat).
    """
    if not raw_text:
        return False
    low = raw_text.lower()
    return not any(m in low for m in markers)


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
        return AdmissibilityReport.from_items(self._items_art319(summary, raw_text))

    def _items_art319(self, s: PetitionSummary, raw_text: str | None) -> list[ChecklistItem]:
        """Checklist do art. 319 do CPC — comum a todos os ritos."""
        return [
            self._check_court(s),
            self._check_parties(s),
            self._check_qualification(s, raw_text),
            self._check_text(Requirement.FACTS, s.facts),
            self._check_text(Requirement.LEGAL_BASIS, s.legal_basis),
            self._check_claims(s, raw_text),
            self._check_claim_value(s, raw_text),
            self._check_evidence(s),
            self._check_hearing(s),
            self._check_documents(s),
        ]

    @staticmethod
    def _det(
        req: Requirement,
        present: bool,
        evid: str | None,
        detail: str,
        *,
        caveat: str | None = None,
    ) -> ChecklistItem:
        return ChecklistItem(
            requirement=req,
            present=present,
            method=CheckMethod.DETERMINISTIC,
            evidence=evid,
            detail=detail,
            caveat=caveat,
        )

    def _check_parties(self, s: PetitionSummary) -> ChecklistItem:
        has_active = any(p.pole is Polo.ACTIVE for p in s.parties)
        has_passive = any(p.pole is Polo.PASSIVE for p in s.parties)
        present = has_active and has_passive
        return self._det(
            Requirement.PARTIES,
            present,
            evid=f"{len(s.parties)} parte(s)",
            detail="Polos ativo e passivo identificados."
            if present
            else "Falta polo ativo/passivo.",
        )

    def _check_qualification(self, s: PetitionSummary, raw_text: str | None) -> ChecklistItem:
        # 1. Parte ativa extraída pelo LLM tem precedência (documento não-mascarado).
        for parte in s.parties:
            if parte.pole is Polo.ACTIVE:
                doc = _valid_document(parte.document)
                if doc:
                    return self._det(
                        Requirement.QUALIFICATION, True, doc, "CPF/CNPJ do autor válido (checksum)."
                    )
                # Documento mascarado pela anonimização — validar pelo texto original.
                if raw_text is not None:
                    doc = _scan_valid_document(raw_text)
                    detail = (
                        "CPF/CNPJ válido no documento (checksum)."
                        if doc
                        else "Sem CPF/CNPJ válido."
                    )
                    return self._det(Requirement.QUALIFICATION, doc is not None, doc, detail)
                return self._det(
                    Requirement.QUALIFICATION, False, None, "Autor sem CPF/CNPJ válido."
                )
        # 2. LLM não identificou parte ativa — escanear texto original como fallback.
        if raw_text is not None:
            doc = _scan_valid_document(raw_text)
            detail = "CPF/CNPJ válido no documento." if doc else "Sem CPF/CNPJ válido."
            return self._det(Requirement.QUALIFICATION, doc is not None, doc, detail)
        return self._det(Requirement.QUALIFICATION, False, None, "Autor sem CPF/CNPJ válido.")

    def _check_text(self, req: Requirement, value: str) -> ChecklistItem:
        present = bool(value and value.strip())
        return self._det(
            req, present, evid=None, detail="Campo presente." if present else "Ausente."
        )

    def _check_claims(self, s: PetitionSummary, raw_text: str | None) -> ChecklistItem:
        present = len(s.claims) > 0
        caveat = _CAVEAT_CLAIMS if present and _missing_marker(raw_text, _CLAIMS_MARKERS) else None
        return self._det(
            Requirement.CLAIMS,
            present,
            evid=f"{len(s.claims)} pedido(s)",
            detail="Pedidos formulados." if present else "Nenhum pedido identificado.",
            caveat=caveat,
        )

    def _check_claim_value(self, s: PetitionSummary, raw_text: str | None) -> ChecklistItem:
        valor = parse_claim_amount(s.claim_amount)
        present = valor is not None
        caveat = (
            _CAVEAT_CLAIM_VALUE
            if present and _missing_marker(raw_text, _CLAIM_VALUE_MARKERS)
            else None
        )
        return self._det(
            Requirement.CLAIM_VALUE,
            present,
            evid=valor.formatted if valor else s.claim_amount,
            detail="Valor da causa válido." if present else "Valor da causa ausente/ilegível.",
            caveat=caveat,
        )

    @staticmethod
    def _sem(req: Requirement, present: bool, evid: str | None, detail: str) -> ChecklistItem:
        return ChecklistItem(
            requirement=req,
            present=present,
            method=CheckMethod.SEMANTIC,
            evidence=evid,
            detail=detail,
        )

    def _check_court(self, s: PetitionSummary) -> ChecklistItem:
        present = bool(s.court and s.court.strip())
        return self._sem(
            Requirement.COURT,
            present,
            evid=s.court,
            detail="Endereçamento ao juízo presente."
            if present
            else "Sem endereçamento (art. 319, I).",
        )

    def _check_evidence(self, s: PetitionSummary) -> ChecklistItem:
        return self._sem(
            Requirement.EVIDENCE,
            s.requests_evidence,
            evid=None,
            detail="Indica provas a produzir."
            if s.requests_evidence
            else "Não indica provas (art. 319, VI).",
        )

    def _check_hearing(self, s: PetitionSummary) -> ChecklistItem:
        present = s.hearing_option is not None
        return self._sem(
            Requirement.HEARING,
            present,
            evid=("opta por audiência" if s.hearing_option else "dispensa audiência")
            if present
            else None,
            detail="Manifestou opção sobre audiência."
            if present
            else "Omisso quanto à audiência (art. 319, VII).",
        )

    def _check_documents(self, s: PetitionSummary) -> ChecklistItem:
        mentioned = " ".join(s.cited_documents).lower()
        present = any(doc in mentioned for doc in _ESSENTIAL_DOCS)
        return ChecklistItem(
            requirement=Requirement.DOCUMENTS,
            present=present,
            method=CheckMethod.SEMANTIC,
            evidence=", ".join(s.cited_documents) or None,
            detail="Procuração mencionada." if present else "Procuração não mencionada.",
        )


class TrabalhistaStrategy(CivelStrategy):
    """Admissibilidade do rito trabalhista (CLT art. 840 §1º).

    Herda o checklist do art. 319 (partes, fatos, pedidos, valor, etc.) e acrescenta
    a exigência de **pedido líquido**: cada pedido deve vir com valor (certo e
    determinado). Pedido ilíquido → requisito essencial ausente → emenda (RED).
    """

    def run(self, summary: PetitionSummary, *, raw_text: str | None = None) -> AdmissibilityReport:
        items = self._items_art319(summary, raw_text)
        items.append(self._check_liquid_claim(summary))
        return AdmissibilityReport.from_items(items)

    def _check_liquid_claim(self, s: PetitionSummary) -> ChecklistItem:
        illiquid = [p for p in s.claims if parse_claim_amount(p.amount) is None]
        present = bool(s.claims) and not illiquid
        if not s.claims:
            evid, detail = None, "Sem pedidos para aferir liquidez (CLT art. 840 §1º)."
        elif present:
            evid = f"{len(s.claims)} pedido(s) com valor"
            detail = "Todos os pedidos são líquidos (com valor)."
        else:
            evid = "; ".join(p.description for p in illiquid)
            detail = "Pedido(s) ilíquido(s): CLT art. 840 §1º exige valor por pedido."
        return self._det(Requirement.LIQUID_CLAIM, present, evid, detail)


# Registro padrão Rito → estratégia. Novo rito = nova entrada (open/closed).
DEFAULT_STRATEGIES: dict[Rito, AdmissibilityStrategy] = {
    Rito.CIVEL: CivelStrategy(),
    Rito.TRABALHISTA: TrabalhistaStrategy(),
}
