---
title: "Backlog do Produto e Sprint Backlog"
description: "Backlog do Produto (épicos e histórias, visão de futuro) e Sprint Backlog (tasks estimadas das 2 sprints)."
doc_type: backlog
project: SHERPI
status: approved
version: 1.1
updated: 2026-06-19
language: pt-BR
tags: [backlog, epicos, historias-de-usuario, sprint, estimativas]
---

# Backlog — SHERPI

Sob responsabilidade do **Product Owner (PO)**. Conforme o Guia de Diretrizes, o backlog é dividido
em duas partes: o **Backlog do Produto** (visão completa de futuro) e o **Sprint Backlog** (recorte
de execução das 2 Sprints, desdobrado em tasks estimadas).

Legenda — Prioridade (MoSCoW): **M**ust · **S**hould · **C**ould · **W**on't (agora).
Estimativa em *story points* (SP, Fibonacci). Recorte: 🔵 Sprint · ⚪ Futuro.

---

## Parte 1 — Backlog do Produto (visão completa)

### Épico EP1 — Integridade Documental (firewall) 🔵 *core diferencial*

| ID | História | Prio | Status |
|---|---|---|---|
| US1.1 | Como **assessor**, quero que o sistema detecte texto oculto/*prompt injection* no PDF **antes** de qualquer análise, para não ser enganado por conteúdo manipulado. | M | ✅ feito |
| US1.2 | Como **magistrado**, quero um laudo das anomalias (tipo, página, evidência), para fundamentar eventual multa por má-fé. | M | ✅ feito |
| US1.3 | Como **servidor**, quero que arquivos não-PDF/grandes demais sejam rejeitados com mensagem clara, para garantir segurança de upload. | S | ✅ feito |

### Épico EP2 — Análise da Petição (extração + admissibilidade) 🔵 *core domain*

| ID | História | Prio | Recorte |
|---|---|---|---|
| US2.1 | Como **assessor**, quero um resumo estruturado (partes, fatos, fundamentação, pedidos, valor da causa), para reduzir o tempo de leitura. | M | 🔵 S1 |
| US2.2 | Como **magistrado**, quero destaque de pedidos de **liminar/tutela de urgência**, para priorizar a análise. | M | 🔵 S2 |
| US2.3 | Como **servidor**, quero um **checklist de admissibilidade** (arts. 319/321) com semáforo, para identificar necessidade de emenda. | M | 🔵 S2 |
| US2.4 | Como **assessor**, quero ver a **proveniência** (trecho de origem) de cada campo extraído, para confiar no resumo (interpretabilidade). | S | 🔵 S2 |

### Épico EP3 — Orquestração & Plataforma 🔵

| ID | História | Prio | Recorte |
|---|---|---|---|
| US3.1 | Como **usuário**, quero enviar um PDF e receber a análise consolidada em uma única operação. | M | 🔵 S2 |
| US3.2 | Como **time**, quero que o LLM seja trocável por configuração, para não depender de um fornecedor. | M | 🔵 S1 |
| US3.3 | Como **time**, quero **persistir** as análises, para consultá-las posteriormente. | S | 🔵 S2 |
| US3.4 | Como **time**, quero um **eval harness** com métricas, para medir a qualidade objetivamente. | S | 🔵 S2 |

### Épico EP4 — Experiência do Usuário (UI mínima) 🔵

| ID | História | Prio | Recorte |
|---|---|---|---|
| US4.1 | Como **assessor**, quero uma tela para enviar o PDF e ver **laudo + resumo lado a lado**. | M | 🔵 S2 |
| US4.2 | Como **magistrado**, quero **tarja vermelha** quando houver injeção detectada, para perceber o risco de imediato. | M | 🔵 S2 |

### Épicos da Fase 4 (agendados em sprints — ordem por importância/ganho)

| Épico | Histórias (resumo) | Prio | Sprint |
|---|---|---|---|
| EP10 — Domínio Trabalhista + rito-aware | Arquitetura por rito (ADR-0008); `TrabalhistaStrategy` (CLT 840, pedido líquido). | **M** | 3 |
| EP6 — Identidade & Acesso | Login obrigatório (JWT, perfil único); rotas protegidas. | M | 4 |
| EP7 — Revisão & Auditoria | Registrar decisão humana; trilha append-only (CNJ 615/2025). | M | 4 |
| EP5 — Classificação Taxonômica (TPU) | Sugerir top-3 classes/assuntos do CNJ (JurisBERT + k-NN), por ramo. | S | 5 |
| EP9 — Hardening de Produção | Observabilidade (logs+correlation id), LGPD pleno (NER), deploy/CI-CD. | S | 6 |
| EP8 — Integração Judicial | Conectores PJe/E-Proc; ingestão em lote/assíncrona. | C | 7 |
| EP11 — Domínios adicionais | Previdenciário/INSS, execução fiscal, família/JEC (encaixes rito-aware). | C | pós-3 |

---

## Parte 2 — Sprint Backlog (execução)

Histórias selecionadas por sprint, desdobradas em **tasks técnicas estimadas**. Sprints 1–2 (MVP)
concluídas; Sprints 3–6 (Fase 4) planejadas.

### Sprint 1 — Fundações + Firewall + Extração *(grande parte concluída)*

| História | Task | SP | Status |
|---|---|---|---|
| — | Scaffold DDD + tooling + CI + docker-compose | 5 | ✅ |
| US1.1/1.2 | Detector puro (7 vetores) + `ForensicsReport` | 5 | ✅ |
| US1.1 | Adapter PyMuPDF (CropBox→MediaBox) | 3 | ✅ |
| US1.3 | Guarda de upload (tipo/tamanho/páginas) | 2 | ✅ |
| — | Gerador de dados sintéticos + corpus rotulado | 3 | ✅ |
| US3.2 | Port `LLMProvider` + adapter Gemini + `FakeProvider` | 5 | ✅ |
| US2.1 | `ExtractPetition` + schema `PetitionSummary` + retry | 5 | ✅ |
| US2.1 | *Defensive prompting* + *chunking* (>100 págs) | 3 | ✅ |
| **Total Sprint 1** | | **31** | ✅ |

### Sprint 2 — Admissibilidade + Orquestração + Persistência + UI

| História | Task | SP |
|---|---|---|
| US2.3 | Validadores determinísticos (CPF/CNPJ, valor, pedidos) | 3 |
| US2.3 | Checagem semântica de documentos + `AdmissibilityReport` (semáforo) | 5 |
| US2.2 | Destaque de liminar/tutela de urgência | 2 |
| US2.4 | Proveniência dos campos extraídos (interpretabilidade) | 3 |
| US3.1 | Orquestrador `analyze_petition` (firewall→extração→admissibilidade) | 3 |
| US3.1 | API FastAPI `POST /analyze` + `/health` `/ready` | 3 |
| US3.3 | Persistência (SQLModel + Alembic + repositório) | 5 |
| US3.4 | Eval harness + métricas + gate de CI | 5 |
| US4.1 | UI mínima: upload → painel laudo + resumo | 5 |
| US4.2 | Tarja de risco (BLOCK) na UI | 2 |
| **Total Sprint 2** | | **36** ✅ |

### Sprint 3 — Domínio Trabalhista (CLT 840) + rito-aware

| Épico | Task | SP | Status |
|---|---|---|---|
| EP10 | Enum `Rito` + `AdmissibilityStrategy` (Protocol) + registro; extrair `CivelStrategy` (sem mudar comportamento) | 5 | ✅ |
| EP10 | `TrabalhistaStrategy` (CLT art. 840 §1º) + checagem de **pedido líquido** | 5 | ✅ |
| EP10 | `Pedido.valor` no `PetitionSummary` + prompt; parâmetro `rito` no `POST /v1/analyze` | 3 | ✅ |
| EP10 | Cenários sintéticos trabalhistas (cumulação massiva; pedido líquido × ilíquido) | 3 | ✅ |
| **Total Sprint 3** | | **16** | ✅ |

**Desdobramento técnico** (execução):

- **Rito-aware** (ADR-0008): `Rito` (enum) em `shared_kernel/value_objects.py`;
  `AdmissibilityStrategy` (`Protocol`), `CivelStrategy`, `TrabalhistaStrategy` e
  `DEFAULT_STRATEGIES` em `petition_analysis/domain/strategies.py`. `CheckAdmissibility`
  vira **dispatcher** `Rito → estratégia` (default cível); cível byte-a-byte inalterado
  (testes legados intactos como prova de não-regressão).
- **Pedido líquido**: `TrabalhistaStrategy` herda o checklist do art. 319 e acrescenta o
  requisito `PEDIDO_LIQUIDO` (cada `Pedido` precisa de `valor` parseável); ilíquido →
  emenda (VERMELHO). `Pedido.valor` adicionado ao `PetitionSummary` + instrução no prompt.
- **Roteamento**: `AnalyzePetition.run(..., rito=CIVEL)` e `AnalysisResult.rito`; `rito` como
  *form field* em `POST /v1/analyze` (default cível; valor inválido → 422).
- **Massa**: `trabalhista_pedido_liquido` (verde), `trabalhista_pedido_iliquido` (vermelho),
  `trabalhista_cumulacao_massiva` (verde); rótulo `rito` no corpus/`labels.json`.

**Definition of Done (Sprint 3)**

- [x] Admissibilidade despacha por rito; cível inalterado; `TrabalhistaStrategy` valida pedido líquido.
- [x] Massa com cenários trabalhistas (cumulação massiva, pedido líquido × ilíquido). Testes verdes.
- [x] `POST /v1/analyze` aceita `rito` (default cível); rito inválido → 422.
- [x] `ruff`/`mypy`/`pytest` limpos; eval do firewall no limiar (precision/recall = 1.0).
- [ ] **Sprint Review (sábado)**: demo do trabalhista (pedido ilíquido → VERMELHO) vs. cível.

### Sprint 4 — Confiança & Conformidade (`identity` + `review`)

| Épico | Task | SP |
|---|---|---|
| EP6 | Contexto `identity`: `User`/`Role`, `BcryptHasher`, `JwtIssuer`, `UserRepository` (SQLModel) | 5 |
| EP6 | `Authenticate` (OAuth2 password + JWT) + `POST /v1/auth/login` + usuário semeado | 3 |
| EP6 | Proteção de rotas por JWT (cookie httpOnly+Secure+SameSite) + rate-limit/lockout + CSRF | 5 |
| EP7 | Contexto `review`: `ReviewDecision`, `AuditEvent`, `RecordReview`, `AuditRepository` (append-only) | 5 |
| EP7 | `POST /v1/analyses/{id}/review` (decisão vinculada ao usuário) | 3 |
| EP6/EP7 | UI: tela de login + ações de revisão (aceitar/rejeitar/corrigir) | 5 |
| **Total Sprint 4** | | **26** |

### Sprint 5 — Classificação TPU (`taxonomy`)

| Épico | Task | SP |
|---|---|---|
| EP5 | Deps de ML (`--extra ml`) + **seed rotulado** petição→código TPU | 5 |
| EP5 | `EmbeddingModel` (JurisBERT/HuggingFace) + `TpuIndex` (k-NN em pgvector) | 5 |
| EP5 | `ClassifyTpu` + `SuggestTpu` (top-3 com confiança) + ligação no orquestrador | 5 |
| EP5 | Eval: acurácia top-1/top-3 sobre o seed (honesta) | 3 |
| EP5 | UI: top-3 sugestões com confiança e exemplos-âncora | 3 |
| **Total Sprint 5** | | **21** |

### Sprint 6 — Produção (observabilidade, LGPD pleno, deploy)

| Épico | Task | SP |
|---|---|---|
| EP9 | Logging estruturado (`structlog`) + correlation IDs (middleware) | 3 |
| EP9 | *Error tracking* (Sentry) + métricas básicas | 3 |
| EP9 | LGPD: NER de nomes (Presidio/spaCy) + anonimização reversível | 5 |
| EP9 | Retenção/eliminação de PDFs/análises (direito ao esquecimento) | 3 |
| EP9 | Containerização completa (app+db) + CI/CD com deploy + secrets manager + TLS | 5 |
| **Total Sprint 6** | | **19** |

### Sprint 7 — Integração PJe/E-Proc

| Épico | Task | SP |
|---|---|---|
| EP8 | Bounded context de integração: adapter PJe/E-Proc (sandbox) | 8 |
| EP8 | Ingestão em lote + execução assíncrona/fila | 5 |
| **Total Sprint 7** | | **13** |

> As estimativas serão recalibradas em cada *Sprint Planning* conforme a capacidade real da equipe e
> o framework de Design Sprint.
