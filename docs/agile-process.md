---
title: "Processo Ágil de Desenvolvimento"
description: "Papéis (8 integrantes), Design Sprint, Kanban, cerimônias e retrospectivas."
doc_type: process
project: SHERPI
status: approved
version: 1.1
updated: 2026-06-18
language: pt-BR
tags: [agil, scrum, kanban, design-sprint, papeis, processo]
---

# Processo Ágil — SHERPI

| Campo | Valor |
|---|---|
| Documento | Processo Ágil de Desenvolvimento |
| Disciplina | Desenvolvimento Ágil para Projetos de IA (DAIA) |
| Framework | **Design Sprint semanal** (modelo Google) + Scrum/Kanban; **2 Sprints / 2 semanas** |
| Versão | 1.1 |

> Este documento registra **como** o SHERPI é desenvolvido — papéis, artefatos e cerimônias —
> tornando explícita a metodologia ágil exigida pela ementa e pelo Guia de Diretrizes. Complementa o
> [`roadmap.md`](roadmap.md) (o *o quê* e *quando*), o [`pgp.md`](pgp.md) (gerência do projeto), a
> [`eap.md`](eap.md) (EAP) e o [`backlog.md`](backlog.md) (backlog do produto e das sprints).

## 1. Por que ágil em um projeto de IA

Projetos de IA têm incerteza intrínseca que o desenvolvimento em cascata não absorve: não se sabe,
de antemão, se um modelo atingirá a acurácia necessária nem se uma abordagem (ex.: classificador TPU)
é viável com os dados disponíveis. O ágil responde a isso com **iteração curta e validação empírica**:
cada sprint entrega uma fatia funcional e mensurável, e o *eval harness* fecha o ciclo de feedback
quantitativo. Decisões arriscadas (firewall, qualidade da extração via LLM) são atacadas **cedo**,
reduzindo o risco de descobrir tarde que algo não funciona.

Fundamentos aplicados: Scrum como framework de cadência e papéis (Sutherland & Schwaber, *The Scrum
Guide*, 2017); colaboração como "jogo cooperativo" de comunicação entre os papéis (Cockburn, *Agile
Software Development*, 2015). O LeSS (Larman & Vodde, 2016) é a referência de escala para quando o
produto crescer além de um time (Fase 4); no MVP, mantém-se **um único time multidisciplinar**.

## 2. Papéis (colaboração interdisciplinar)

A ementa enfatiza a colaboração entre desenvolvedores de software e cientistas de dados. Os **oito
integrantes** do time do SHERPI estruturam essa colaboração em sete papéis; o de **Desenvolvedor
Fullstack é ocupado por dois integrantes** (um com foco em backend/API, outro em frontend), por ser a
maior superfície do projeto e por API e frontend serem desacoplados.

| # | Papel | Integrantes | Responsabilidade | Foco no SHERPI |
|---|---|---|---|---|
| 0 | **Gerente de Projeto (GP)** | 1 | Cronograma, escopo, riscos, *stakeholders* e entregas acadêmicas. | Garante a entrega do MVP em 2 sprints e a defesa do trabalho. |
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

O backlog completo (Épicos → histórias) e o Sprint Backlog (tasks estimadas) são mantidos em
[`backlog.md`](backlog.md), conforme a divisão **visão completa × escopo de execução** exigida pelo
Guia. A EAP está em [`eap.md`](eap.md). Resumo abaixo.

### 3.1 Metas das Sprints (recorte do MVP — 2 semanas)

| Sprint | Meta | Épicos/histórias |
|---|---|---|
| **1** | Fundações + firewall + extração estruturada | EP1 (US1.x), EP3 (US3.2), EP2 (US2.1) |
| **2** | Admissibilidade + orquestração + persistência + UI mínima | EP2 (US2.2–2.4), EP3 (US3.1/3.3/3.4), EP4 (US4.x) |

Visão de futuro (fora do recorte): TPU (EP5), autenticação (EP6), auditoria (EP7), integração
judicial (EP8), hardening (EP9) — registrados no backlog do produto.

> Priorização **risco-primeiro**: itens de maior incerteza técnica (firewall, extração) puxados para
> o início, para falhar cedo e barato.

### 3.2 Definition of Done (transversal)

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

Ferramentas: **GitHub Projects** (quadro Kanban vinculado às *issues*/PRs do repositório) e
**Microsoft Planner**, conforme o Guia. Cada cartão atravessa as colunas e só chega a "Concluído"
quando satisfaz a *Definition of Done*.

## 5. Ritmo: Design Sprint semanal + cerimônias

O Guia define um **Design Sprint semanal (modelo Google)**: cada dia útil corresponde a uma etapa, e
as Dailies ganham propósito por estarem ancoradas nessa etapa. O mapa abaixo é uma **proposta inicial**
a ser ajustada após a aula de sábado em que o professor apresenta o framework oficial e a metodologia
de projetos de IA/Mineração de Dados.

| Dia | Etapa (Design Sprint) | Aplicação no SHERPI |
|---|---|---|
| Segunda | Mapear/Entender | Sprint Planning; alinhar a meta da semana com o PO. |
| Terça | Idear/Esboçar | Desenhar a solução das histórias da sprint (contratos, prompts, telas). |
| Quarta | Decidir | Escolher abordagem; refinar tasks no Kanban. |
| Quinta | Construir/Prototipar | Implementação + testes. |
| Sexta | Testar/Validar | Eval, integração, preparação da demo. |
| **Sábado** | **Sprint Review** | Validação da entrega com o **professor** + refinamento do backlog. |

| Cerimônia | Cadência | Propósito no SHERPI |
|---|---|---|
| **Sprint Planning** | Segunda | Selecionar histórias do backlog e definir a meta da sprint. |
| **Daily** | Diária | Sincronizar progresso e impedimentos, ancorada na etapa do dia; alinhamento com o PO. |
| **Sprint Review** | **Sábado** | Demonstrar a fatia funcional ao professor (ex.: firewall bloqueando um PDF malicioso ao vivo). |
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

### Sprint 2 — *(a registrar na Sprint Review de sábado)*

## 7. Métricas de processo (saúde ágil)

- **Velocidade**: itens de backlog concluídos por sprint (referência para o planejamento seguinte).
- **Lead time**: tempo de um cartão de "A Fazer" a "Concluído".
- **Qualidade do incremento**: cobertura de testes e métricas do *eval* por sprint — o feedback
  empírico que substitui a "sensação" de progresso por evidência.
