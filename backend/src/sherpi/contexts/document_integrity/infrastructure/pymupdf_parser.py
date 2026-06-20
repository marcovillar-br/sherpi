"""Adapter de parsing baseado em PyMuPDF.

Traduz um PDF (bytes não-confiáveis) na `ParsedDocument` pura que o detector
consome, preservando os atributos visuais necessários à análise forense.
Trata o arquivo como hostil: qualquer falha de parsing vira
`UntrustedDocumentError` (nunca propaga exceção crua do PyMuPDF).

Limitações conhecidas (MVP → refinar na Fase 4):
- `/ActualText` por span não é extraído pelo PyMuPDF; o detector cobre o vetor
  via testes sintéticos, e este adapter o deixa como None.
- Atribuição de span↔camada OCG é best-effort (diff de texto on/off).
"""

from __future__ import annotations

import signal
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from types import FrameType

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


@contextmanager
def _parse_deadline(seconds: float) -> Iterator[None]:
    """Guarda de tempo (best-effort) em torno do parsing CPU-bound do PyMuPDF.

    Mitiga DoS por parsing lento (ex.: bomba de descompressão) cortando o fluxo
    quando o tempo de parede estoura. Usa SIGALRM, que tem limites conhecidos:
    só funciona em Unix e na main thread, e NÃO interrompe um laço preso em
    código C nativo até o controle voltar ao Python. O isolamento pleno de
    recursos (subprocesso + `setrlimit`) fica para a Fase 4. Fora desse cenário
    (thread worker, plataforma sem SIGALRM, ou `seconds<=0`) degrada para no-op.
    """
    usable = (
        seconds > 0
        and hasattr(signal, "SIGALRM")
        and threading.current_thread() is threading.main_thread()
    )
    if not usable:
        yield
        return

    def _on_timeout(signum: int, frame: FrameType | None) -> None:
        raise UntrustedDocumentError(f"Parsing do PDF excedeu {seconds:g}s (possível DoS).")

    previous = signal.signal(signal.SIGALRM, _on_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


class PyMuPDFParser:
    """Implementação do port `PdfParser` usando PyMuPDF."""

    def __init__(self, *, timeout_seconds: float = 0.0) -> None:
        # 0.0 desativa a guarda de tempo (default usado por testes/evals); a API
        # injeta `pdf_parse_timeout_seconds` da config no wiring de produção.
        self._timeout_seconds = timeout_seconds

    def parse(self, content: bytes, *, max_pages: int) -> ParsedDocument:
        with _parse_deadline(self._timeout_seconds):
            return self._parse(content, max_pages=max_pages)

    def _parse(self, content: bytes, *, max_pages: int) -> ParsedDocument:
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
                page_spans = self._extract_spans(page, index)
                spans.extend(page_spans)
                page_area = max((cb.x1 - cb.x0) * (cb.y1 - cb.y0), 1.0)
                pages.append(
                    PageGeometry(
                        page=index,
                        cropbox=cropbox,
                        has_text=any(s.text.strip() for s in page_spans),
                        image_ratio=min(self._image_area(page) / page_area, 1.0),
                    )
                )

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
    def _image_area(page: pymupdf.Page) -> float:
        """Área total coberta por blocos de imagem na página (pontos²)."""
        total = 0.0
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") == 1:  # bloco de imagem (0 = texto)
                x0, y0, x1, y1 = block["bbox"]
                total += (x1 - x0) * (y1 - y0)
        return total

    @staticmethod
    def _extract_spans(page: pymupdf.Page, index: int) -> list[TextSpan]:
        spans: list[TextSpan] = []
        data = page.get_text("dict")
        for block_idx, block in enumerate(data.get("blocks", [])):
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
                            block=block_idx,
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
