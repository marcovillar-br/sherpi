# SHERPI — comandos de desenvolvimento
# Requer: docker, uv, npm
# Use sempre `uv run` — NÃO exporte o .env no shell; o uv/pydantic-settings lê automaticamente.

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help up down setup migrate seed-tpu tpu-catalog seed-tpu-cnj synthetic test lint typecheck eval dev-backend dev-backend-fake dev-frontend e2e

help:
	@echo "Comandos disponíveis:"
	@echo "  make up            Sobe o banco Postgres em container"
	@echo "  make down          Para o container do banco"
	@echo "  make setup         Setup completo: banco + migrations + TPU (uso único)"
	@echo "  make migrate       Roda as migrations Alembic"
	@echo "  make seed-tpu      Popula o índice TPU (seed sintético; Fake se sem extra ml)"
	@echo "  make tpu-catalog   Baixa a TUA real do CNJ (data/cnj/tpu_assuntos.json)"
	@echo "  make seed-tpu-cnj  Popula o índice TPU com a TUA real do CNJ (JurisBERT; extra ml)"
	@echo "  make synthetic     Gera o corpus sintético (data/synthetic/)"
	@echo "  make synthetic-from-template TEMPLATE=... [N=3]  Petições a partir de um .docx real (requer LibreOffice)"
	@echo "  make test          Roda a suite de testes"
	@echo "  make lint          ruff check + format --check"
	@echo "  make typecheck     mypy strict"
	@echo "  make eval          Eval harness (gate de CI; sai != 0 abaixo do limiar)"
	@echo "  make dev-backend       Inicia o backend (hot reload, LLM real)"
	@echo "  make dev-backend-fake  Inicia o backend com FakeProvider (sem tokens)"
	@echo "  make dev-frontend      Inicia o frontend (hot reload)"
	@echo "  make e2e               Roda testes E2E Playwright (requer dev-backend-fake)"
	@echo "  make e2e-llm           Roda testes de admissibilidade com LLM real (requer dev-backend)"

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

# TPU semântica com a tabela real do CNJ (ADR-0016). `uv run` reverte o ambiente, então
# o `--extra ml` precisa ir em CADA chamada — senão cai no FakeEmbeddingModel (com WARNING).
tpu-catalog:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run python scripts/fetch_tpu_cnj.py

seed-tpu-cnj: tpu-catalog
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run --extra ml python scripts/seed_tpu.py --source cnj

synthetic:
	cd $(BACKEND_DIR) && uv run python -m synthetic.generate

# Gera petições a partir dos templates reais (.docx) em docs/templates/.
# Requer LibreOffice (soffice) para o PDF. Use TEMPLATE=... e, opcionalmente, N=...
synthetic-from-template:
	cd $(BACKEND_DIR) && uv run python -m synthetic.from_template "$(TEMPLATE)" --n $(or $(N),3)

# --- Qualidade ---

test:
	cd $(BACKEND_DIR) && uv run pytest

lint:
	cd $(BACKEND_DIR) && uv run ruff check . && uv run ruff format --check .

typecheck:
	cd $(BACKEND_DIR) && uv run mypy src/ evals/

# Eval harness — gate de CI; sai com código != 0 se abaixo do limiar.
eval:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run python -m evals.run --ci

# --- Servidores ---

dev-backend:
	cd $(BACKEND_DIR) && uv run uvicorn sherpi.interfaces.api.main:app --reload --port 8000

# Backend sem LLM real — obrigatório para `make e2e` (zero custo de token)
dev-backend-fake:
	cd $(BACKEND_DIR) && SHERPI_LLM_BACKEND=fake uv run uvicorn sherpi.interfaces.api.main:app --reload --port 8000

dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev

# Testes E2E Playwright — valida veredito do firewall de todos os cenários sintéticos.
# Pré-requisito: `make dev-backend-fake` rodando em outro terminal.
e2e:
	cd $(FRONTEND_DIR) && npx playwright test

# Testes E2E com LLM real — valida semáforo de admissibilidade e liminar.
# Pré-requisito: `make dev-backend` rodando em outro terminal (consome tokens).
# ~8 cenários × 1 chamada LLM cada. Sem retry, sem loop.
e2e-llm:
	cd $(FRONTEND_DIR) && npx playwright test --config=playwright.llm.config.ts
