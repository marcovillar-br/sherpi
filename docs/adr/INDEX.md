---
title: "Índice de ADRs"
description: "Lista das decisões de arquitetura (Architecture Decision Records)."
doc_type: adr-index
project: SHERPI
status: reference
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, index]
---

# Architecture Decision Records (ADRs)

Registro das decisões de arquitetura do SHERPI. Cada ADR segue o formato padrão
(Contexto · Decisão · Consequências) e é imutável após aceito — uma decisão nova
que substitua outra cria um novo ADR que marca o anterior como *Substituído*.

| # | Decisão | Status |
|---|---|---|
| [0001](0001-ddd-hexagonal.md) | DDD modular monolith + hexagonal (ports & adapters) | ✅ Aceito |
| [0002](0002-orquestrador-explicito-vs-langgraph.md) | Orquestrador Python explícito em vez de LangGraph | ✅ Aceito |
| [0003](0003-llm-agnostico-via-port.md) | Camada LLM-agnóstica via port `LLMProvider` | ✅ Aceito |
| [0004](0004-postgres-pgvector.md) | PostgreSQL + pgvector (relacional + embeddings) | ✅ Aceito |
| [0005](0005-gemini-flash-default.md) | Google Gemini Flash como LLM default | ✅ Aceito |
| [0006](0006-docker-apenas-banco.md) | Docker apenas para o banco; app nativa em dev | ✅ Aceito |
| [0007](0007-auth-jwt-perfil-unico.md) | Autenticação JWT com perfil único (extensível a RBAC) | ✅ Aceito |

> Convenção: arquivos nomeados `NNNN-titulo-em-kebab-case.md`, numeração sequencial.
