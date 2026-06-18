---
title: "Plano de Gerenciamento do Projeto (PGP)"
description: "Escopo, tempo, custos, riscos, equipe, comunicação e qualidade do projeto SHERPI."
doc_type: pgp
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [gerenciamento-de-projeto, pgp, escopo, riscos, cronograma]
---

# Plano de Gerenciamento do Projeto (PGP) — SHERPI

Documento sob responsabilidade do **Gerente de Projeto (GP)**, focado no **escopo do projeto**.
Complementa o backlog (responsabilidade do PO, [`backlog.md`](backlog.md)) e a
[`eap.md`](eap.md). Conforme o Guia de Diretrizes da disciplina.

## 1. Identificação

| Campo | Valor |
|---|---|
| Projeto | **SHERPI** — Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais |
| Disciplina | Desenvolvimento Ágil para Projetos de IA (DAIA) |
| **Formato da entrega** | **MVP** (sistema funcional, com código implementado e executável) |
| Duração | **2 semanas / 2 Sprints** |
| Cliente/patrocinador (simulado) | Gabinete judicial de 1º grau (persona: magistrado/assessor) |
| Avaliador | Professor (Sprint Reviews aos sábados) |

## 2. Gerenciamento de Escopo

### 2.1 Objetivo do MVP
Demonstrar, com código executável, o fluxo de triagem assistida de uma petição inicial:
**firewall anti prompt-injection → extração estruturada → checagem de admissibilidade**, sob
supervisão humana.

### 2.2 Dentro do escopo (recorte das 2 Sprints)
- Firewall determinístico de integridade documental (✅ entregue na Sprint 1).
- Extração estruturada da petição via LLM agnóstico (Gemini default + `FakeProvider`).
- Checagem de admissibilidade (validadores determinísticos + extração semântica).
- Orquestrador do fluxo + API + persistência básica + UI mínima (upload → laudo + resumo).

### 2.3 Fora do escopo (registrado como visão de futuro no Backlog do Produto)
Classificação TPU (embeddings/k-NN), autenticação/RBAC completa, trilha de auditoria completa,
integração PJe/E-Proc, *hardening* de produção (Fase 4). Detalhamento em [`backlog.md`](backlog.md).

> A divisão escopo-completo (futuro) × escopo-de-execução (sprints) está formalizada no backlog,
> conforme exigência do Guia.

## 3. Gerenciamento de Tempo (cronograma)

Ritmo de **Design Sprint semanal** (modelo Google), **Dailies** de alinhamento com o PO e
**Sprint Review aos sábados** com o professor. Mapa detalhado dos dias em
[`agile-process.md`](agile-process.md).

| Sprint | Semana | Foco | Review |
|---|---|---|---|
| **Sprint 1** | 1 | Fundações + firewall + extração estruturada | Sábado, fim da semana 1 |
| **Sprint 2** | 2 | Admissibilidade + orquestrador + persistência + UI mínima | Sábado, fim da semana 2 |

Marcos: **M1** firewall funcional (atingido); **M2** extração ponta-a-ponta; **M3** MVP demonstrável.

## 4. Gerenciamento de Custos

Projeto acadêmico de **baixíssimo custo**, por decisão de arquitetura:

| Item | Estratégia | Custo |
|---|---|---|
| LLM | Gemini Flash (free tier acadêmico) + `FakeProvider` nos testes | ~R$ 0 |
| Infra | Docker local (Postgres+pgvector); sem nuvem no MVP | R$ 0 |
| Modelos ML | Apenas se a TPU entrar (HuggingFace, CPU) — fora do recorte atual | R$ 0 |
| Mão de obra | 8 integrantes (esforço acadêmico) | — |

Guarda de custo de tokens configurável (`SHERPI_LLM_MAX_INPUT_TOKENS`) evita estouro de *free tier*.

## 5. Gerenciamento de Riscos

| # | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| R1 | Escopo não caber em 2 semanas | Alta | Alto | Recorte MVP enxuto; TPU/auth como futuro; firewall já pronto. |
| R2 | Qualidade da extração do LLM (alucinação) | Média | Alto | `temperature=0`, validação de schema com retry, *defensive prompting*, eval. |
| R3 | Dependência de *free tier*/rede do LLM | Média | Médio | `FakeProvider` para dev/testes; guarda de custo; *chunking*. |
| R4 | Dados reais com PII/segredo de justiça (LGPD) | Média | Alto | *Synthetic-first*; port `Anonymizer`; nenhum dado real no MVP. |
| R5 | Metodologia de IA/Design Sprint só na aula de sábado | Alta | Baixo | *Placeholders* prontos; adaptar `agile-process.md` após a aula. |
| R6 | Integração de múltiplos contextos atrasar | Média | Médio | Orquestrador explícito simples; *ports* desacoplam modelo de sistema. |

## 6. Gerenciamento de Recursos e Equipe

8 integrantes; papéis detalhados em [`agile-process.md`](agile-process.md). Pilares exigidos pelo Guia:
- **Product Owner (PO)** — escopo do **produto**: lidera o Backlog do Produto e valida requisitos nas Dailies.
- **Gerente de Projeto (GP)** — escopo do **projeto**: mantém este PGP e garante o andamento das entregas.

## 7. Gerenciamento de Comunicação

| Canal | Uso | Cadência |
|---|---|---|
| Dailies | Alinhamento com o PO, remoção de impedimentos | Diária |
| Sprint Review | Validação com o professor | Sábados |
| Quadro Kanban (GitHub Projects) | Fluxo de tasks e WIP | Contínuo |
| Repositório Git (branch `development`) | Código, docs, histórico | Contínuo |

## 8. Gerenciamento de Qualidade

*Definition of Done* transversal: código + testes passando; `ruff`/`mypy` limpos; documentação
atualizada; e — para itens de modelo — **métrica medida** no *eval* (nunca prometida). Gate de
qualidade no CI (lint + type + testes + eval). Detalhes em [`tech-spec-sherpi.md`](tech-spec-sherpi.md).

## 9. Partes interessadas

| Parte | Interesse |
|---|---|
| Professor (avaliador) | Aderência ao processo ágil, artefatos e MVP funcional. |
| Cliente simulado (gabinete) | Redução do tempo de triagem; segurança contra fraude algorítmica. |
| Equipe | Aprendizado de ágil aplicado a IA; entrega no prazo. |
