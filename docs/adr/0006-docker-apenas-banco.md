---
title: "ADR-0006: Docker apenas para o banco"
description: "Docker apenas para o banco — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0006 — Docker apenas para o banco de dados

**Status**: Aceito

## Contexto

Containerizar tudo (backend, frontend, banco) num POC de 3 semanas atrasa o desenvolvimento e prejudica o hot reload. Mas o banco é uma dependência com estado que precisa ser reproduzível entre máquinas.

## Decisão

Usar **docker-compose apenas para Postgres+pgvector** (e MinIO opcional). Backend (uv) e frontend (npm) rodam **nativos** em dev, com hot reload. Containerização completa fica para a **Fase 4**.

## Consequências

**Positivas**

- Setup de dev rápido; hot reload de backend e frontend.
- Banco reproduzível e descartável via `docker compose up -d`.
- Menos overhead de build durante o desenvolvimento.

**Negativas / trade-offs**

- O ambiente de dev não é idêntico ao de produção (sem container para app) — divergência aceitável no POC, resolvida na Fase 4 com containerização completa e CI/CD.
- Exige Python/Node instalados localmente para rodar a aplicação.
