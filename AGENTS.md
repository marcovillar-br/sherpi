# AGENTS.md — SHERPI

Contexto mínimo para agentes de IA a cada sessão. Conteúdo em **pt-BR**; nomes de arquivo em **en-US**.

## O que é

**SHERPI** — Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais. MVP acadêmico
(disciplina DAIA) de apoio à triagem de petições no Judiciário brasileiro. Fluxo central:
**firewall anti prompt-injection → extração estruturada → checagem de admissibilidade** (e, no futuro,
classificação TPU). Sempre como **apoio à decisão humana**, nunca decisão automática.

Documentação completa em [`docs/`](docs/) (índice: [`docs/INDEX.md`](docs/INDEX.md)). Arquitetura:
[`docs/tech-spec-sherpi.md`](docs/tech-spec-sherpi.md). Decisões: [`docs/adr/`](docs/adr/).

## Princípios inegociáveis (NÃO violar)

1. **Agnóstico a LLM.** Nunca chame um SDK de LLM diretamente nem faça hardcode de provider/modelo.
   Todo acesso a LLM passa pelo **port `LLMProvider`** (`shared_kernel/ports.py`); o provider vem da
   **config** (`SHERPI_LLM_BACKEND`). Default **Gemini Flash**; adapters: Maritaca Sabiá / OpenAI /
   Ollama (`infrastructure/llm/`). Em testes, use **`FakeProvider`** (sem rede). Trocar de modelo =
   trocar um adapter, sem tocar no domínio.
2. **Domínio puro.** `domain/` não importa FastAPI, SQL, PyMuPDF nem SDK de LLM. Dependência externa =
   **port** (camada interna) + **adapter** (infraestrutura). Hexagonal/DDD.
3. **Human-in-the-loop.** Toda saída é sugestão auditável; jamais decisão automática (Res. CNJ 615/2025).
4. **Synthetic-first / LGPD.** Sem PII real. Dados de teste vêm do gerador sintético (`synthetic/`).
   Texto enviado a LLM externo passa pelo port `Anonymizer`. Nunca logar PII.
5. **Métrica medida, nunca prometida.** Acurácia (ex.: TPU, extração) é reportada pelo eval, não afirmada.
6. **Segredos fora do git.** Apenas `.env.example` é versionado; `.env` é local e ignorado.

## Escopo atual (MVP — 2 sprints)

Em escopo: `document_integrity` (✅ firewall), `petition_analysis` (extração + admissibilidade),
orquestração, persistência, UI mínima. **Futuro (Fase 4):** `taxonomy` (TPU), `identity` (auth),
`review` (auditoria), integração PJe. Ver [`docs/roadmap.md`](docs/roadmap.md) e
[`docs/backlog.md`](docs/backlog.md). Não implemente itens "Futuro" sem pedido explícito.

## Arquitetura e estrutura

Monólito modular DDD + hexagonal. Backend é o projeto Python (uv); frontend será Next.js separado.

```
backend/src/sherpi/
  shared_kernel/        # Value Objects (CPF, CNPJ, ValorCausa, RiskVerdict) + ports transversais
  contexts/<ctx>/{domain,application,infrastructure}   # bounded contexts
  application/          # orquestrador cross-context (analyze_petition)
  infrastructure/{llm,persistence,storage}             # adapters
  interfaces/api/       # FastAPI (driving adapter)
backend/synthetic/      # gerador de PDFs sintéticos (dev/eval — fora do pacote)
backend/evals/          # eval harness (gate de CI)
backend/tests/          # pytest (espelha os contextos)
docs/                   # PRD, spec, roadmap, PGP, EAP, backlog, ADRs, segurança
```

## Stack

Python ≥3.12 · FastAPI · uv · PyMuPDF · Pydantic v2 · SQLModel + Alembic · PostgreSQL + pgvector ·
google-genai (default) / openai (compat) · Next.js + TS (frontend) · Docker só para o banco.

## Comandos (rodar em `backend/`)

```bash
uv sync                                # instala deps
uv run pytest                          # testes (sem rede — usa FakeProvider)
uv run ruff check . && uv run ruff format --check .
uv run mypy src/ evals/                # type check strict
uv run python -m evals.run --ci        # eval gate (firewall)
uv run python -m synthetic.generate    # gera data/synthetic/ (corpus rotulado)
docker compose up -d db                # Postgres+pgvector (a partir da raiz)
```

## Convenções

- **Definition of Done**: código + testes passando, `ruff`/`mypy` limpos, docs atualizadas; para
  modelos, métrica medida no eval. Tudo isso é gate de CI.
- **mypy strict.** PyMuPDF é sem tipos: relaxe apenas no adapter/ferramenta (override em `pyproject.toml`),
  nunca no domínio. Pacote `sherpi` tem `py.typed`.
- **Testes**: domínio puro e firewall sem rede; use `FakeProvider` para qualquer caminho com LLM.
  `synthetic`/`evals` são importáveis via `pythonpath = ["."]` (pytest).
- **Git**: trabalhe na branch `development`. Commits no estilo *conventional* (`feat:`, `docs:`,
  `chore:`...), em pt-BR, escopados por assunto.
- **Docs**: cada `.md` em `docs/` tem frontmatter YAML padronizado — gere/atualize via
  `scripts/add_frontmatter.py` (fonte de verdade dos metadados; rode após criar um doc novo).
