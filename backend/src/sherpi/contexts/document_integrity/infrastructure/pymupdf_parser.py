"""Adapter de parsing baseado em PyMuPDF.

Traduz um PDF (bytes não-confiáveis) na `ParsedDocument` pura que o detector
consome, preservando os atributos visuais necessários à análise forense.
Trata o arquivo como hostil: qualquer falha de parsing vira
`UntrustedDocumentError` (nunca propaga exceção crua do PyMuPDF).

Limitações conhecidas (POC → refinar na Fase 4):
- `/ActualText` por span não é extraído pelo PyMuPDF; o detector cobre o vetor
  via testes sintéticos, e este adapter o deixa como None.
- Atribuição de span↔camada OCG é best-effort (diff de texto on/off).
"""

from __future__ import annotations

import pymupdf

from sherpi.contexts.document_integrity.domain.document import (
    PageGeometry,
    ParsedDocument,
    TextSpan,
)
from sherpi.shared_kernel.errors import UntrustedDocumentError


def _int_to_rgb(color: int) -> tuple[float, float, float]:
    """Converte cor sRGB inteira do PyMuPDF em RGB normalizado de 0 a 1."""
    return ((color >> 16) & 0xFF) / 255.0, ((color >> 8) & 0xFF) / 255.0, (color & 0xFF) / 255.0


class PyMuPDFParser:
    """Implementação do port `PdfParser` usando PyMuPDF."""

    def parse(self, content: bytes, *, max_pages: int) -> ParsedDocument:
        try:
            doc = pymupdf.open(stream=content, filetype="pdf")
        except Exception as exc:  # parsing de arquivo hostil
            raise UntrustedDocumentError(f"Falha ao abrir o PDF: {exc}") from exc

        try:
            if doc.page_count > max_pages:
                raise UntrustedDocumentError(
                    f"PDF excede o limite de {max_pages} páginas ({doc.page_count})."
                )

            spans: list[TextSpan] = []
            pages: list[PageGeometry] = []
            for index in range(doc.page_count):
                page = doc[index]
                # Preserva a CropBox ORIGINAL (área visível) e expande para a
                # MediaBox para que o texto escondido FORA da CropBox também seja
                # extraído — é exatamente o que um parser ingênuo entregaria à IA.
                cb = page.cropbox
                cropbox = (cb.x0, cb.y0, cb.x1, cb.y1)
                page.set_cropbox(page.mediabox)
                pages.append(PageGeometry(page=index, cropbox=cropbox))
                spans.extend(self._extract_spans(page, index))

            return ParsedDocument(
                page_count=doc.page_count,
                spans=spans,
                pages=pages,
                metadata=self._extract_metadata(doc),
                has_optional_content=bool(doc.get_ocgs()),
            )
        finally:
            doc.close()

    @staticmethod
    def _extract_spans(page: pymupdf.Page, index: int) -> list[TextSpan]:
        spans: list[TextSpan] = []
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if not text:
                        continue
                    spans.append(
                        TextSpan(
                            text=text,
                            rgb=_int_to_rgb(int(span.get("color", 0))),
                            size=float(span.get("size", 0.0)),
                            bbox=tuple(span["bbox"]),
                            page=index,
                        )
                    )
        return spans

    @staticmethod
    def _extract_metadata(doc: pymupdf.Document) -> dict[str, str]:
        meta: dict[str, str] = {}
        for key, value in (doc.metadata or {}).items():
            if isinstance(value, str) and value.strip():
                meta[key] = value
        # XMP completo entra como um único campo para varredura de palavras-chave.
        try:
            xmp = doc.get_xml_metadata()
            if xmp:
                meta["xmp"] = xmp
        except Exception:  # XMP malformado não deve derrubar o parsing
            pass
        return meta
