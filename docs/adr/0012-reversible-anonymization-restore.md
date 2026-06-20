---
title: "ADR-0012: Anonimização reversível — restaurar PII no resumo do revisor"
description: "Anonimizar apenas para o LLM externo e restaurar os valores reais no resumo exibido ao revisor humano; consequência de PII em repouso."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-20
language: pt-BR
tags: [adr, lgpd, anonimizacao, seguranca]
---

# ADR 0012 — Anonimização reversível (restaurar PII no resumo do revisor)

**Status**: Aceito

## Contexto

A extração roda sobre o texto **anonimizado** (CPF/CNPJ/nomes → placeholders), para
não vazar PII ao LLM externo ([ADR-0010](0010-name-masking-regex-vs-ner.md)). Efeito
colateral: o `PetitionSummary` voltava com **placeholders** (`[NOME]`/`[CPF]`), e o
**revisor humano** via o resumo mascarado em vez de quem processa quem. A admissibilidade
já usava o texto original (logo, a evidência dela mostrava o documento real) — havia até
**inconsistência** na UI: admissibilidade com dado real, resumo com placeholder.

A anonimização deve proteger o **LLM externo**, não a visão do **revisor autorizado** — o
propósito da ferramenta é apoiar a triagem de peças **reais**.

## Decisão

Tornar a anonimização **reversível** e **restaurar** os valores reais no resumo:

- Port `ReversibleAnonymizer.anonymize_mapped(text) -> (texto, {placeholder: valor})`.
- Placeholders **numerados**: `[CPF_1]`, `[CNPJ_1]`, `[NOME_1]`… (`MappedRegexAnonymizer`
  + `MappedRegexNameAnonymizer`, compostos em `MappedCompositeAnonymizer`).
- O orquestrador: `anonymize_mapped` → extração (LLM vê só placeholders) →
  `deanonymize_model(summary, mapa)` restaura nome/CPF/CNPJ reais em todos os campos do
  resumo.
- O **prompt persistido para auditoria permanece anonimizado** (é o que o LLM viu).

## Consequências

**Positivas**
- O revisor vê o resumo com os **dados reais** (utilidade restaurada), enquanto o LLM
  externo continua recebendo apenas texto anonimizado.
- A trilha de auditoria do LLM continua **sem PII**.

**Negativas / trade-offs**
- O **resumo persistido passa a conter PII** (nomes/CPF/CNPJ). É coerente: a peça real
  tem PII de qualquer forma, e o controle-chave é não vazá-la ao LLM externo. Mitigação:
  acesso ao banco é autenticado (JWT); **criptografia em repouso** fica para a Fase 4.
- A restauração depende de o LLM **preservar os tokens** (`[CPF_1]`) verbatim. Confiável
  em campos copiados (nome/documento da parte); em texto parafraseado (fatos), a maioria
  dos placeholders sobrevive, mas pode haver perda — *best-effort*, alinhado ao ADR-0010.
- Para LLM **local/on-prem** (sem anonimização), o mapa é vazio e a restauração é no-op.
