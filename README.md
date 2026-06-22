# SHERPI

**Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais.**

MVP acadêmico de IA aplicada ao Judiciário brasileiro que ataca três gargalos da triagem de
petições iniciais:

1. **Firewall anti *prompt-injection*** — detecta, de forma determinística e sem LLM, manipulações
   ocultas em **PDF e DOCX** (texto branco no branco, fonte microscópica, texto fora da área visível,
   Unicode invisível, `/ActualText`, metadados, e no DOCX o atributo `w:vanish` — útil para validar a
   peça **antes** de gerar o PDF). Também sinaliza PDFs **sem camada de texto** (imagem/escaneado), que
   não seguem para o LLM. É o diferencial do produto e a primeira barreira do fluxo.
2. **Extração estruturada + checagem de admissibilidade *rito-aware*** — resume a petição e verifica
   os requisitos por rito: arts. 319/321 do CPC no cível e CLT art. 840 §1º (pedido líquido) no
   trabalhista (extração via LLM + validadores determinísticos).
3. **Classificação taxonômica (TPU)** — sugere a classe/assunto do CNJ por similaridade semântica.

Tudo sob **supervisão humana obrigatória** (*human-in-the-loop*) e *synthetic-first* (sem PII real),
em conformidade com a Resolução CNJ 615/2025 e a LGPD.

> Projeto da disciplina **Desenvolvimento Ágil para Projetos de IA (DAIA)**.
> Origem e justificativa: [`docs/archive/sherpi-deep-research-v1.md`](docs/archive/sherpi-deep-research-v1.md).

## Arquitetura

Monólito modular orientado a **Domain-Driven Design** com **ports & adapters (hexagonal)**.
O domínio é puro; toda dependência externa (LLM, banco, parser de PDF, storage) é um *port* com
*adapter* trocável — é o que torna o sistema **agnóstico a LLM** (default Google Gemini Flash;
**Grok (xAI)** e **Claude Sonnet (Anthropic)** como adapters trocáveis por configuração).

| Bounded context | Papel | Status |
|---|---|---|
| `document_integrity` | Firewall anti *prompt-injection* (sem LLM) | ✅ Sprint 1 |
| `petition_analysis` | Extração + admissibilidade **rito-aware** (**core domain**) | ✅ Sprint 1–3 |
| `identity` | Autenticação JWT (perfil único) | ✅ Sprint 4 · UI Sprint 8 |
| `review` | *Human-in-the-loop* + auditoria append-only | ✅ Sprint 4 · UI Sprint 8 |
| `taxonomy` | Classificação TPU (embedding + k-NN) | ✅ Sprint 5 · UI Sprint 8 |
| `integration` | Ingestão assíncrona de petições (PJe/E-Proc/sandbox) | ✅ Sprint 7 (backend; sem UI) |

## Stack

- **Backend**: Python ≥3.12 · FastAPI · uv · PyMuPDF (PDF) + python-docx (DOCX) · Pydantic v2 · SQLModel + Alembic
- **Auth**: bcrypt + pyjwt (passlib incompatível com bcrypt>=5) · OAuth2 password flow
- **Observabilidade**: structlog · correlation ID · Sentry (soft-dep)
- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind v4 (desacoplado da API)
- **Dados**: PostgreSQL + SQLModel · embeddings como bytes (numpy/float32, sem pgvector extension)
- **IA**: camada `LLMProvider` agnóstica · classificação TPU local (JurisBERT ou FakeEmbeddingModel)
- **Infra**: Dockerfile multi-stage (non-root) · docker-compose.prod.yml · pip-audit gate real

## Estrutura do repositório

```
backend/     # API e domínio (DDD) — ver backend/README.md
frontend/    # UI Next.js completa (login, análise, TPU, revisão, histórico, auditoria de LLM)
docs/        # PRD, spec técnica, roadmap, mapa DDD, ADRs, modelo de ameaças
docker-compose.yml       # PostgreSQL 16 (dev: só o banco)
docker-compose.prod.yml  # Postgres + backend (produção)
Makefile                 # orquestra setup, dev, testes (ver "Início rápido")
```

## Início rápido

