---
title: "ADR-0005: Gemini Flash como LLM default"
description: "Gemini Flash como LLM default — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0005 — Google Gemini Flash como LLM default

**Status**: Aceito

## Contexto

O SHERPI é LLM-agnóstico (ver ADR 0003), mas precisa de um provider default para o POC. As petições podem ter 100+ páginas, exigindo janela de contexto grande. Sendo um projeto acadêmico, custo é restrição. Maritaca Sabiá é forte em português jurídico, mas fica como adapter para um segundo momento.

## Decisão

Adotar **Google Gemini Flash** como default (`gemini.py`), pela janela de contexto grande (lê petições longas sem chunking agressivo) e pelo free tier acadêmico. **Maritaca Sabiá** fica disponível via `openai_compat.py`, a ser ativada na Fase 4 conforme avaliação comparativa.

## Consequências

**Positivas**

- Contexto grande reduz a necessidade de chunking em peças longas.
- Free tier viabiliza o POC sem custo.
- Default trocável por configuração; Sabiá pronta para avaliação posterior.

**Negativas / trade-offs**

- LLM externo implica enviar texto para fora → mitigado por synthetic-first + port `Anonymizer` (ver ADR 0003 e security.md).
- Free tier tem limites de taxa; tratado com timeout/retry/backoff e guarda de custo.
- Sabiá pode superar o Gemini em português jurídico; por isso a avaliação comparativa na Fase 4.
