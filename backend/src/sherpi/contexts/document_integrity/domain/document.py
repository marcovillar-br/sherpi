"""Representação pura de um PDF para análise forense.

Estas estruturas são a fronteira entre o adapter de parsing (PyMuPDF, na
infraestrutura) e o domínio puro (`DetectInjection`). Não contêm nenhuma
dependência de PyMuPDF — apenas dados. Isso permite testar o detector com
documentos sintéticos, sem PDFs reais.
"""

from __future__ import annotations

from pydantic import BaseModel

# (x0, y0, x1, y1) em pontos PDF.
BBox = tuple[float, float, float, float]
# Componentes RGB normalizados de 0.0 a 1.0.
Rgb = tuple[float, float, float]


class TextSpan(BaseModel):
    """Um trecho contíguo de texto com seus atributos visuais."""

    model_config = {"frozen": True}

    text: str
    rgb: Rgb
    size: float  # tamanho da fonte em pontos
    bbox: BBox
    page: int  # índice da página (0-based)
    in_hidden_ocg: bool = False  # pertence a uma camada (OCG) desativada
    actual_text: str | None = None  # /ActualText associado (camada de acessibilidade)


class PageGeometry(BaseModel):
    """Geometria de uma página: o que é efetivamente visível (CropBox)."""

    model_config = {"frozen": True}

    page: int
    cropbox: BBox


class ParsedDocument(BaseModel):
    """Resultado estrutural do parsing, consumido pelo detector."""

    model_config = {"frozen": True}

    page_count: int
    spans: list[TextSpan]
    pages: list[PageGeometry]
    # Metadados /Info + XMP achatados em pares chave→valor (ex.: Subject, Keywords).
    metadata: dict[str, str] = {}
    # True se o documento declara OCGs (camadas de conteúdo opcional).
    has_optional_content: bool = False

    def visible_text(self) -> str:
        """Texto que um humano de fato enxerga (exclui spans ocultos)."""
        from .detector import is_span_hidden  # import tardio: evita ciclo

        return " ".join(s.text for s in self.spans if not is_span_hidden(s, self))
