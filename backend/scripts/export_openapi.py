"""Exporta o schema OpenAPI da API do SHERPI para `docs/openapi.json`.

Gera o contrato versionado a partir da própria FastAPI (fonte de verdade), sem
subir o servidor nem tocar o banco — `app.openapi()` deriva o schema das rotas.

Uso: `make openapi` (ou `cd backend && PYTHONPATH=. uv run python scripts/export_openapi.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

from sherpi.interfaces.api.main import app

OUTPUT = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths = len(schema.get("paths", {}))
    print(f"OpenAPI {schema['info']['version']} -> {OUTPUT} ({paths} paths)")


if __name__ == "__main__":
    main()
