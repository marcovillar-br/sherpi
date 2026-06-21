"""Normalização do texto antes do LLM (_normalize_input): menos tokens, sem perder mérito."""

from __future__ import annotations

from sherpi.contexts.petition_analysis.application.extract import _normalize_input


def test_removes_repeated_boilerplate_and_page_footers():
    text = "\n".join(
        [
            "MODELO AVISO este modelo e uma ferramenta para auxiliar cidadaos",
            "PETIÇÃO INICIAL",
            "Página 1 de 3",
            "MODELO AVISO este modelo e uma ferramenta para auxiliar cidadaos",
            "DOS FATOS conteudo unico da pagina dois",
            "Página 2 de 3",
            "MODELO AVISO este modelo e uma ferramenta para auxiliar cidadaos",
            "DOS PEDIDOS conteudo unico da pagina tres",
            "Página 3 de 3",
        ]
    )
    out = _normalize_input(text)
    assert "MODELO AVISO" not in out  # repetiu 3x → removido
    assert "Página" not in out  # "Página N de 3" agrupa por dígito → 3x → removido
    assert "PETIÇÃO INICIAL" in out  # conteúdo único preservado
    assert "DOS FATOS conteudo unico da pagina dois" in out
    assert "DOS PEDIDOS conteudo unico da pagina tres" in out


def test_collapses_excess_whitespace():
    assert _normalize_input("texto   com    espaços\n\n\n\nfim") == "texto com espaços\n\nfim"


def test_keeps_line_repeating_below_threshold():
    # 2 repetições (< 3) não são boilerplate — preservadas (evita falso-positivo).
    out = _normalize_input("linha repetida\núnica\nlinha repetida")
    assert out.count("linha repetida") == 2


def test_preserves_pii_placeholders():
    # roda sobre texto já anonimizado; marcadores não podem ser tocados.
    out = _normalize_input("PARTE REQUERENTE: [NOME_1] , CPF [CPF_1]")
    assert "[NOME_1]" in out and "[CPF_1]" in out
