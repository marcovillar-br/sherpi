"""`DetectInjection` — domain service puro do firewall anti prompt-injection.

Recebe um `ParsedDocument` (dados, sem PyMuPDF) e produz um `ForensicsReport`.
Determinístico e sem efeitos colaterais: a mesma entrada gera sempre o mesmo
laudo. Toda a lógica de segurança vive aqui e é exaustivamente testável com
documentos sintéticos.

Princípio de defesa em profundidade: este firewall é heurístico (não pega
100%). A segunda camada é o *defensive prompting* na extração (texto como dado,
não instrução) — ver contexto petition_analysis.
"""

from __future__ import annotations

from .document import ParsedDocument, TextSpan
from .report import Anomaly, AnomalyType, ForensicsReport, Severity

# --- Limiares de detecção ---
_NEAR_WHITE = 0.92  # canais RGB acima disso = praticamente branco
_MIN_VISIBLE_SIZE = 1.0  # fontes < 1pt são consideradas invisíveis
_COLOR_BG_DELTA = 0.06  # distância máx. p/ considerar texto da cor do fundo

# Caracteres Unicode de largura zero / invisíveis.
_ZERO_WIDTH = {
    "​",  # zero width space
    "‌",  # zero width non-joiner
    "‍",  # zero width joiner
    "⁠",  # word joiner
    "﻿",  # zero width no-break space (BOM)
    "­",  # soft hyphen
}

# Frases imperativas típicas de injeção contra IA judicial (pt/en).
_INJECTION_PHRASES = (
    "ignore as instruções",
    "ignore todas as instruções",
    "desconsidere as instruções",
    "ignore previous",
    "ignore all previous",
    "disregard",
    "system prompt",
    "você deve",
    "conceda",
    "defira",
    "resuma favoravelmente",
    "decida a favor",
    "julgue procedente",
    "conceda a gratuidade",
    "conceda a liminar",
    "as a language model",
    "assistant:",
)


def _is_near_white(rgb: tuple[float, float, float]) -> bool:
    return all(c >= _NEAR_WHITE for c in rgb)


def is_span_hidden(span: TextSpan, doc: ParsedDocument) -> bool:
    """Heurística unificada de invisibilidade de um span (usada também por
    `ParsedDocument.visible_text`)."""
    return (
        span.in_hidden_ocg
        or span.size < _MIN_VISIBLE_SIZE
        or _is_near_white(span.rgb)
        or _is_off_cropbox(span, doc)
    )


def _page_cropbox(doc: ParsedDocument, page: int) -> tuple[float, float, float, float] | None:
    for geo in doc.pages:
        if geo.page == page:
            return geo.cropbox
    return None


def _is_off_cropbox(span: TextSpan, doc: ParsedDocument) -> bool:
    box = _page_cropbox(doc, span.page)
    if box is None:
        return False
    cx0, cy0, cx1, cy1 = box
    x0, y0, x1, y1 = span.bbox
    # Totalmente fora da área visível (com pequena tolerância).
    tol = 1.0
    return x1 < cx0 - tol or x0 > cx1 + tol or y1 < cy0 - tol or y0 > cy1 + tol


def _has_zero_width(text: str) -> bool:
    return any(ch in _ZERO_WIDTH for ch in text)


def _contains_injection(text: str) -> bool:
    low = text.lower()
    return any(phrase in low for phrase in _INJECTION_PHRASES)


def _truncate(text: str, limit: int = 120) -> str:
    clean = text.strip().replace("\n", " ")
    return clean if len(clean) <= limit else clean[:limit] + "…"


class DetectInjection:
    """Domain service: inspeciona um documento e emite o laudo forense."""

    def run(self, doc: ParsedDocument) -> ForensicsReport:
        anomalies: list[Anomaly] = []

        for span in doc.spans:
            anomalies.extend(self._inspect_span(span, doc))

        anomalies.extend(self._inspect_metadata(doc))
        return ForensicsReport.from_anomalies(anomalies)

    def _inspect_span(self, span: TextSpan, doc: ParsedDocument) -> list[Anomaly]:
        found: list[Anomaly] = []
        text_has_content = bool(span.text.strip())
        hidden = is_span_hidden(span, doc)

        # 1. Branco no branco
        if text_has_content and _is_near_white(span.rgb):
            found.append(
                Anomaly(
                    type=AnomalyType.WHITE_ON_WHITE,
                    severity=Severity.HIGH,
                    detail="Texto com cor praticamente branca (invisível ao leitor humano).",
                    page=span.page,
                    evidence=_truncate(span.text),
                )
            )

        # 2. Fonte microscópica
        if text_has_content and span.size < _MIN_VISIBLE_SIZE:
            found.append(
                Anomaly(
                    type=AnomalyType.TINY_FONT,
                    severity=Severity.HIGH,
                    detail=f"Fonte de {span.size:.2f}pt, abaixo do limiar de visibilidade.",
                    page=span.page,
                    evidence=_truncate(span.text),
                )
            )

        # 3. Fora da CropBox
        if text_has_content and _is_off_cropbox(span, doc):
            found.append(
                Anomaly(
                    type=AnomalyType.OFF_CROPBOX,
                    severity=Severity.HIGH,
                    detail="Texto posicionado fora da área visível da página (CropBox).",
                    page=span.page,
                    evidence=_truncate(span.text),
                )
            )

        # 4. Camada OCG oculta
        if text_has_content and span.in_hidden_ocg:
            found.append(
                Anomaly(
                    type=AnomalyType.HIDDEN_OCG_LAYER,
                    severity=Severity.MEDIUM,
                    detail="Texto em camada de conteúdo opcional (OCG) desativada.",
                    page=span.page,
                    evidence=_truncate(span.text),
                )
            )

        # 5. Unicode de largura zero
        if _has_zero_width(span.text):
            found.append(
                Anomaly(
                    type=AnomalyType.ZERO_WIDTH_UNICODE,
                    severity=Severity.MEDIUM,
                    detail="Presença de caracteres Unicode invisíveis (largura zero).",
                    page=span.page,
                    evidence=_truncate(span.text),
                )
            )

        # 6. /ActualText divergente do texto renderizado
        if span.actual_text is not None and span.actual_text.strip() != span.text.strip():
            found.append(
                Anomaly(
                    type=AnomalyType.ACTUALTEXT_DIVERGENCE,
                    severity=Severity.HIGH,
                    detail="/ActualText diverge do texto visível (acessibilidade abusada).",
                    page=span.page,
                    evidence=_truncate(f"visível={span.text!r} actual={span.actual_text!r}"),
                )
            )

        # 7. Comando à IA em texto OCULTO (eleva a CRITICAL)
        target = f"{span.text} {span.actual_text or ''}"
        if hidden and _contains_injection(target):
            found.append(
                Anomaly(
                    type=AnomalyType.INJECTION_KEYWORDS,
                    severity=Severity.CRITICAL,
                    detail="Comando imperativo direcionado a IA embutido em texto oculto.",
                    page=span.page,
                    evidence=_truncate(target),
                )
            )

        return found

    def _inspect_metadata(self, doc: ParsedDocument) -> list[Anomaly]:
        found: list[Anomaly] = []
        for key, value in doc.metadata.items():
            if value and _contains_injection(value):
                found.append(
                    Anomaly(
                        type=AnomalyType.SUSPICIOUS_METADATA,
                        severity=Severity.HIGH,
                        detail=f"Comando imperativo embutido no metadado '{key}'.",
                        evidence=_truncate(value),
                    )
                )
        return found
