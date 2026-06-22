"""Testes do agrupamento por bloco em ParsedDocument.visible_text."""

from __future__ import annotations

from sherpi.contexts.document_integrity.domain.document import (
    PageGeometry,
    ParsedDocument,
    TextSpan,
)

_A4 = (0.0, 0.0, 595.0, 842.0)


def _span(text: str, block: int, page: int = 0) -> TextSpan:
    return TextSpan(
        text=text, rgb=(0.0, 0.0, 0.0), size=12.0, bbox=(10, 10, 100, 20), page=page, block=block
    )


def _doc(spans: list[TextSpan]) -> ParsedDocument:
    return ParsedDocument(page_count=1, spans=spans, pages=[PageGeometry(page=0, cropbox=_A4)])


def test_visible_text_joins_within_block_and_breaks_between_blocks() -> None:
    doc = _doc(
        [
            _span("Endereçamento", 0),
            _span("AÇÃO DE COBRANÇA", 1),
            _span("FULANO", 2),
            _span("DE TAL", 2),
        ]
    )
    assert doc.visible_text() == "Endereçamento\nAÇÃO DE COBRANÇA\nFULANO DE TAL"


def test_visible_text_single_block_is_space_joined() -> None:
    # Retrocompat: tudo no bloco 0 (default) → comportamento antigo (espaço).
    doc = _doc([_span("a", 0), _span("b", 0), _span("c", 0)])
    assert doc.visible_text() == "a b c"
