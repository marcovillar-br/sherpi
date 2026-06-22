# AGENTS.md — SHERPI

Contexto mínimo para agentes de IA a cada sessão. Conteúdo em **pt-BR**; nomes de arquivo em **en-US**.

## O que é

**SHERPI** — Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais. MVP acadêmico
(disciplina DAIA) de apoio à triagem de petições no Judiciário brasileiro. Fluxo central:
**firewall → extração → admissibilidade rito-aware → classificação TPU → ingestão assíncrona**,
com **identity/review/auditoria** e **observabilidade**. Sempre como **apoio à decisão humana**, nunca
decisão automática.

Documentação completa em [`docs/`](docs/) (índice: [`docs/INDEX.md`](docs/INDEX.md)). Arquitetura:
[`docs/tech-spec-sherpi.md`](docs/tech-spec-sherpi.md). Decisões: [`docs/adr/`](docs/adr/).

## Princípios inegociáveis (NÃO violar)

1. **Agnóstico a LLM.** Nunca chame um SDK de LLM diretamente nem faça hardcode de provider/modelo.
   Todo acesso a LLM passa pelo **port `LLMProvider`** (`shared_kernel/ports.py`); o provider vem da
   **config** (`SHERPI_LLM_BACKEND`). Default **Gemini Flash** (`google-genai`); adapters trocáveis
   **Grok (xAI)** e **Claude Sonnet (Anthropic)** — ambos via httpx, sem SDK (`infrastructure/llm/`,
   ADR-0011). Em testes, use **`FakeProvider`** (sem rede). Trocar de modelo = trocar um adapter, sem
   tocar no domínio.
2. **Domínio puro.** `domain/` não importa FastAPI, SQL, PyMuPDF nem SDK de LLM. Dependência externa =
   **port** (camada interna) + **adapter** (infraestrutura). Hexagonal/DDD.
3. **Human-in-the-loop.** Toda saída é sugestão auditável; jamais decisão automática (Res. CNJ 615/2025).
4. **Synthetic-first / LGPD.** Sem PII real. Dados de teste vêm do gerador sintético (`synthetic/`).
   Texto enviado a LLM externo passa pelo port `Anonymizer`. Nunca logar PII.
5. **Métrica medida, nunca prometida.** Acurácia (ex.: TPU, extração) é reportada pelo eval, não afirmada.
6. **Segredos fora do git.** Apenas `.env.example` é versionado; `.env` é local e ignorado.
7. **Custo×benefício primeiro.** Custo (tokens de LLM, tempo, memória, complexidade, manutenção) é
   variável de toda decisão — escolha o **melhor ROI**, não a opção mais "robusta" por reflexo. Antes de
   uma ação cara (muitas chamadas de LLM, jobs longos, refactors amplos), exponha o trade-off e a
   alternativa mais barata; faça o **diagnóstico gratuito primeiro**. LLM cobra **por token** (não por
   chamada) — em escala, use **batch** e o modelo mais barato que resolve.

## Escopo atual (Sprints 1–9 entregues — backend + frontend completo)

Entregue:
- `document_integrity` — firewall anti prompt-injection (PyMuPDF, 8 vetores)
- `petition_analysis` — extração + admissibilidade **rito-aware** (cível + trabalhista, CLT 840 §1º, ADR-0008)
- `identity` — auth JWT+bcrypt (pyjwt direto; passlib incompatível com bcrypt>=5), lockout, seed user
- `review` — AuditEvent append-only, RecordReview, GetCurrentUser dependency
- `taxonomy` — SuggestTpu (FakeEmbeddingModel hash SHA-256 + JurisbertEmbeddingModel), k-NN numpy/bytes
- `integration` — IngestPetitions + IngestQueue (asyncio) + SandboxSourceAdapter
- Observabilidade: structlog + CorrelationIdMiddleware + Sentry (soft-dep)
- LGPD: MappedRegexAnonymizer (reversível) + PresidioAnonymizer (extra `ner`)
- Dockerfile multi-stage, docker-compose.prod.yml, pip-audit gate real
- **UI (Sprint 8)**: página `/login`, seletor de rito, `TpuPanel` (top-3 + confiança + âncora), `ReviewPanel` (ACEITAR/CORRIGIR/REJEITAR + trilha append-only); Next.js 16 + React 19

Ver [`docs/roadmap.md`](docs/roadmap.md) e [`docs/backlog.md`](docs/backlog.md).

## Arquitetura e estrutura

Monólito modular DDD + hexagonal. Backend é o projeto Python (uv); frontend em Next.js 16 + React 19 (Sprint 8 completa).

