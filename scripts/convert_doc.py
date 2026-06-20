#!/usr/bin/env python3
"""Converte documentos com base na extensão de entrada e saída.

Uso:
    python convert_doc.py input.md output.pdf
    python convert_doc.py input.md output.docx
    python convert_doc.py input.md output.html
"""

import argparse
import subprocess
import sys
from pathlib import Path


SUPPORTED = {
    (".md", ".pdf"),
    (".md", ".docx"),
    (".md", ".html"),
    (".html", ".pdf"),
    (".html", ".docx"),
    (".docx", ".pdf"),
}

PANDOC_FORMATS = {
    ".md": "markdown",
    ".html": "html",
    ".docx": "docx",
}


def convert_to_pdf_weasyprint(input_path: Path, output_path: Path, orientation: str = "portrait") -> None:
    from weasyprint import HTML
    import markdown

    suffix = input_path.suffix.lower()
    if suffix == ".md":
        html = markdown.markdown(
            input_path.read_text(encoding="utf-8"),
            extensions=["tables", "fenced_code", "nl2br"],
        )
    elif suffix == ".html":
        html = input_path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"weasyprint não suporta entrada {suffix}")

    styled = f"""
    <style>
      @page {{ size: A4 {orientation}; margin: 1cm; }}
      body {{ font-family: sans-serif; font-size: 12px; margin: 0; }}
      table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
      th, td {{ border: 1px solid #888; padding: 6px 10px; text-align: left; }}
      th {{ background: #f0f0f0; font-weight: bold; }}
      tr:nth-child(even) {{ background: #fafafa; }}
      code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
      pre {{ background: #f4f4f4; padding: 1em; border-radius: 4px; }}
    </style>
    {html}
    """
    HTML(string=styled, base_url=str(input_path.parent)).write_pdf(str(output_path))


def convert_via_pandoc(input_path: Path, output_path: Path) -> None:
    from_fmt = PANDOC_FORMATS.get(input_path.suffix.lower())
    cmd = ["pandoc", str(input_path), "-o", str(output_path)]
    if from_fmt:
        cmd += ["-f", from_fmt]
    subprocess.run(cmd, check=True)


def convert(input_path: Path, output_path: Path, orientation: str = "portrait") -> None:
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower()

    if (in_ext, out_ext) not in SUPPORTED:
        supported_str = ", ".join(f"{a}→{b}" for a, b in sorted(SUPPORTED))
        print(f"Erro: conversão {in_ext}→{out_ext} não suportada.")
        print(f"Pares suportados: {supported_str}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if out_ext == ".pdf" and in_ext in (".md", ".html"):
        convert_to_pdf_weasyprint(input_path, output_path, orientation)
    else:
        convert_via_pandoc(input_path, output_path)

    print(f"Convertido: {input_path} → {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte documentos por extensão.")
    parser.add_argument("input", type=Path, help="Arquivo de entrada")
    parser.add_argument("output", type=Path, help="Arquivo de saída")
    parser.add_argument(
        "--orientation",
        choices=["portrait", "landscape"],
        default="portrait",
        help="Orientação do PDF (default: portrait). Ignorado para DOCX/HTML.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Erro: arquivo de entrada não encontrado: {args.input}")
        sys.exit(1)

    convert(args.input, args.output, args.orientation)


if __name__ == "__main__":
    main()