O `Makefile` (na raiz) orquestra tudo. Requer `docker`, `uv` e `npm`.

```bash
# 1. Configure o ambiente do backend
cp backend/.env.example backend/.env   # ajuste SHERPI_LLM_API_KEY, SHERPI_JWT_SECRET

# 2. Setup completo (banco + migrations + índice TPU + corpus sintético)
make setup

# 3. Suba os serviços (em terminais separados)
make dev-backend       # LLM real  (ou: make dev-backend-fake — sem custo de token)
make dev-frontend

# Testes
make test              # backend (pytest)
make e2e               # E2E Playwright (requer `make dev-backend-fake` rodando)
```

Lista completa de alvos: `make help`. Detalhes do backend: [`backend/README.md`](backend/README.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/prd-sherpi.md`](docs/prd-sherpi.md) | Requisitos de produto, personas, métricas |
| [`docs/tech-spec-sherpi.md`](docs/tech-spec-sherpi.md) | Arquitetura, contratos, API, diagramas |
| [`docs/c4-model.md`](docs/c4-model.md) | Modelo C4 (Contexto → Contêineres → Componentes → Código) |
| [`docs/roadmap.md`](docs/roadmap.md) | Sprints (MVP + Fase 4), *Definition of Done*, visão de futuro |
| [`docs/pmp.md`](docs/pmp.md) · [`docs/wbs.md`](docs/wbs.md) · [`docs/backlog.md`](docs/backlog.md) | Gerenciamento de projeto: PGP, EAP/WBS e backlog (produto + sprints) |
| [`docs/agile-process.md`](docs/agile-process.md) | Papéis, Design Sprint, Kanban, cerimônias, retrospectivas |
| [`docs/ddd-context-map.md`](docs/ddd-context-map.md) | Mapa de contextos + linguagem ubíqua |
| [`docs/adr/`](docs/adr/) | Decisões de arquitetura (ADRs) |
| [`docs/threat-model.md`](docs/threat-model.md) · [`docs/security.md`](docs/security.md) | Segurança e confiabilidade |

## Roadmap

- **Sprint 1** ✅ — Fundações DDD + firewall + dados sintéticos + extração estruturada (LLM agnóstico)
- **Sprint 2** ✅ — Admissibilidade + orquestrador + persistência + UI mínima + eval → **MVP concluído**
- **Sprint 3** ✅ — **Domínio Trabalhista (CLT 840) + arquitetura rito-aware** (foco do grupo)
- **Sprint 4** ✅ — Confiança & Conformidade: autenticação JWT + revisão/auditoria append-only
- **Sprint 5** ✅ — Classificação TPU por ramo (JurisBERT + k-NN/numpy)
- **Sprint 6** ✅ — Produção: structlog + correlation ID, LGPD (anonimização de PII + retenção), Dockerfile, pip-audit gate
- **Sprint 7** ✅ — Integração PJe/E-Proc: ingestão assíncrona (asyncio.Queue + SandboxSourceAdapter)
- **Sprint 8** ✅ — UI das Sprints 4–7: login, seletor de rito, TPU top-3, revisão humana (Next.js 16)
- **Sprint 9** ✅ — Refactor de nomenclatura en-US (EP12): identificadores Python pt-BR → en-US (campos e enums; classes de domínio mantêm pt-BR pela regra de duas camadas)
- **Refinamentos contínuos** ✅ — TPU 1.0 sobre a TUA real do CNJ (ranking híbrido + limiar de confiança, [ADR-0016](docs/adr/0016-cnj-tua-real-catalog-tpu.md)); anonimização de nomes por default; detecção de PDF imagem/escaneado; adapters Grok/Anthropic
- **Domínios adicionais** (pós rito-aware) — previdenciário/INSS, execução fiscal, família/JEC

Detalhes: [`docs/roadmap.md`](docs/roadmap.md) · planejamento e papéis em [`docs/pmp.md`](docs/pmp.md), [`docs/wbs.md`](docs/wbs.md), [`docs/backlog.md`](docs/backlog.md), [`docs/agile-process.md`](docs/agile-process.md).

## Licença

Distribuído sob a licença **Apache-2.0** — ver [`LICENSE`](LICENSE).
