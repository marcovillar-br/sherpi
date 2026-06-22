---
title: "ADR-0009: k-NN em numpy/bytes (revisa o ADR-0004)"
description: "Embeddings TPU como bytes (numpy/float32) + k-NN em Python, sem a extensão pgvector."
doc_type: adr
project: SHERPI
status: accepted
version: 1.1
updated: 2026-06-22
language: pt-BR
tags: [adr, arquitetura, decisao, tpu]
---

# ADR 0009 — k-NN em numpy/bytes para a TPU (revisa o ADR-0004)

**Status**: Aceito — substitui o [ADR-0004](0004-postgres-pgvector.md) **na parte de busca vetorial**; a decisão relacional (PostgreSQL único para análises/usuários/auditoria) permanece válida.

## Contexto

O [ADR-0004](0004-postgres-pgvector.md) previu a extensão **pgvector** para cobrir o k-NN dos embeddings do seed TPU. Na implementação, o índice opera sobre um **conjunto-semente** de poucas dezenas/centenas de vetores — escala em que uma busca vetorial linear em memória é trivial e exata. Introduzir a extensão pgvector (tipo `Vector`, índice IVFFlat/HNSW, `CREATE EXTENSION`) traria dependência operacional e de build sem ganho prático nessa escala, além de divergir do banco de testes (SQLite), que não tem a extensão.

## Decisão

- Embeddings persistidos como **bytes** (`numpy.float32` via `tobytes()` / `np.frombuffer`) em coluna binária comum, em SQLite (test) e PostgreSQL (dev/prod).
- **k-NN em Python/numpy** dentro do adapter `SqlTpuIndex`: busca linear exata em memória (produto matriz × vetor de consulta), com **ranking híbrido** — similaridade densa (cosseno) combinada a um sinal **léxico/IDF** (peso `_LEXICAL_WEIGHT`) e **dedupe por `tpu_code`** antes do top-k (ver [ADR-0016](0016-cnj-tua-real-catalog-tpu.md)).
- **Sem** a extensão pgvector e **sem** a dependência Python `pgvector`.
- O **PostgreSQL** segue como sistema relacional único (a parte do ADR-0004 que continua valendo).

## Consequências

**Positivas**

- Zero dependência da extensão pgvector (build e operação mais simples; sem `CREATE EXTENSION`).
- A imagem Docker do banco passa a ser **`postgres:16`** puro (a variante `pgvector/pgvector` deixa de ser necessária); o volume de dados é compatível (mesmo PostgreSQL 16).
- Portável: a mesma lógica roda em SQLite e PostgreSQL, o que mantém os testes sem rede/extensões.
- Exato e suficiente para a escala do seed; o port `TpuIndex` isola a escolha do índice.

**Negativas / trade-offs**

- Busca linear **não escala** para grandes volumes. Quando o seed crescer (ou em produção com base ampla), reavaliar pgvector (IVFFlat/HNSW) ou um vector store dedicado — troca contida no adapter `TpuIndex`, **sem tocar no domínio**.
- Embeddings ficam opacos ao SQL (são bytes), sem consultas vetoriais no banco.
