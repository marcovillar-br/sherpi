---
title: "ADR-0002: Orquestrador explícito vs. LangGraph"
description: "Orquestrador explícito vs. LangGraph — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0002 — Orquestrador Python explícito em vez de LangGraph

**Status**: Aceito

## Contexto

O relatório de pesquisa propunha orquestrar o pipeline com **LangGraph** (StateGraph, multi-agente, loops e ramificações). Porém o fluxo real do SHERPI é **linear com um único early-exit**: integridade → [BLOCK? encerra] → extração → admissibilidade → TPU. Não há loops nem múltiplos agentes cooperando.

## Decisão

Substituir o LangGraph por um **use case Python explícito** (`application/analyze_petition.py`): uma função que chama os contextos em sequência, com um `if` para o early-exit do firewall. O orquestrador vive na camada de aplicação, depende apenas de ports e é testável com `FakeProvider`.

## Consequências

**Positivas**

- Sem lock-in de framework de grafos para um fluxo que não precisa dele.
- Fluxo legível, depurável e totalmente coberto por testes unitários (caminho feliz + BLOCK).
- Menos dependências e menos superfície de manutenção.

**Negativas / trade-offs**

- Se a Fase 4 exigir grafos complexos (loops, múltiplos agentes, retomada de estado), pode ser necessário reintroduzir um orquestrador de grafos. Mitigado por o orquestrador ser uma fronteira isolada, fácil de reimplementar.
