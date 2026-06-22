# SHERPI — comandos de desenvolvimento
# Requer: docker, uv, npm
# Use sempre `uv run` — NÃO exporte o .env no shell; o uv/pydantic-settings lê automaticamente.

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help up down setup migrate seed-tpu tpu-catalog seed-tpu-cnj synthetic test test-sliced test-domain lint typecheck openapi eval eval-tpu dev-backend dev-backend-fake dev-frontend e2e

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
	@echo "  make test          Roda a suite completa (CI; pesada — evite no WSL)"
	@echo "  make test-sliced   Suíte fatiada por domínio (recomendada em dev/WSL)"
	@echo "  make test-domain D=taxonomy   Roda só um domínio (tests/<D>)"
	@echo "  make lint          ruff check + format --check"
	@echo "  make typecheck     mypy strict"
	@echo "  make eval          Eval harness (gate de CI; sai != 0 abaixo do limiar)"
	@echo "  make eval-tpu      Eval rotulado da TPU sobre a TUA real (JurisBERT; extra ml)"
	@echo "  make dev-backend       Inicia o backend (hot reload, LLM real + TPU JurisBERT)"
	@echo "  make dev-backend-fake  Inicia o backend com FakeProvider (sem tokens, sem ML)"
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

# Suíte FATIADA por domínio — recomendada em dev/WSL: cada domínio roda num processo
# pytest separado (memória liberada entre fatias) com guarda de wall-clock por fatia.
# Evita o pico de recursos que derruba a sessão ao rodar tudo de uma vez.
#   make test-sliced                 # todas as fatias
#   make test-domain D=taxonomy      # apenas um domínio
test-sliced:
	cd $(BACKEND_DIR) && bash scripts/run_tests_sliced.sh

test-domain:
	cd $(BACKEND_DIR) && timeout 180 uv run pytest tests/$(D) -q

lint:
	cd $(BACKEND_DIR) && uv run ruff check . && uv run ruff format --check .

typecheck:
	cd $(BACKEND_DIR) && uv run mypy src/ evals/

# Exporta o contrato OpenAPI versionado para docs/openapi.json (deriva das rotas; sem subir o servidor).
openapi:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run python scripts/export_openapi.py

# Eval harness — gate de CI; sai com código != 0 se abaixo do limiar.
eval:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run python -m evals.run --ci

# Eval rotulado da TPU sobre a TUA real do CNJ (ADR-0016) — requer extra ml + catálogo.
# Não é gate de CI (precisa de JurisBERT); use para medir acurácia top-1/3/5.
eval-tpu: tpu-catalog
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run --extra ml python -m evals.tpu_labeled

# --- Servidores ---

# `--extra ml` para a TPU semântica (JurisBERT): `uv run` reverte o ambiente, então o
# extra precisa ir AQUI — senão o embedder cai no Fake (64-dim), não casa com o índice
# JurisBERT (768) e a TPU é desabilitada. Veja backend/README (TPU semântica).
dev-backend:
	cd $(BACKEND_DIR) && PYTHONPATH=. uv run --extra ml uvicorn sherpi.interfaces.api.main:app --reload --port 8000

# Backend sem LLM real — obrigatório para `make e2e` (zero custo de token). SEM `--extra ml`:
# o e2e valida o firewall, não a TPU; evita carregar torch (~2 GB) à toa.
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
