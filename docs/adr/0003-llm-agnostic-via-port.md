---
title: "ADR-0003: Camada LLM-agnóstica via port"
description: "Camada LLM-agnóstica via port — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0003 — LLM-agnóstico via port `LLMProvider`

**Status**: Aceito

## Contexto

O relatório acoplava o sistema a modelos específicos (gpt-4o-mini, Gemini 1.5 Flash) hardcodados. Modelos datam rápido, e o projeto quer poder trocar entre Gemini, Maritaca Sabiá, OpenAI-compat e Ollama — inclusive um provider local para dados sensíveis (LGPD). Os testes não podem depender de rede.

## Decisão

Definir um port `LLMProvider` na fronteira domínio/aplicação, com a assinatura `complete(messages, response_schema) -> objeto validado`. Implementar adapters em `infrastructure/llm`:

- `gemini.py` (**default**, SDK google-genai), `grok.py` (xAI) e `anthropic.py` (Sonnet) — estes dois via httpx direto sobre a base `HttpLLMProvider`, sem SDK — e `fake.py` (`FakeProvider` determinístico).

Provider e modelo vêm de `config.py` (pydantic-settings/.env), nunca hardcodados.

## Consequências

**Positivas**

- Troca de LLM sem tocar no domínio; suporte a LLM local na Fase 4 sem refatoração.
- Testes determinísticos e offline com `FakeProvider`.
- Sem dependência de SDK específico vazando para o domínio.

**Negativas / trade-offs**

- O port é o menor denominador comum: features específicas de um provider (ex.: caching nativo, tool use proprietário) ficam fora do contrato comum ou exigem extensão do port.
- Necessário manter mais de um adapter atualizado.
