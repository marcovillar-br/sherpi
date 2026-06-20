---
title: "Plano de Gerenciamento do Projeto (PGP / PMP)"
description: "Escopo, tempo, custos, riscos, equipe, comunicação e qualidade do projeto SHERPI."
doc_type: pmp
project: SHERPI
status: approved
version: 1.2
updated: 2026-06-19
language: pt-BR
tags: [gerenciamento-de-projeto, pgp, pmp, escopo, riscos, cronograma]
---

# Plano de Gerenciamento do Projeto (PGP / PMP) — SHERPI

Documento sob responsabilidade do **Gerente de Projeto (GP)**, focado no **escopo do projeto**.
Complementa o backlog (responsabilidade do PO, [`backlog.md`](backlog.md)) e a
[`wbs.md`](wbs.md). Conforme o Guia de Diretrizes da disciplina.

## 1. Identificação

| Campo | Valor |
|---|---|
| Projeto | **SHERPI** — Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais |
| Disciplina | Desenvolvimento Ágil para Projetos de IA (DAIA) |
| **Formato da entrega** | **MVP** (sistema funcional, com código implementado e executável) |
| Duração | **MVP em 2 Sprints** + **Fase 4** em 7 sprints (3–9); **Sprints 1–9 entregues** |
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

### 2.3 Escopo da Fase 4 (pós-MVP, agendado em sprints)
Com o MVP entregue, as capacidades adiadas foram **agendadas em sprints** por importância/ganho:
domínio trabalhista + rito-aware (Sprint 3, ✅), identidade + revisão/auditoria (Sprint 4, ✅),
classificação TPU (Sprint 5, ✅), hardening de produção — observabilidade/LGPD pleno/deploy (Sprint 6, ✅),
integração PJe/E-Proc (Sprint 7, ✅), UI das Sprints 4–7 (Sprint 8, ✅) e refactor en-US/compliance (Sprint 9, ✅). Detalhe das histórias/tasks em [`backlog.md`](backlog.md);
objetivos e DoD em [`roadmap.md`](roadmap.md).

> A divisão escopo-completo (produto) × escopo-de-execução (sprint) segue formalizada no backlog,
> conforme exigência do Guia.

## 3. Gerenciamento de Tempo (cronograma)

Ritmo de **Design Sprint semanal** (modelo Google), **Dailies** de alinhamento com o PO e
**Sprint Review aos sábados** com o professor. Mapa detalhado dos dias em
[`agile-process.md`](agile-process.md).

| Sprint | Foco | Status |
|---|---|---|
| **Sprint 1** | Fundações + firewall + extração estruturada | ✅ entregue |
| **Sprint 2** | Admissibilidade + orquestrador + persistência + UI mínima | ✅ entregue |
| **Sprint 3** | **Domínio Trabalhista (CLT 840) + arquitetura rito-aware** (foco do grupo) | ✅ entregue |
| **Sprint 4** | Confiança & Conformidade: `identity` (JWT) + `review` (human-in-the-loop + auditoria) | ✅ entregue |
| **Sprint 5** | Classificação TPU (`taxonomy`) por ramo: JurisBERT + k-NN/numpy | ✅ entregue |
| **Sprint 6** | Produção: observabilidade, LGPD pleno (NER), deploy/CI-CD | ✅ entregue |
| **Sprint 7** | Integração PJe/E-Proc (ingestão assíncrona) | ✅ entregue |
| **Sprint 8** | UI das Sprints 4–7: login, seletor de rito, TPU top-3, revisão humana | ✅ entregue |
| **Sprint 9** | Refactor de nomenclatura en-US (EP12): identificadores Python, enums, prompts e frontend | ✅ entregue |
| *(pós-9)* | Domínios adicionais: previdenciário/INSS, execução fiscal, família/JEC (encaixes rito-aware) | backlog |

Marcos: **M1** firewall (✅); **M2** MVP (✅); **M3** trabalhista (✅); **M4** identity+review (✅); **M5** TPU (✅); **M6** produção (✅); **M7** integração (✅); **M8** UI completa (✅); **M9** en-US compliance (✅). Detalhe em [`roadmap.md`](roadmap.md).

## 4. Gerenciamento de Custos

Projeto acadêmico de **baixíssimo custo**, por decisão de arquitetura:

| Item | Estratégia | Custo |
|---|---|---|
| LLM | Gemini Flash (free tier acadêmico) + `FakeProvider` nos testes | ~R$ 0 |
| Infra | Docker local (PostgreSQL 16); sem nuvem no MVP | R$ 0 |
| Modelos ML | TPU na Sprint 5: JurisBERT via HuggingFace, inferência em CPU | R$ 0 |
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
| R7 | (Fase 4) Falta de *dataset* rotulado petição→TPU | Alta | Alto | Seed sintético rotulado; k-NN sobre embeddings (não exige fine-tuning); acurácia medida e reportada honestamente. |
| R8 | (Fase 4) NER de nomes (PII) com baixa precisão | Média | Médio | Manter *synthetic-first*; Presidio/spaCy + revisão; anonimização estrutural (regex) já cobre CPF/CNPJ. |
| R9 | (Fase 4) Acesso a PJe/E-Proc (credenciais/sandbox) indisponível | Alta | Médio | Adapter atrás de port; usar homologação/sandbox; manter upload manual como fallback. |

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
