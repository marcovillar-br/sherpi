---
title: "Processo Ágil de Desenvolvimento"
description: "Papéis (8 integrantes), Design Sprint, Kanban, cerimônias e retrospectivas."
doc_type: process
project: SHERPI
status: approved
version: 1.3
updated: 2026-06-19
language: pt-BR
tags: [agil, scrum, kanban, design-sprint, papeis, processo]
---

# Processo Ágil — SHERPI

| Campo | Valor |
|---|---|
| Documento | Processo Ágil de Desenvolvimento |
| Disciplina | Desenvolvimento Ágil para Projetos de IA (DAIA) |
| Framework | **Design Sprint semanal** (modelo Google) + Scrum/Kanban; MVP em 2 sprints + Fase 4 (sprints 3–9) |
| Versão | 1.3 |

> Este documento registra **como** o SHERPI é desenvolvido — papéis, artefatos e cerimônias —
> tornando explícita a metodologia ágil exigida pela ementa e pelo Guia de Diretrizes. Complementa o
> [`roadmap.md`](roadmap.md) (o *o quê* e *quando*), o [`pmp.md`](pmp.md) (gerência do projeto), a
> [`wbs.md`](wbs.md) (EAP) e o [`backlog.md`](backlog.md) (backlog do produto e das sprints).

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
| 6 | **Engenheiro DevOps, Segurança e Observabilidade** | 1 | Infra, CI/CD, *hardening* e telemetria. | Docker/PostgreSQL, CI (lint/type/test/eval), segurança de upload/auth, logging estruturado, `/health`·`/ready`. |

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
Guia. A EAP está em [`wbs.md`](wbs.md). Resumo abaixo.

### 3.1 Metas das Sprints

Sprints 1–9 entregues (backend + frontend completo + refactor en-US/EP12). Tasks em [`backlog.md`](backlog.md).

| Sprint | Meta | Épicos | Status |
|---|---|---|---|
| **1** | Fundações + firewall + extração estruturada | EP1, EP3, EP2 | ✅ |
| **2** | Admissibilidade + orquestração + persistência + UI mínima | EP2, EP3, EP4 | ✅ |
| **3** | **Domínio Trabalhista (CLT 840) + rito-aware** (foco do grupo) | EP10 | ✅ |
| **4** | Confiança & Conformidade: identidade (JWT) + revisão/auditoria | EP6, EP7 | ✅ |
| **5** | Classificação TPU por ramo (JurisBERT + k-NN/numpy) | EP5 | ✅ |
| **6** | Produção: observabilidade, LGPD pleno (NER), deploy/CI-CD | EP9 | ✅ |
| **7** | Integração PJe/E-Proc (ingestão assíncrona) | EP8 | ✅ |
| **8** | UI das Sprints 4–7: login, rito, TPU top-3, revisão humana | EP6, EP7, EP5 | ✅ |
| **9** | Refactor de nomenclatura para en-US (domínio/API/UI) + coerência documental | EP12 | ✅ |

> Priorização: **risco-primeiro** no MVP (firewall/extração antes); na Fase 4, **valor/conformidade
> primeiro** (controle humano auditável destrava adoção), depois a capacidade que falta (TPU),
> hardening e, por fim, a integração externa (maior dependência).

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
- Firewall `document_integrity` detecta 8 vetores de injeção; veredito `BLOCK` encerra o fluxo
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

### Sprints 2–9

O registro detalhado de Review/Retrospective das Sprints 2–9 vive nos artefatos
de entrega de cada sprint — ver [`demo-sprint-review.md`](demo-sprint-review.md) e
[`backlog.md`](backlog.md). Resumo: 9 sprints entregues, frontend completo e
refactor en-US (EP12); sem débito técnico bloqueante.

## 7. Métricas de processo (saúde ágil)

- **Velocidade**: itens de backlog concluídos por sprint (referência para o planejamento seguinte).
- **Lead time**: tempo de um cartão de "A Fazer" a "Concluído".
- **Qualidade do incremento**: cobertura de testes e métricas do *eval* por sprint — o feedback
  empírico que substitui a "sensação" de progresso por evidência.
