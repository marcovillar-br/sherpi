---
title: "Processo Ágil de Desenvolvimento"
description: "Papéis (8 integrantes), backlog, Kanban, cerimônias e retrospectivas."
doc_type: process
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [agil, scrum, kanban, papeis, processo]
---

# Processo Ágil — SHERPI

| Campo | Valor |
|---|---|
| Documento | Processo Ágil de Desenvolvimento |
| Disciplina | Desenvolvimento Ágil para Projetos de IA (DAIA) |
| Framework | Scrum adaptado ao contexto de IA, com quadro Kanban |
| Versão | 1.0 |

> Este documento registra **como** o SHERPI é desenvolvido — papéis, artefatos e cerimônias —
> tornando explícita a metodologia ágil exigida pela ementa. Complementa o
> [`roadmap.md`](roadmap.md) (o *o quê* e *quando*) com o *como*.

## 1. Por que ágil em um projeto de IA

Projetos de IA têm incerteza intrínseca que o desenvolvimento em cascata não absorve: não se sabe,
de antemão, se um modelo atingirá a acurácia necessária nem se uma abordagem (ex.: classificador TPU)
é viável com os dados disponíveis. O ágil responde a isso com **iteração curta e validação empírica**:
cada sprint entrega uma fatia funcional e mensurável, e o *eval harness* fecha o ciclo de feedback
quantitativo. Decisões arriscadas (firewall, viabilidade da TPU) são atacadas **cedo**, reduzindo o
risco de descobrir tarde que algo não funciona.

Fundamentos aplicados: Scrum como framework de cadência e papéis (Sutherland & Schwaber, *The Scrum
Guide*, 2017); colaboração como "jogo cooperativo" de comunicação entre os papéis (Cockburn, *Agile
Software Development*, 2015). O LeSS (Larman & Vodde, 2016) é a referência de escala para quando o
produto crescer além de um time (Fase 4); no POC, mantém-se **um único time multidisciplinar**.

## 2. Papéis (colaboração interdisciplinar)

A ementa enfatiza a colaboração entre desenvolvedores de software e cientistas de dados. Os **oito
integrantes** do time do SHERPI estruturam essa colaboração em sete papéis; o de **Desenvolvedor
Fullstack é ocupado por dois integrantes** (um com foco em backend/API, outro em frontend), por ser a
maior superfície do projeto e por API e frontend serem desacoplados.

| # | Papel | Integrantes | Responsabilidade | Foco no SHERPI |
|---|---|---|---|---|
| 0 | **Gerente de Projeto (GP)** | 1 | Cronograma, escopo, riscos, *stakeholders* e entregas acadêmicas. | Garante a entrega do POC em 3 sprints e a defesa do trabalho. |
| 1 | **Product Owner (PO)** | 1 | Prioriza o backlog, define valor e *Definition of Done*. | Mantém o foco no gargalo de triagem e no *human-in-the-loop*. |
| 2 | **Scrum Master** | 1 | Facilita as cerimônias, remove impedimentos, protege o time. | Conduz planning/review/retro; cuida do quadro Kanban e do WIP. |
| 3 | **Arquiteto de Sistemas (Multiagentes)** | 1 | Desenho da arquitetura e dos contratos entre capacidades. | DDD hexagonal, *ports & adapters*, orquestrador que compõe as *skills* (firewall → extração → admissibilidade → TPU). |
| 4 | **Engenheiro de IA Generativa e Agentes** | 1 | Camada de modelos, *prompting*, *eval* e interpretabilidade. | `LLMProvider`/adapters, `ExtractPetition`, *defensive prompting*, classificador TPU (embeddings/k-NN), *eval harness*. |
| 5 | **Desenvolvedor Fullstack** | **2** | API e frontend desacoplados (um foco backend, um foco frontend). | **Backend**: FastAPI (rotas, contratos, integração dos use cases). **Frontend**: Next.js (PDF + extração + laudo), cliente tipado. |
| 6 | **Engenheiro DevOps, Segurança e Observabilidade** | 1 | Infra, CI/CD, *hardening* e telemetria. | Docker/Postgres+pgvector, CI (lint/type/test/eval), segurança de upload/auth, logging estruturado, `/health`·`/ready`. |

**Total: 8 integrantes** (1+1+1+1+1+2+1).

A colaboração mais sensível — entre o **Engenheiro de IA Generativa** (papel 4) e o **Desenvolvedor
Fullstack / Arquiteto** (papéis 3 e 5) — é mediada pela própria arquitetura: os modelos vivem atrás de
*ports* (`LLMProvider`, `EmbeddingModel`), então o time de IA itera no modelo sem quebrar o domínio, e
o time de engenharia evolui o sistema sem depender de um modelo específico. Esse desacoplamento **é** a
forma técnica da colaboração interdisciplinar que a ementa cobra. O **DevOps/Segurança** (papel 6)
fornece os *guard-rails* (CI, *eval gate*, telemetria) que tornam cada iteração mensurável e segura.

