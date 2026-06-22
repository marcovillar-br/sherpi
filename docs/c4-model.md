---
title: "Modelo C4 — Arquitetura do SHERPI"
description: "Arquitetura do SHERPI nos quatro níveis do modelo C4 (Contexto, Contêineres, Componentes e Código), refletindo a implementação atual."
doc_type: architecture
project: SHERPI
status: reference
version: 1.0
updated: 2026-06-22
language: pt-BR
tags: [arquitetura, c4, ddd, hexagonal, diagramas]
---

# Modelo C4 — SHERPI

Visão da arquitetura do SHERPI pelos quatro níveis do **modelo C4** (Simon Brown): do mais
abstrato (Contexto) ao mais concreto (Código). Os diagramas refletem o **estado implementado**
(Sprints 1–9), não uma visão aspiracional — em caso de divergência, vale o código.

Complementa, sem repetir:
- [`tech-spec-sherpi.md`](tech-spec-sherpi.md) — contratos das capacidades, camada LLM, API;
- [`ddd-context-map.md`](ddd-context-map.md) — relações upstream/downstream entre contextos e linguagem ubíqua;
- [`adr/`](adr/) — as decisões que justificam cada escolha.

> **Convenção de leitura.** O sistema é um **monólito modular DDD** com **ports & adapters
> (hexagonal)**: o domínio é puro e toda dependência externa (LLM, banco, parser de PDF, embeddings)
> entra por um *port* implementado como *adapter* trocável. É o que o torna **agnóstico a LLM**.

---

## Nível 1 — Contexto do sistema

Quem usa o SHERPI e com quais sistemas externos ele conversa.

