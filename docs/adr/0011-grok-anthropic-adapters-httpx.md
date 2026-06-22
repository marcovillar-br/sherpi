---
title: "ADR-0011: Adapters Grok (xAI) e Anthropic (Sonnet) via httpx; remoção do openai"
description: "Adapters de LLM alternativos ao Gemini implementados com httpx direto sobre uma base comum; remoção da dependência órfã openai e do backend stub openai_compat."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-20
language: pt-BR
tags: [adr, llm, adapters, arquitetura]
---

# ADR 0011 — Adapters Grok (xAI) e Anthropic (Sonnet) via httpx

**Status**: Aceito

## Contexto

O SHERPI é LLM-agnóstico via o port `LLMProvider` ([ADR-0003](0003-llm-agnostic-via-port.md)),
com **Gemini Flash** como default ([ADR-0005](0005-gemini-flash-default.md)). A alternativa
originalmente prevista era a **Maritaca Sabiá** por um adapter genérico `openai_compat`, que **nunca
foi implementado**: a factory apenas levantava erro, e a dependência `openai` (`openai>=1.54`) estava
no `pyproject` mas **não era importada em lugar nenhum** (dep órfã).

A direção do projeto mudou: as alternativas desejadas passaram a ser **Grok (xAI)** e **Claude
Sonnet (Anthropic)**. Era preciso implementá-las de fato, mantendo a invariante de domínio (o texto
vai **anonimizado** ao LLM externo) e a resiliência já exigida (timeout, retry/backoff, guarda de
custo), sem inflar dependências.

## Decisão

Implementar dois adapters reais, **via httpx direto (sem SDK)**, sobre uma base comum:

- **`HttpLLMProvider`** — base que concentra o que independe do provedor: guarda de custo, timeout e
  retry com backoff; cada provider concreto implementa só a montagem do payload e o parsing.
- **`GrokProvider`** — a API do Grok é **OpenAI-compatível** (`/chat/completions`); saída estruturada
  via `response_format: { type: "json_schema" }`.
- **`AnthropicProvider`** — a **Messages API** não tem JSON nativo; saída estruturada via **tool-use**
  forçado (uma tool cujo `input_schema` é o JSON Schema esperado + `tool_choice`).

A factory passa a aceitar `llm_backend ∈ {gemini, grok, anthropic, fake}` (remoção de `openai_compat`),
com **modelo-default por backend** (`grok-4-latest`, `claude-sonnet-4-6`) quando `SHERPI_LLM_MODEL`
não é trocado. Ambos entram no wiring real (`build_llm_provider`) envoltos pelos decorators
`CircuitBreakerLLMProvider → PersistingLLMProvider → LoggingLLMProvider`, e são tratados como **LLM
externo** (`is_external_llm`), logo a anonimização LGPD se aplica. A dependência `openai` é
**removida** do `pyproject`/`uv.lock`.

**Alternativas consideradas:**

- *SDK `openai` apontado para a xAI* (Grok) — rejeitado: reintroduz justamente a dep que se quer remover.
- *SDK oficial `anthropic`* — rejeitado: dependência adicional, sendo que `httpx` já é dep do projeto e basta.
- *Manter o `openai_compat` genérico* — rejeitado: config morta (nunca implementada, nunca usada).

## Consequências

**Positivas**

- Dois providers alternativos **reais e trocáveis por configuração**, sem nenhuma dependência nova.
- Resiliência consistente (a base `HttpLLMProvider` é compartilhada).
- Menos superfície de dependência: remove a dep órfã `openai` (e `jiter`, transitiva).

**Negativas / limitações**

- Falar HTTP direto significa **manter manualmente** o formato de payload/headers e a versão da API
  (`anthropic-version`) de cada provedor.
- A saída estruturada foi validada com **httpx mockado**; em uso real, o modo `json_schema` estrito do
  Grok pode exigir ajuste de schema (`additionalProperties`). Mitigação: o schema é enviado sem `strict`
  e o retry + validação Pydantic cobrem divergências (mesma estratégia do adapter Gemini).
- Grok e Anthropic são **pagos** (sem free tier como o Gemini); por isso Gemini permanece default.