## 3. Artefatos

### 3.1 Product Backlog (priorizado por valor × risco)

| # | Item (história / capacidade) | Valor | Risco | Sprint |
|---|---|---|---|---|
| 1 | Firewall que bloqueia *prompt injection* antes do LLM | Alto | Alto | 1 |
| 2 | Gerador de dados sintéticos rotulados (sem LGPD) | Alto | Médio | 1 |
| 3 | Extração estruturada da petição (LLM, agnóstico) | Alto | Alto | 2 |
| 4 | Checagem de admissibilidade (arts. 319/321) | Alto | Médio | 2 |
| 5 | Classificação TPU (embeddings + k-NN) | Médio | **Alto** | 2 |
| 6 | Persistência + auditoria | Médio | Baixo | 2 |
| 7 | Autenticação (perfil único) | Médio | Baixo | 3 |
| 8 | Frontend (PDF + extração + laudo) | Alto | Médio | 3 |
| 9 | *Eval harness* + relatório de métricas | Alto | Médio | 3 |

> Priorização **risco-primeiro**: os itens de maior incerteza técnica (firewall, extração, TPU) são
> puxados para as primeiras sprints, para falhar cedo e barato.

### 3.2 Sprint Backlogs

Cada sprint tem um objetivo único e *Definition of Done* (detalhada no [`roadmap.md`](roadmap.md)).
As tarefas são rastreadas no quadro Kanban (§4) e refletidas na lista de tarefas do projeto.

| Sprint | Objetivo (meta da sprint) | Itens do backlog |
|---|---|---|
| **1** | Fundações DDD + firewall funcionando + dados de teste | 1, 2 |
| **2** | Núcleo cognitivo agnóstico + persistência | 3, 4, 5, 6 |
| **3** | Produto utilizável + autenticação + métricas → POC | 7, 8, 9 |

### 3.3 Definition of Done (transversal)

Um item só é "pronto" quando: código + **testes** passando; `ruff`/`mypy` limpos; documentação
atualizada; e — para itens de modelo — **métrica medida** no *eval* (nunca "prometida").

## 4. Quadro Kanban

Fluxo de trabalho visual com limite de WIP para evitar multitarefa:

```
┌─────────────┬───────────────┬──────────────┬───────────────┬─────────────┐
│  Backlog    │  A Fazer      │ Em Progresso │  Em Revisão   │  Concluído  │
│ (priorizado)│  (da sprint)  │  (WIP ≤ 2)   │ (testes/PR)   │   (DoD ✓)   │
└─────────────┴───────────────┴──────────────┴───────────────┴─────────────┘
```

No SHERPI o quadro é materializado pela lista de tarefas do projeto; cada cartão atravessa as colunas
e só chega a "Concluído" quando satisfaz a *Definition of Done*.

## 5. Cerimônias

| Cerimônia | Cadência | Propósito no SHERPI |
|---|---|---|
| **Sprint Planning** | Início da sprint | Selecionar itens do backlog e definir a meta da sprint. |
| **Daily** | Diária | Sincronizar progresso e remover impedimentos (relevante na ponte dev × cientista de dados). |
| **Sprint Review** | Fim da sprint | Demonstrar a fatia funcional (ex.: firewall bloqueando um PDF malicioso ao vivo). |
| **Retrospective** | Fim da sprint | Melhorar o processo; registrada em §6. |

## 6. Registro de Sprint Review & Retrospective

### Sprint 1 — Fundações + Firewall + Dados

**Review (incremento demonstrável):**
- Firewall `document_integrity` detecta 7 vetores de injeção; veredito `BLOCK` encerra o fluxo
  **sem gastar token** de LLM.
- Gerador de petições sintéticas rotuladas + corpus em `data/synthetic/`.
- 24 testes passando (domínio puro + integração PDF→parser→laudo); `ruff` e `mypy` limpos.

**Retrospective:**
- 👍 *Manter*: validar empiricamente as heurísticas contra PDFs reais cedo revelou o *clipping* da
  CropBox pelo PyMuPDF e levou à técnica de expandir CropBox→MediaBox.
- ⚠️ *Aprendizado*: nem todo vetor faz *round-trip* via fontes base de PDF (zero-width, `/ActualText`);
  decisão de cobri-los por teste de unidade do domínio e documentar a limitação — honestidade > inflar
  cobertura aparente.
- 🔧 *Ajustar*: investir cedo em interpretabilidade (item nominal da ementa) em vez de deixar para o fim.

### Sprint 2 — *(a registrar ao final da sprint)*

### Sprint 3 — *(a registrar ao final da sprint)*

## 7. Métricas de processo (saúde ágil)

- **Velocidade**: itens de backlog concluídos por sprint (referência para o planejamento seguinte).
- **Lead time**: tempo de um cartão de "A Fazer" a "Concluído".
- **Qualidade do incremento**: cobertura de testes e métricas do *eval* por sprint — o feedback
  empírico que substitui a "sensação" de progresso por evidência.
