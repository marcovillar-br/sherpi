# SHERPI

**Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais.**

MVP acadêmico de IA aplicada ao Judiciário brasileiro que ataca três gargalos da triagem de
petições iniciais:

1. **Firewall anti *prompt-injection*** — detecta, de forma determinística e sem LLM, manipulações
   ocultas em PDFs (texto branco no branco, fonte microscópica, texto fora da área visível, Unicode
   invisível, `/ActualText` divergente, metadados e comandos de IA embutidos). É o diferencial do
   produto e a primeira barreira do fluxo.
2. **Extração estruturada + checagem de admissibilidade** — resume a petição e verifica os
   requisitos dos arts. 319/321 do CPC (extração via LLM + validadores determinísticos).
3. **Classificação taxonômica (TPU)** — sugere a classe/assunto do CNJ por similaridade semântica.

Tudo sob **supervisão humana obrigatória** (*human-in-the-loop*) e *synthetic-first* (sem PII real),
em conformidade com a Resolução CNJ 615/2025 e a LGPD.

> Projeto da disciplina **Desenvolvimento Ágil para Projetos de IA (DAIA)**.
> Origem e justificativa: [`docs/sherpi-deep-research-v1.md`](docs/sherpi-deep-research-v1.md).

## Arquitetura

Monólito modular orientado a **Domain-Driven Design** com **ports & adapters (hexagonal)**.
O domínio é puro; toda dependência externa (LLM, banco, parser de PDF, storage) é um *port* com
*adapter* trocável — é o que torna o sistema **agnóstico a LLM** (default Google Gemini Flash;
Maritaca Sabiá/OpenAI/Ollama como adapters).

| Bounded context | Papel | Status |
|---|---|---|
| `document_integrity` | Firewall anti *prompt-injection* (sem LLM) | ✅ Sprint 1 |
| `petition_analysis` | Extração + admissibilidade (**core domain**) | 🔵 Sprint 1–2 |
| `taxonomy` | Classificação TPU (embedding + k-NN) | ⚪ Futuro |
| `review` | *Human-in-the-loop* + auditoria | ⚪ Futuro |
| `identity` | Autenticação (perfil único) | ⚪ Futuro |

## Stack

- **Backend**: Python 3.12+ · FastAPI · uv · PyMuPDF · Pydantic · SQLModel + Alembic
- **Frontend**: Next.js + TypeScript + Tailwind + shadcn/ui + react-pdf (desacoplado da API)
- **Dados**: PostgreSQL + pgvector (relacional + embeddings TPU)
- **IA**: camada `LLMProvider` agnóstica · classificação TPU local (JurisBERT)
- **Infra**: Docker apenas para o banco; backend e frontend nativos em dev

## Estrutura do repositório

```
backend/     # API e domínio (DDD) — ver backend/README.md
frontend/    # UI Next.js (Sprint 2 — UI mínima)
docs/        # PRD, spec técnica, roadmap, mapa DDD, ADRs, modelo de ameaças
docker-compose.yml   # Postgres + pgvector
```

## Início rápido

```bash
# 1. Banco de dados (a partir da raiz)
docker compose up -d db

# 2. Backend
cd backend
uv sync
cp .env.example .env          # configure SHERPI_LLM_API_KEY, SHERPI_JWT_SECRET, etc.
uv run pytest                 # roda os testes
uv run python -m synthetic.generate   # gera o corpus sintético rotulado
```

Detalhes de comandos e estrutura do backend: [`backend/README.md`](backend/README.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/prd-sherpi.md`](docs/prd-sherpi.md) | Requisitos de produto, personas, métricas |
| [`docs/tech-spec-sherpi.md`](docs/tech-spec-sherpi.md) | Arquitetura, contratos, API, diagramas |
| [`docs/roadmap.md`](docs/roadmap.md) | MVP em 2 sprints, *Definition of Done*, visão de futuro |
| [`docs/pgp.md`](docs/pgp.md) · [`docs/eap.md`](docs/eap.md) · [`docs/backlog.md`](docs/backlog.md) | Gerenciamento de projeto: PGP, EAP/WBS e backlog (produto + sprints) |
| [`docs/agile-process.md`](docs/agile-process.md) | Papéis, Design Sprint, Kanban, cerimônias, retrospectivas |
| [`docs/ddd-context-map.md`](docs/ddd-context-map.md) | Mapa de contextos + linguagem ubíqua |
| [`docs/adr/`](docs/adr/) | Decisões de arquitetura (ADRs) |
| [`docs/threat-model.md`](docs/threat-model.md) · [`docs/security.md`](docs/security.md) | Segurança e confiabilidade |

## Roadmap (MVP em 2 sprints)

- **Sprint 1** — Fundações DDD + firewall ✅ + dados sintéticos ✅ + extração estruturada (LLM agnóstico)
- **Sprint 2** — Admissibilidade + orquestrador + persistência + UI mínima + eval → **MVP concluído**
- **Futuro (Fase 4)** — TPU, autenticação, auditoria, integração PJe/E-Proc, observabilidade, deploy

Detalhes: [`docs/roadmap.md`](docs/roadmap.md) · planejamento e papéis em [`docs/pgp.md`](docs/pgp.md), [`docs/eap.md`](docs/eap.md), [`docs/backlog.md`](docs/backlog.md), [`docs/agile-process.md`](docs/agile-process.md).
