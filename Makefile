# SHERPI — comandos de desenvolvimento
# Requer: docker, uv, npm
# Use sempre `uv run` — NÃO exporte o .env no shell; o uv/pydantic-settings lê automaticamente.

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help up down setup migrate seed-tpu synthetic test lint typecheck dev-backend dev-frontend

help:
	@echo "Comandos disponíveis:"
	@echo "  make up            Sobe o banco Postgres em container"
	@echo "  make down          Para o container do banco"
	@echo "  make setup         Setup completo: banco + migrations + TPU (uso único)"
	@echo "  make migrate       Roda as migrations Alembic"
	@echo "  make seed-tpu      Popula o índice TPU no banco"
	@echo "  make synthetic     Gera o corpus sintético (data/synthetic/)"
	@echo "  make test          Roda a suite de testes"
	@echo "  make lint          ruff check + format --check"
	@echo "  make typecheck     mypy strict"
	@echo "  make dev-backend   Inicia o backend (hot reload)"
	@echo "  make dev-frontend  Inicia o frontend (hot reload)"

# --- Banco ---

up:
	docker compose up -d db
	@echo "Aguardando Postgres ficar pronto..."
	@until docker compose exec db pg_isready -U sherpi -d sherpi -q; do sleep 1; done
	@echo "Postgres pronto."

down:
	docker compose stop db

# --- Setup inicial ---

setup: up migrate seed-tpu synthetic
	@echo ""
	@echo "Setup concluído. Inicie o backend com:  make dev-backend"
	@echo "Inicie o frontend com:                  make dev-frontend"

migrate:
	cd $(BACKEND_DIR) && uv run alembic upgrade head

seed-tpu:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run python scripts/seed_tpu.py

synthetic:
	cd $(BACKEND_DIR) && uv run python -m synthetic.generate

# --- Qualidade ---

test:
	cd $(BACKEND_DIR) && uv run pytest

lint:
	cd $(BACKEND_DIR) && uv run ruff check . && uv run ruff format --check .

typecheck:
	cd $(BACKEND_DIR) && uv run mypy src/ evals/

# --- Servidores ---

dev-backend:
	cd $(BACKEND_DIR) && uv run uvicorn sherpi.interfaces.api.main:app --reload --port 8000

dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev
