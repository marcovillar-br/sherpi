---
title: "Roadmap do MVP (2 sprints)"
description: "Roadmap do MVP em 2 sprints (2 semanas), com Definition of Done, visão de futuro e marcos."
doc_type: roadmap
project: SHERPI
status: approved
version: 1.1
updated: 2026-06-18
language: pt-BR
tags: [roadmap, sprints, planejamento, mvp]
---

# Roadmap — SHERPI

| Campo | Valor |
|---|---|
| Documento | Roadmap |
| Versão | 1.1 |
| Status | Aprovado |
| Última atualização | 2026-06-18 |

O **MVP** é entregue em **2 Sprints (2 semanas)**, conforme o Guia de Diretrizes da disciplina, com
ritmo de **Design Sprint semanal** e **Sprint Review aos sábados** (ver [`agile-process.md`](agile-process.md)).
Cada sprint tem objetivos, entregáveis e **critérios de saída (Definition of Done)**. O escopo além
do MVP está registrado como **visão de futuro** (ver [`backlog.md`](backlog.md)) e detalhado na **Fase 4**.

---

## Sprint 1 (Semana 1) — Fundações + Firewall + Extração

**Objetivo**: erguer o esqueleto hexagonal, entregar o diferencial do produto (firewall) testado, os dados sintéticos do eval e a extração estruturada agnóstica a LLM.

**Entregáveis**

- Scaffolding `backend/` (uv); `docker-compose` com Postgres+pgvector; CI (lint + type + test).
- `shared_kernel`: Value Objects (CPF, CNPJ, ValorCausa, RiskVerdict) e ports transversais (LLMProvider, BlobStorage, Anonymizer).
- Bounded context **document_integrity** completo: `DetectInjection` + `PyMuPDFParser`, cobrindo os 7 vetores de injeção, fortemente unit-testado. ✅
- **Gerador de petições sintéticas**: peças limpas + injeções plantadas de cada vetor (ground truth). ✅
- Port `LLMProvider` + adapter **Gemini (default)** + `FakeProvider`.
- Bounded context **petition_analysis** (parcial): `ExtractPetition` (JSON validado, temperature=0, *defensive prompting*, *chunking* >100 págs).

**Definition of Done**

- [x] `uv run pytest` verde no domínio puro e no firewall (um teste por vetor de injeção).
- [x] CI executa lint (ruff), type (mypy) e testes em cada push.
- [x] Dataset sintético com rótulos disponível via `synthetic.generate`.
- [ ] `LLMProvider` trocável por config; `ExtractPetition` retorna `PetitionSummary` validado (com `FakeProvider`).
- [ ] **Sprint Review (sábado)**: demo do firewall bloqueando PDF malicioso + extração de uma petição limpa.

---

## Sprint 2 (Semana 2) — Admissibilidade + Orquestração + Persistência + UI

**Objetivo**: fechar o MVP demonstrável ponta a ponta: admissibilidade, orquestrador, persistência e uma UI mínima.

**Entregáveis**

- **petition_analysis**: `CheckAdmissibility` (validadores determinísticos + extração semântica, arts. 319/321) com proveniência dos campos.
- Use case orquestrador `analyze_petition` (integrity → [BLOCK?] → extração → admissibilidade).
- API FastAPI: `POST /analyze`, `/health`, `/ready`.
- Persistência: SQLModel + Alembic, repositório das análises.
- **UI mínima**: upload do PDF → painel com laudo de segurança + resumo estruturado (tarja vermelha em `BLOCK`).
- **Eval harness**: precision/recall do firewall e F1 da extração; gate no CI.

**Definition of Done**

- [ ] Orquestrador testado com `FakeProvider` (sem rede): caminho feliz e early-exit por `BLOCK`.
- [ ] Validadores determinísticos (checksum CPF/CNPJ, valor da causa, pedidos) com testes exatos.
- [ ] `POST /analyze`: PDF limpo → resumo + admissibilidade; PDF com injeção → `BLOCK` **sem chamada LLM**; análise persistida e recuperável.
- [ ] UI: upload → laudo + resumo lado a lado; tarja vermelha quando houver injeção.
- [ ] `uv run python -m evals.run` produz métricas; CI falha abaixo do limiar.
- [ ] `ruff` e `mypy` limpos.
- [ ] **Sprint Review (sábado)**: demo do MVP completo (upload → análise consolidada na UI).

---

## Visão de futuro (pós-MVP) — Fase 4 — Hardening e expansão

**Objetivo**: transformar o MVP em sistema produtivo, seguro e operável, incorporando as capacidades adiadas.

**Entregáveis**

- **Capacidades adiadas do MVP** (visão de futuro do backlog):
  - **taxonomy**: `SuggestTpu` (embedding JurisBERT + k-NN sobre pgvector) — top-3 classes/assuntos do CNJ.
  - **identity**: login OAuth2/JWT (perfil único) e, depois, RBAC.
  - **review**: `RecordReview` (human-in-the-loop) + trilha de auditoria append-only (CNJ 615/2025).
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
| M1 — Firewall + dados + extração | Semana 1 | Firewall testado por vetor; dataset sintético; LLM agnóstico + extração estruturada. |
| M2 — MVP completo | Semana 2 | Admissibilidade + orquestrador + persistência + UI + eval; demo ponta a ponta. |
| M3 — Expansão/Produção | Fase 4 | TPU, auth, auditoria, integração processual, observabilidade, CI/CD. |