```mermaid
C4Context
    title Nível 1 — Contexto do sistema (SHERPI)

    Person(assessor, "Assessor de Triagem", "Servidor do Judiciario que tria peticoes iniciais sob supervisao humana obrigatoria (perfil unico, autenticado por JWT)")

    System(sherpi, "SHERPI", "Extrai, resume e classifica peticoes iniciais; firewall anti prompt-injection; admissibilidade rito-aware; sugestao de TPU")

    System_Ext(llm, "Provedor de LLM", "Gemini 2.5 Flash (default), Grok 4 (xAI) ou Claude Sonnet 4.6 (Anthropic) - trocavel por configuracao")
    System_Ext(tribunais, "Tribunais (PJe / E-Proc)", "Ingestao assincrona de peticoes - hoje via SandboxSourceAdapter (simulado)")
    System_Ext(sentry, "Sentry", "Observabilidade / captura de erros (dependencia opcional)")

    Rel(assessor, sherpi, "Envia peticao, revisa resumo e decide", "HTTPS")
    Rel(sherpi, llm, "Extrai dados estruturados com texto pseudonimizado", "HTTPS/JSON")
    Rel(tribunais, sherpi, "Disponibiliza peticoes para ingestao", "fonte de ingestao")
    Rel(sherpi, sentry, "Reporta erros e contexto", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

**Notas de implementação**
- O **firewall** é **determinístico e sem LLM**: se o veredito for `BLOCK`, o fluxo encerra **antes**
  de qualquer chamada externa (economia de token + não alimentar o modelo com conteúdo manipulado).
- O texto que vai ao LLM externo é **pseudonimizado** (masking reversível das partes/PII — LGPD art. 5º,
  XI); os valores reais são restaurados no resumo do revisor ([ADR-0012](adr/0012-reversible-anonymization-restore.md)).
- A classificação **TPU** roda **localmente** (embedding + k-NN), sem chamada externa.

---

## Nível 2 — Contêineres

As unidades executáveis/implantáveis e os dados.

```mermaid
C4Container
    title Nivel 2 — Conteineres (SHERPI)

    Person(assessor, "Assessor de Triagem", "Navegador")

    System_Boundary(sherpi, "SHERPI") {
        Container(web, "Web App", "Next.js 16 + React 19 + Tailwind v4", "UI: login, analise (rito, firewall, resumo, TPU top-3), revisao humana, historico, auditoria de LLM. Chama a API diretamente (cliente tipado, cookie httpOnly); guarda de rota via Proxy do Next (proxy.ts) - NAO e um BFF")
        Container(api, "API Backend", "Python >=3.12 / FastAPI", "REST /v1 + /v1/ingestion; JWT; orquestrador analyze_petition; 6 bounded contexts (DDD/hexagonal)")
        Container(worker, "Worker de Ingestao", "asyncio.Queue (in-process)", "Consome jobs de ingestao de peticoes de forma assincrona (Sprint 7)")
        ContainerDb(db, "PostgreSQL 16", "PostgreSQL + SQLModel/Alembic", "Analises (resumo + PII, sob JWT), eventos de auditoria, usuarios, jobs de ingestao, indice TPU (embeddings como bytes float32), auditoria de chamadas LLM")
    }

    System_Ext(llm, "Provedor de LLM", "Gemini / Grok / Anthropic / Fake")
    System_Ext(tribunais, "Tribunais (PJe / E-Proc)", "Sandbox")
    System_Ext(sentry, "Sentry", "Erros")

    Rel(assessor, web, "Usa", "HTTPS")
    Rel(web, api, "Chama a API REST", "HTTPS/JSON (direto; cookie httpOnly)")
    Rel(api, db, "Le e grava", "SQL (SQLModel)")
    Rel(api, worker, "Enfileira jobs", "in-process")
    Rel(worker, db, "Persiste estado do job", "SQL")
    Rel(tribunais, worker, "Fornece peticoes", "SourceAdapter")
    Rel(api, llm, "complete() via port LLMProvider", "HTTPS/JSON")
    Rel(api, sentry, "Reporta erros", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

**Notas de implementação**
- O **Worker de Ingestão** é *in-process* (uma `asyncio.Queue`), não um contêiner separado — é
  apresentado à parte por ter ciclo de vida próprio (job assíncrono). Não há broker externo no MVP.
- O **modelo de embedding** do TPU (JurisBERT, ou `FakeEmbeddingModel` em testes) roda **dentro** do
  processo da API — não é um serviço à parte.
- Implantação: `docker-compose.prod.yml` sobe **Postgres + API** (imagem multi-stage, *non-root*); o
  `docker-compose.yml` de dev sobe **só o banco**.

---

## Nível 3 — Componentes (API Backend)

Decomposição interna do contêiner **API Backend**, por camada hexagonal e bounded context.

```mermaid
C4Component
    title Nivel 3 — Componentes da API Backend

    Container_Boundary(api, "API Backend") {

        Component(rest, "interfaces/api", "FastAPI (driving adapter)", "Rotas REST /v1 e /v1/ingestion, /health, /ready; middleware (correlation id, JWT); dependencies = composition root")

        Component(orch, "application/analyze_petition", "Use case (orquestrador)", "Pipeline cross-context com early-exit no firewall; persistencia e deanonymize")

        Component(di, "document_integrity", "Bounded context", "DetectInjection - firewall determinístico (sem LLM); parsers PyMuPDF/DOCX (dispatching)")
        Component(pa, "petition_analysis", "Bounded context (CORE)", "ExtractPetition (LLM) + CheckAdmissibility (rito-aware: estrategias CPC 319/321 e CLT 840)")
        Component(tax, "taxonomy", "Bounded context", "SuggestTpu - embedding + indice k-NN (ranking hibrido, limiar de confianca; TUA real do CNJ)")
        Component(rev, "review", "Bounded context", "RecordReview - human-in-the-loop + auditoria append-only")
        Component(idc, "identity", "Bounded context", "Authenticate - JWT, bcrypt")
        Component(intg, "integration", "Bounded context", "IngestPetitions - fila assincrona + SandboxSourceAdapter")

        Component(sk, "shared_kernel", "Dominio transversal", "Ports (LLMProvider, BlobStorage, Anonymizer, ReversibleAnonymizer); VOs (CPF, CNPJ, Rito, RiskVerdict, Role); eventos")

        Component(infra_llm, "infrastructure/llm", "Adapters", "factory + Gemini/Grok/Anthropic/Fake; circuit breaker; auditoria de chamadas")
        Component(infra_anon, "infrastructure/anonymization", "Adapters", "RegexAnonymizer / Mapped (reversivel) + PresidioAnonymizer (NER, opcional)")
        Component(infra_db, "infrastructure/persistence", "Adapters", "engine, models, repository (SQLModel)")
    }

    ContainerDb(db, "PostgreSQL 16", "Banco")
    System_Ext(llm, "Provedor de LLM", "Externo")

    Rel(rest, idc, "autentica")
    Rel(rest, orch, "dispara analise")
    Rel(rest, rev, "registra revisao")
    Rel(rest, intg, "cria/consulta jobs")

    Rel(orch, di, "1. firewall (early-exit)")
    Rel(orch, pa, "2. extrai + 3. admissibilidade")
    Rel(orch, tax, "4. sugere TPU")

    Rel(pa, sk, "usa port LLMProvider")
    Rel(infra_llm, sk, "implementa LLMProvider")
    Rel(infra_anon, sk, "implementa Anonymizer")
    Rel(pa, infra_llm, "complete()")
    Rel(infra_llm, llm, "HTTPS/JSON")

    Rel(rev, infra_db, "persiste")
    Rel(idc, infra_db, "persiste")
    Rel(tax, infra_db, "indice TPU")
    Rel(orch, infra_db, "persiste analise")
    Rel(infra_db, db, "SQL")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Notas de implementação**
- A **regra do hexágono**: cada contexto tem `domain` (puro) → `application` (use cases) →
  `infrastructure` (adapters). O `shared_kernel` declara os ports transversais; os adapters em
  `infrastructure/` os implementam e são **injetados** em `interfaces/api/dependencies.py` (composition root).
- `document_integrity` é o **único** contexto que **não** depende de LLM — é puro PyMuPDF/python-docx.
- A numeração das setas do orquestrador (1→4) corresponde ao fluxo do Nível 4.

---

## Nível 4 — Código (fluxo do orquestrador `analyze_petition`)

No nível mais concreto, o C4 admite mostrar a estrutura de código onde ela for relevante. Aqui o que
importa é o **fluxo do use case** que costura os contextos — um Python explícito com **um único ponto
de bifurcação** (não um framework de grafos).

```mermaid
flowchart TB
    A["bytes do PDF/DOCX (Documento)"] --> B["DetectInjection<br/>firewall determinístico (PyMuPDF)"]
    B --> C{"verdict?"}
    C -->|BLOCK| Z["encerra: ForensicsReport<br/>SEM nenhuma chamada de LLM"]
    C -->|PASS / WARN| D["texto sanitizado<br/>+ pseudonimização (Anonymizer)"]
    D --> E["ExtractPetition<br/>LLMProvider.complete (temperature=0, retry)"]
    E --> F["CheckAdmissibility<br/>estratégia por Rito (CPC 319/321 · CLT 840)"]
    F --> G["SuggestTpu<br/>embedding + k-NN (ranking híbrido + limiar)"]
    G --> H["deanonymize_model<br/>restaura PII no resumo do revisor"]
    H --> I["Analysis persistida (PostgreSQL)"]
```

**Invariantes do fluxo**
- **`BLOCK` ⇒ zero LLM.** O *early-exit* do firewall é inegociável (custo + segurança).
- O **prompt persistido** para auditoria fica **pseudonimizado** (é o que o LLM viu); o **resumo
  persistido** contém PII e fica atrás de **JWT** (cripto em repouso = Fase 4).
- `CheckAdmissibility` é **determinístico + semântico**: validadores por rito, não só prompt.

---

## Rastreabilidade C4 ↔ código

| Nível C4 | Onde está no repositório |
|---|---|
| Contêiner Web App | `frontend/` (Next.js — `src/app`, `src/proxy.ts` = Proxy do Next 16, ex-middleware) |
| Contêiner API | `backend/src/sherpi/interfaces/api/` |
| Orquestrador | `backend/src/sherpi/application/analyze_petition.py` |
| Bounded contexts | `backend/src/sherpi/contexts/<contexto>/{domain,application,infrastructure}/` |
| Ports transversais | `backend/src/sherpi/shared_kernel/ports.py`, `value_objects.py` |
| Adapters de infraestrutura | `backend/src/sherpi/infrastructure/{llm,anonymization,persistence}/` |
| Composition root (DI) | `backend/src/sherpi/interfaces/api/dependencies.py` |
