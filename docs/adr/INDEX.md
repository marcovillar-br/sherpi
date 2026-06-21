---
title: "Índice de ADRs"
description: "Lista das decisões de arquitetura (Architecture Decision Records)."
doc_type: adr-index
project: SHERPI
status: reference
version: 1.6
updated: 2026-06-21
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
| [0002](0002-explicit-orchestrator-vs-langgraph.md) | Orquestrador Python explícito em vez de LangGraph | ✅ Aceito |
| [0003](0003-llm-agnostic-via-port.md) | Camada LLM-agnóstica via port `LLMProvider` | ✅ Aceito |
| [0004](0004-postgres-pgvector.md) | PostgreSQL + pgvector (relacional + embeddings) | 🔄 Substituído por 0009 (busca vetorial) |
| [0005](0005-gemini-flash-default.md) | Google Gemini Flash como LLM default | ✅ Aceito |
| [0006](0006-docker-db-only.md) | Docker apenas para o banco; app nativa em dev | ✅ Aceito |
| [0007](0007-auth-jwt-single-profile.md) | Autenticação JWT com perfil único (extensível a RBAC) | ✅ Aceito |
| [0008](0008-multi-domain-architecture.md) | Arquitetura multi-domínio (rito-aware): estratégias de admissibilidade por rito | ✅ Aceito |
| [0009](0009-knn-numpy-bytes.md) | k-NN em numpy/bytes (revisa o 0004): embeddings sem extensão pgvector | ✅ Aceito |
| [0010](0010-name-masking-regex-vs-ner.md) | Mascaramento de nomes por âncora (regex) no MVP; NER (Presidio) na Fase 4 | ✅ Aceito |
| [0011](0011-grok-anthropic-adapters-httpx.md) | Adapters Grok (xAI) e Anthropic (Sonnet) via httpx; remoção da dep órfã `openai` | ✅ Aceito |
| [0012](0012-reversible-anonymization-restore.md) | Anonimização reversível: restaurar PII real no resumo do revisor (LLM externo só vê o anonimizado) | ✅ Aceito |
| [0013](0013-docx-support-native-firewall.md) | Suporte a .docx com firewall nativo (OOXML via python-docx; reusa o `DetectInjection`) | ✅ Aceito |
| [0014](0014-rito-neutral-extraction-prompt.md) | Prompt de extração rito-neutro (reforça o 0008): CPC 319 + CLT 840 num só prompt, sem ramificar por rito | ✅ Aceito |
| [0015](0015-merit-only-claims-extraction.md) | claims restritos ao mérito (refina o 0014): exclui pedidos procedimentais (citação, audiência, gratuidade), que já têm campo próprio — limpa o sinal da TPU | ✅ Aceito |
| [0016](0016-cnj-tua-real-catalog-tpu.md) | TPU 1.0 sobre a TUA real do CNJ (escopo cível+trabalhista): ingestão via SGT, texto de embedding híbrido (glossário > caminho > LLM), eval rotulado; k-NN numpy mantido | 📝 Proposto |

> Convenção: arquivos nomeados `NNNN-titulo-em-kebab-case.md`, numeração sequencial.
