---
title: "Backlog do Produto e Sprint Backlog"
description: "Backlog do Produto (épicos e histórias, visão de futuro) e Sprint Backlog (tasks estimadas das 2 sprints)."
doc_type: backlog
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
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

### Épicos de visão de futuro (fora do recorte das 2 Sprints)

| Épico | Histórias (resumo) | Prio |
|---|---|---|
| EP5 — Classificação Taxonômica (TPU) | Sugerir top-3 classes/assuntos do CNJ por similaridade (embeddings + k-NN). | C ⚪ |
| EP6 — Identidade & Acesso | Login (perfil único), depois RBAC. | W ⚪ |
| EP7 — Revisão & Auditoria | Registrar decisão humana; trilha append-only (CNJ 615/2025). | W ⚪ |
| EP8 — Integração Judicial | Conectores PJe/E-Proc; ingestão em lote. | W ⚪ |
| EP9 — Hardening de Produção | Observabilidade, LGPD, deploy, escala (Fase 4). | W ⚪ |

---

## Parte 2 — Sprint Backlog (execução)

Apenas as histórias selecionadas para as 2 Sprints, desdobradas em **tasks técnicas estimadas**.

### Sprint 1 — Fundações + Firewall + Extração *(grande parte concluída)*

| História | Task | SP | Status |
|---|---|---|---|
| — | Scaffold DDD + tooling + CI + docker-compose | 5 | ✅ |
| US1.1/1.2 | Detector puro (7 vetores) + `ForensicsReport` | 5 | ✅ |
| US1.1 | Adapter PyMuPDF (CropBox→MediaBox) | 3 | ✅ |
| US1.3 | Guarda de upload (tipo/tamanho/páginas) | 2 | ✅ |
| — | Gerador de dados sintéticos + corpus rotulado | 3 | ✅ |
| US3.2 | Port `LLMProvider` + adapter Gemini + `FakeProvider` | 5 | ⏳ |
| US2.1 | `ExtractPetition` + schema `PetitionSummary` + retry | 5 | ⏳ |
| US2.1 | *Defensive prompting* + *chunking* (>100 págs) | 3 | ⏳ |
| **Total Sprint 1** | | **31** | |

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
| **Total Sprint 2** | | **36** |

> As estimativas serão recalibradas na *Sprint Planning* conforme a capacidade real da equipe e o
> framework de Design Sprint apresentado pelo professor.
