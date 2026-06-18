---
title: "Roadmap (idea → produção)"
description: "Sprints com Definition of Done, Fase 4 de produção e marcos."
doc_type: roadmap
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [roadmap, sprints, planejamento]
---

# Roadmap idea→produção — SHERPI

| Campo | Valor |
|---|---|
| Documento | Roadmap |
| Versão | 1.0 |
| Status | Aprovado |
| Última atualização | 2026-06-17 |

O POC é entregue em **3 sprints (3 semanas)**. A **Fase 4** é o hardening para produção (pós-POC). Cada sprint tem objetivos, entregáveis e **critérios de saída (Definition of Done)**.

---

## Sprint 1 (Semana 1) — Fundações DDD + Firewall + Dados

**Objetivo**: erguer o esqueleto hexagonal, entregar o diferencial do produto (firewall) testado e produzir os dados sintéticos que sustentam todo o eval.

**Entregáveis**

- Scaffolding `backend/` (uv) e `frontend/` (Next.js); `docker-compose` com Postgres+pgvector; CI (lint + type + test).
- `shared_kernel`: Value Objects (CPF, CNPJ, ValorCausa, RiskVerdict, Documento) e ports transversais (LLMProvider, BlobStorage, Anonymizer).
- Bounded context **document_integrity** completo: `DetectInjection` (domain service) + `PyMuPDFParser` (adapter), cobrindo os 7 vetores de injeção, fortemente unit-testado.
- **Gerador de petições sintéticas**: peças limpas + injeções plantadas de cada vetor (ground truth).
- **Seed TPU** rotulado.
- Glossário da linguagem ubíqua + primeiros ADRs.

**Definition of Done**

- [ ] `uv run pytest` verde no domínio puro e no firewall (um teste por vetor de injeção).
- [ ] `docker compose up -d` sobe Postgres+pgvector; `alembic upgrade head` aplica o schema inicial.
- [ ] CI executa lint (ruff), type (mypy) e testes em cada push.
- [ ] Dataset sintético versionado em `data/synthetic/` com rótulos.
- [ ] ADRs 0001–0007 redigidos; glossário publicado em `ddd-context-map.md`.

---

## Sprint 2 (Semana 2) — Core domain + Cognição agnóstica + Persistência

**Objetivo**: implementar o núcleo cognitivo (extração + admissibilidade + TPU) atrás de ports, com o orquestrador explícito e a persistência completa.

**Entregáveis**

- Port `LLMProvider` + adapter **Gemini (default)** + `FakeProvider`.
- Bounded context **petition_analysis**: `ExtractPetition` (JSON validado, temperature=0, chunking >100 págs) e `CheckAdmissibility` (validadores determinísticos + extração semântica).
- Bounded context **taxonomy**: `SuggestTpu` (embedding JurisBERT + k-NN sobre pgvector).
- Use case orquestrador `analyze_petition` (integrity → [BLOCK?] → extract → admiss → tpu).
- Persistência: SQLModel + Alembic, repositórios, Unit of Work.

**Definition of Done**

- [ ] Orquestrador testado com `FakeProvider` (sem rede): caminho feliz e early-exit por `BLOCK`.
- [ ] Validadores determinísticos (checksum CPF/CNPJ, valor da causa, pedidos) com testes exatos.
- [ ] `SuggestTpu` retorna top-3 com confiança sobre o seed.
- [ ] Análise consolidada persistida e recuperável.
- [ ] Schema de extração com retry em caso de saída inválida.

---

## Sprint 3 (Semana 3) — Frontend + Auth + Avaliação + Entrega

**Objetivo**: fechar o POC com autenticação, supervisão humana, frontend e eval harness; demo funcional ponta a ponta.

**Entregáveis**

- Bounded context **identity**: login OAuth2/JWT, usuário semeado via `.env`, cookie httpOnly.
- Bounded context **review**: `RecordReview` (human-in-the-loop) + auditoria append-only.
- API FastAPI: `/auth/login`, `/analyze`, `/analyses/{id}`, `/analyses/{id}/review`, `/health`, `/ready` (rotas de análise protegidas).
- Frontend Next.js: tela de login + viewer de PDF + painel de extração + laudo de segurança.
- **Eval harness**: precision/recall do firewall, F1 da extração, top-3 TPU; gate no CI.
- Demo → **POC concluído**.

**Definition of Done**

- [ ] `/analyze` sem token → 401; com token → análise persistida.
- [ ] PDF limpo → resumo + semáforo + top-3 TPU; PDF com injeção → `BLOCK` sem chamada LLM.
- [ ] `POST /review` grava `AuditEvent` vinculado ao usuário autenticado.
- [ ] Frontend: login → submissão dos dois PDFs → tarja vermelha (injeção) vs. resumo (limpa), PDF renderizado lado a lado; sem login redireciona.
- [ ] `uv run python -m evals.run` produz métricas; CI falha abaixo do limiar.
- [ ] `/health` e `/ready` OK; upload de não-PDF/arquivo grande rejeitado; logins repetidos com senha errada → lockout; logs sem PII; `pip-audit` sem alta severidade.
- [ ] `ruff`, `mypy` e `npm run lint` limpos.

---

## Fase 4 (pós-POC) — Hardening para produção

**Objetivo**: transformar o POC em sistema produtivo, seguro e operável.

**Entregáveis**

- Autenticação/autorização: RBAC, refresh tokens, MFA, segredos em secrets manager, TLS/HTTPS.
- Observabilidade: tracing distribuído, métricas/dashboards, error tracking (Sentry), tracing de LLM.
- Conformidade LGPD: criptografia em repouso, política de retenção/eliminação, DPIA, opção de LLM local (Ollama/Maritaca on-prem) para dados sensíveis reais.
- Integração PJe/E-Proc (novo bounded context).
- Blob storage em S3/MinIO; execução assíncrona/fila para escala; containerização completa; CI/CD e deploy.
- Cadeia de suprimentos: SBOM, Dependabot, secret scanning, revisão de segurança/pentest, backups e DR.
- Ativar adapter **Maritaca Sabiá** conforme avaliação.

**Definition of Done**

- [ ] Auth/RBAC, observabilidade e conformidade LGPD em produção.
- [ ] Integração com pelo menos um sistema processual (PJe ou E-Proc).
- [ ] Pipeline CI/CD com deploy gerenciado e backups/DR.
- [ ] Revisão de segurança/pentest concluída.

---

## Tabela de marcos

| Marco | Sprint | Resultado |
|---|---|---|
| M1 — Firewall + dados | Semana 1 | Firewall testado por vetor; dataset sintético; ADRs. |
| M2 — Núcleo cognitivo | Semana 2 | Extração + admissibilidade + TPU + orquestrador + persistência. |
| M3 — POC completo | Semana 3 | Auth + review + frontend + eval harness; demo ponta a ponta. |
| M4 — Produção | Fase 4 | Hardening, integração processual, observabilidade, CI/CD. |
