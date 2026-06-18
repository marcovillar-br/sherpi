---
title: "ADR-0001: DDD modular monolith + hexagonal"
description: "DDD modular monolith + hexagonal — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0001 — DDD modular monolith + hexagonal (ports & adapters)

**Status**: Aceito

## Contexto

O SHERPI integra capacidades heterogêneas (inspeção de PDF, LLM, embeddings, persistência vetorial, auth) e precisa ser **LLM-agnóstico** e testável sem rede. Um MVP acadêmico de 2 semanas não justifica microsserviços, mas o código precisa ser organizado de forma que sobreviva à Fase 4 (produção). O requisito original fala em "skills modulares".

## Decisão

Adotar um **monólito modular orientado a DDD** com **arquitetura hexagonal (ports & adapters)**. O código é organizado por **bounded context** (`document_integrity`, `petition_analysis`, `taxonomy`, `review`, `identity`), cada um em camadas `domain` → `application` → `infrastructure`. O **domínio é puro** (sem FastAPI, SQL, PyMuPDF ou SDK de LLM). Toda dependência externa é um **port** no domínio/aplicação e um **adapter** na infraestrutura. Cada "skill" do requisito vira uma capacidade de um contexto (domain service ou use case) atrás de um port.

## Consequências

**Positivas**

- LLM-agnóstico de fato: trocar provider = trocar adapter, sem tocar no domínio.
- Domínio testável sem rede (FakeProvider, validadores puros).
- Fronteiras claras facilitam evoluir para serviços na Fase 4 (ex.: integração PJe como novo contexto).
- Regras de negócio (art. 319/321, checksum CPF/CNPJ) isoladas e auditáveis.

**Negativas / trade-offs**

- Mais cerimônia e indireção (ports/adapters) do que um script único — custo aceitável para um sistema que vai a produção.
- Curva de aprendizado de DDD/hexagonal para quem mantém o MVP.
