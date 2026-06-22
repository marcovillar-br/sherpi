"""Dedup de boilerplate por bloco no visible_text (disclaimer/rodapé repetido por página)."""

from __future__ import annotations

from sherpi.contexts.document_integrity.domain.document import ParsedDocument, TextSpan

_DISCLAIMER = (
    "MODELO AVISO - este modelo de petição é uma ferramenta para auxiliar cidadãos que não "
    "têm advogado. É importante lembrar que você é responsável por preencher os dados. "
    "_______________________________________________________________________________"
)


def _doc(spans: list[tuple[int, int, str]]) -> ParsedDocument:
    return ParsedDocument(
        page_count=max((p for p, _, _ in spans), default=0) + 1,
        spans=[
            TextSpan(text=t, rgb=(0, 0, 0), size=11.0, bbox=(0, 0, 1, 1), page=p, block=b)
            for p, b, t in spans
        ],
        pages=[],
    )


def test_removes_pure_repeated_disclaimer_block():
    # disclaimer puro no bloco 0 de 3 páginas → removido; conteúdo único preservado.
    doc = _doc(
        [
            (0, 0, _DISCLAIMER),
            (0, 1, "PETIÇÃO INICIAL conteúdo da página um"),
            (1, 0, _DISCLAIMER),
            (1, 1, "DOS FATOS conteúdo da página dois"),
            (2, 0, _DISCLAIMER),
            (2, 1, "DOS PEDIDOS conteúdo da página três"),
        ]
    )
    out = doc.visible_text(dedup_boilerplate=True)
    assert "MODELO AVISO" not in out
    assert "PETIÇÃO INICIAL conteúdo da página um" in out
    assert "DOS PEDIDOS conteúdo da página três" in out


def test_strips_disclaimer_glued_to_legit_content():
    # disclaimer COLADO a conteúdo legítimo num bloco → remove só o disclaimer.
    # (3 ocorrências puras estabelecem o boilerplate; a 4ª vem colada.)
    glued = _DISCLAIMER + " em face da PARTE REQUERIDA: [NOME_2] S/A, pessoa jurídica"
    doc = _doc([(0, 0, _DISCLAIMER), (1, 0, _DISCLAIMER), (2, 0, _DISCLAIMER), (3, 0, glued)])
    out = doc.visible_text(dedup_boilerplate=True)
    assert "MODELO AVISO" not in out
    assert "em face da PARTE REQUERIDA: [NOME_2] S/A, pessoa jurídica" in out


def test_default_keeps_boilerplate_untouched():
    # sem o flag, o texto íntegro (admissibilidade usa este caminho).
    doc = _doc([(0, 0, _DISCLAIMER), (1, 0, _DISCLAIMER), (2, 0, _DISCLAIMER)])
    assert doc.visible_text().count("MODELO AVISO") == 3


def test_below_threshold_not_removed():
    # repete só 2x (< 3) → preservado (evita falso-positivo).
    doc = _doc([(0, 0, _DISCLAIMER), (1, 0, _DISCLAIMER)])
    assert doc.visible_text(dedup_boilerplate=True).count("MODELO AVISO") == 2
