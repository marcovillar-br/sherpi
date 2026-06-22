---
title: "ADR-0006: Docker apenas para o banco"
description: "Docker apenas para o banco — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.1
updated: 2026-06-22
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0006 — Docker apenas para o banco de dados

**Status**: Aceito

## Contexto

Containerizar tudo (backend, frontend, banco) num MVP de 2 semanas atrasa o desenvolvimento e prejudica o hot reload. Mas o banco é uma dependência com estado que precisa ser reproduzível entre máquinas.

## Decisão

Usar **docker-compose apenas para Postgres 16** (imagem `postgres:16` pura — **sem pgvector**, ver [ADR-0009](0009-knn-numpy-bytes.md); **sem MinIO**). Backend (uv) e frontend (npm) rodam **nativos** em dev, com hot reload. Containerização completa fica para a **Fase 4**.

Esta decisão vale para o **dev** (`docker-compose.yml`, só o serviço `db`). O `docker-compose.prod.yml` já containeriza o backend (`build` + Dockerfile multi-stage) — é o **início da Fase 4**, não contradiz o escopo "só banco" do dev.

## Consequências

**Positivas**

- Setup de dev rápido; hot reload de backend e frontend.
- Banco reproduzível e descartável via `docker compose up -d`.
- Menos overhead de build durante o desenvolvimento.

**Negativas / trade-offs**

- O ambiente de dev não é idêntico ao de produção (sem container para app) — divergência aceitável no MVP, resolvida na Fase 4 com containerização completa e CI/CD.
- Exige Python/Node instalados localmente para rodar a aplicação.
