# Build stage — resolve dependências com uv (sem git, sem ferramentas de dev)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Runtime stage — imagem mínima sem o builder
FROM python:3.13-slim
WORKDIR /app

# Usuário não-root (princípio do mínimo privilégio)
RUN addgroup --system sherpi && adduser --system --ingroup sherpi sherpi

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY src/ src/

USER sherpi
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "sherpi.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
