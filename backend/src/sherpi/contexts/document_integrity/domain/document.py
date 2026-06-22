"""Representação pura de um PDF para análise forense.

Estas estruturas são a fronteira entre o adapter de parsing (PyMuPDF, na
infraestrutura) e o domínio puro (`DetectInjection`). Não contêm nenhuma
dependência de PyMuPDF — apenas dados. Isso permite testar o detector com
documentos sintéticos, sem PDFs reais.
"""

from __future__ import annotations

import re
from collections import Counter

from pydantic import BaseModel

# (x0, y0, x1, y1) em pontos PDF.
BBox = tuple[float, float, float, float]
# Componentes RGB normalizados de 0.0 a 1.0.
Rgb = tuple[float, float, float]

# Fração mínima de imagem para considerar a página "dominada por imagem".
_IMAGE_PAGE_RATIO = 0.5

# Boilerplate (disclaimer/rodapé de modelo) = bloco que se repete em ≥ N páginas.
_BOILERPLATE_MIN_REPEAT = 3
# Comprimento mínimo p/ tratar um bloco repetido como boilerplate (evita remover
# rótulos curtos legítimos que por acaso se repitam).
_BOILERPLATE_MIN_LEN = 120


def _strip_repeated_blocks(groups: list[str]) -> list[str]:
    """Remove blocos de boilerplate que se repetem em várias páginas.

    Dois casos: (a) bloco PURO de boilerplate (idêntico em ≥3 páginas) → descartado;
    (b) boilerplate COLADO a conteúdo legítimo no mesmo bloco (ex.: disclaimer +
    "em face da PARTE REQUERIDA…") → remove só o trecho repetido, preserva o resto.
    """
    counts = Counter(groups)
    boiler = [
        g
        for g, c in counts.items()
        if c >= _BOILERPLATE_MIN_REPEAT and len(g) >= _BOILERPLATE_MIN_LEN
    ]
    if not boiler:
        return groups
    boiler.sort(key=len, reverse=True)  # remove os mais longos primeiro
    out: list[str] = []
    for g in groups:
        if g in boiler:  # bloco puro de boilerplate
            continue
        for bt in boiler:
            g = g.replace(bt, " ")  # boilerplate colado → tira só ele
        g = re.sub(r"\s{2,}", " ", g).strip()
        if g:
            out.append(g)
    return out


class TextSpan(BaseModel):
    """Um trecho contíguo de texto com seus atributos visuais."""

    model_config = {"frozen": True}

    text: str
    rgb: Rgb
    size: float  # tamanho da fonte em pontos
    bbox: BBox
    page: int  # índice da página (0-based)
    block: int = 0  # índice do bloco (parágrafo) na página — agrupa o texto por estrutura
    in_hidden_ocg: bool = False  # pertence a uma camada (OCG) desativada
    actual_text: str | None = None  # /ActualText associado (camada de acessibilidade)


class PageGeometry(BaseModel):
    """Geometria de uma página: o que é efetivamente visível (CropBox)."""

    model_config = {"frozen": True}

    page: int
    cropbox: BBox
    has_text: bool = True  # há texto extraível na página
    image_ratio: float = 0.0  # fração da página coberta por imagem (0..1)


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

    def visible_text(self, *, dedup_boilerplate: bool = False) -> str:
        """Texto que um humano de fato enxerga (exclui spans ocultos).

        Spans são agrupados por **bloco** (parágrafo): unidos por espaço dentro do
        bloco e por quebra de linha entre blocos. Isso preserva a estrutura do
        documento (endereçamento, título e qualificação ficam em parágrafos
        distintos) — sem o qual a anonimização de nomes "atravessaria" o título.

        Com `dedup_boilerplate=True`, remove cabeçalho/rodapé/disclaimer repetido por
        página (ex.: o aviso "MODELO" das petições-modelo, que reaparece em todo bloco
        de topo) — reduz tokens e ruído no envio ao LLM. Default False: a admissibilidade
        usa o texto íntegro.
        """
        from .detector import is_span_hidden  # import tardio: evita ciclo

        groups: list[str] = []
        current: list[str] = []
        current_key: tuple[int, int] | None = None
        for span in self.spans:
            if is_span_hidden(span, self):
                continue
            key = (span.page, span.block)
            if current and key != current_key:
                groups.append(" ".join(current))
                current = []
            current_key = key
            current.append(span.text)
        if current:
            groups.append(" ".join(current))
        if dedup_boilerplate:
            groups = _strip_repeated_blocks(groups)
        return "\n".join(groups)

    def image_only_pages(self) -> list[int]:
        """Páginas sem texto extraível mas cobertas por imagem (≥50%) — provável
        digitalização/escaneamento, onde a extração de texto não é confiável."""
        return [p.page for p in self.pages if not p.has_text and p.image_ratio >= _IMAGE_PAGE_RATIO]

    def image_heavy_pages(self) -> list[int]:
        """Páginas **mistas**: têm algum texto, mas uma imagem domina (≥50%) — pode
        haver conteúdo (texto embutido em imagem) que NÃO é extraído. A extração do
        texto disponível prossegue, mas o revisor deve ser avisado (requer OCR)."""
        return [p.page for p in self.pages if p.has_text and p.image_ratio >= _IMAGE_PAGE_RATIO]