```
backend/src/sherpi/
  shared_kernel/        # Value Objects (CPF, CNPJ, ClaimAmount, RiskVerdict, Rito) + ports transversais
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

Python ≥3.12 · FastAPI · uv · PyMuPDF · Pydantic v2 · SQLModel + Alembic · PostgreSQL ·
bcrypt + pyjwt (auth; **passlib não compatível com bcrypt>=5**) · structlog · sentry-sdk[fastapi] ·
google-genai (Gemini default) · Grok/Anthropic via httpx (sem SDK) · sentence-transformers (extra `ml`) · presidio (extra `ner`) ·
Next.js + TS (frontend) · Dockerfile multi-stage · pip-audit gate CI.

## Comandos (rodar em `backend/`)

```bash
uv sync                                # instala deps
uv run pytest                          # suíte completa (CI; pesada — evite no WSL)
make test-sliced                       # dev/WSL: fatiado por domínio (não derruba a sessão)
make test-domain D=taxonomy            # um domínio só
uv run ruff check . && uv run ruff format --check .
uv run mypy src/ evals/                # type check strict
uv run python -m evals.run --ci        # eval gate (firewall)
uv run python -m synthetic.generate    # gera data/synthetic/ (corpus rotulado)
docker compose up -d db                # PostgreSQL 16 (a partir da raiz)
```

## Convenções

Convenções completas e agnósticas a ferramenta em [`CONTRIBUTING.md`](CONTRIBUTING.md). Em resumo:

- **Idioma**: duas camadas — identificadores Python, constantes internas e chaves de dicionário em
  **en-US** (PEP 8); saída ao usuário, comentários Python e conteúdo de docs em **pt-BR**.
  Nomes de arquivo em `docs/` em **en-US** kebab-case. `trabalhista` é exceção de domínio (sem
  equivalente en-US limpo). Siglas: PMP (não PGP), WBS (não EAP). Detalhes em `CONTRIBUTING.md`.
- **Git**: **nunca** commite/push direto na **`development`** — toda mudança vai em **feature-branch**
  e entra na `development` **via PR** (onde o CI roda). **Base do PR é sempre `development`; nunca
  empilhe PR sobre outro feature-branch** (para dependências, serialize: mescle o pai, rebaseie o
  filho, abra o PR). O **merge `development → main` é do mantenedor** (não mergeie nem abra PR para
  `main` sem pedido). Push direto é bloqueado por *branch protection* + hook local (`.claude/hooks/`).
  Commits *conventional*, em pt-BR.
- **Uma PR por vez (serial por padrão).** NÃO abra nova branch enquanto houver PR aberto — espere o
  merge e parta da `development` atualizada. Arquivos de cruzamento (`Makefile`, `pyproject.toml`,
  `docs/adr/INDEX.md`, índices) são tocados por quase tudo, então branches paralelas colidem; só
  paralelize em arquivos disjuntos e, se inevitável, rebaseie na `development` antes do PR.
- **Definition of Done**: código + testes passando, `ruff`/`mypy` limpos, docs atualizadas, seção
  `[Não publicado]` do `CHANGELOG.md` atualizada (mudança notável); para modelos, métrica medida no
  eval. Tudo isso é gate de CI.
- **mypy strict.** PyMuPDF é sem tipos: relaxe apenas no adapter/ferramenta (override em `pyproject.toml`),
  nunca no domínio. Pacote `sherpi` tem `py.typed`.
- **Testes**: domínio puro e firewall sem rede; use `FakeProvider` para qualquer caminho com LLM.
  `synthetic`/`evals` são importáveis via `pythonpath = ["."]` (pytest).
- **Em dev/WSL, NÃO rode a suíte inteira** (`make test`/`uv run pytest`): o pico de recursos derruba a
  sessão. Use **`make test-sliced`** (um processo por domínio, com guarda de wall-clock) ou
  **`make test-domain D=<dir>`**. `pytest-timeout` (60s/teste, em `pyproject.toml`) corta testes
  pendurados. Não rode `make eval-tpu`/seed JurisBERT junto com pytest (torch disputa memória). O CI
  roda a suíte completa em infra própria.
- **Docs**: cada `.md` em `docs/` tem frontmatter YAML padronizado — gere/atualize via
  `scripts/add_frontmatter.py` (fonte de verdade dos metadados; rode após criar um doc novo).
- **Frontend (Next.js 16)**: a guarda de rota no edge usa a convenção **`proxy.ts`** (função `proxy`) —
  no Next 16 o antigo *Middleware* (`middleware.ts`/`middleware`) foi **renomeado para *Proxy*** e está
  **deprecado**. **NÃO** renomeie `frontend/src/proxy.ts` de volta para `middleware.ts`. O frontend é
  **desacoplado** (chama a API direto, cookie httpOnly) — **não é BFF**. Ver
  [`docs/adr/0017-frontend-decoupled-spa.md`](docs/adr/0017-frontend-decoupled-spa.md). Regra geral:
  antes de afirmar convenção de framework recente, confira a **versão instalada** + doc oficial (não
  decida por memória pré-cutoff).
