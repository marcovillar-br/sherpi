---
title: "ADR-0004: PostgreSQL + pgvector"
description: "PostgreSQL + pgvector — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0004 — PostgreSQL + pgvector como único sistema de persistência

**Status**: Aceito

## Contexto

O SHERPI precisa de dados relacionais (análises, usuários, auditoria) **e** de busca por similaridade vetorial (k-NN sobre embeddings do seed TPU). Manter dois sistemas (um relacional + um vector store dedicado) adicionaria complexidade operacional desnecessária a um MVP.

## Decisão

Usar **PostgreSQL + extensão pgvector** como único sistema, cobrindo relacional e embeddings. Acesso via **SQLModel** (reusa os contratos Pydantic do domínio) e **Alembic** (migrations). Blobs de PDF ficam atrás do port `BlobStorage` (LocalFS no MVP → S3/MinIO na Fase 4).

## Consequências

**Positivas**

- Um só sistema com estado para operar, fazer backup e versionar (Alembic).
- SQLModel reaproveita os VOs/contratos Pydantic, reduzindo duplicação.
- pgvector cobre o k-NN da TPU sem um vector DB separado.

**Negativas / trade-offs**

- pgvector pode não escalar como vector stores especializados em volumes muito grandes; reavaliar na Fase 4 se necessário.
- Acopla a busca vetorial ao Postgres; trocar exigiria novo adapter de índice (`TpuIndex`), já previsto como port.
