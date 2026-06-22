"""Anonymizer com NER de nomes via Presidio (LGPD Fase 4).

Quando usado pela factory na variante mapeada, o masking é reversível →
**pseudonimização** (art. 5º XI), não anonimização (ver ADR-0012).
Requer `uv sync --extra ner` e `python -m spacy download pt_core_news_sm`.
Em produção substitui `RegexAnonymizer` adicionando detecção de nomes próprios.
"""

from __future__ import annotations


class PresidioAnonymizer:
    """Anonymizer com NER de nomes via Presidio + spaCy.

    Implementa o port `Anonymizer`. Lança `ImportError` se as dependências
    opcionais não estiverem instaladas.
    """

    def __init__(self) -> None:
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
        except ImportError as exc:
            raise ImportError(
                "Instale com `uv sync --extra ner` e `python -m spacy download pt_core_news_sm`"
            ) from exc
        self._analyzer = AnalyzerEngine()
        self._engine = AnonymizerEngine()

    def anonymize(self, text: str) -> str:
        from presidio_anonymizer.entities import OperatorConfig

        results = self._analyzer.analyze(text=text, language="pt")
        anonymized = self._engine.anonymize(
            text=text,
            analyzer_results=results,
            operators={"DEFAULT": OperatorConfig("replace", {"new_value": "[NOME]"})},
        )
        return anonymized.text  # type: ignore[no-any-return]
