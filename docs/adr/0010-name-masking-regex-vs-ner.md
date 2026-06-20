---
title: "ADR-0010: Mascaramento de nomes por âncora (regex) vs NER"
description: "Anonimização de nomes das partes antes do LLM: heurística regex por âncora no MVP; NER (Presidio) como evolução."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-20
language: pt-BR
tags: [adr, seguranca, lgpd, anonimizacao]
---

# ADR 0010 — Mascaramento de nomes por âncora (regex) vs NER

**Status**: Aceito

## Contexto

O `RegexAnonymizer` mascara identificadores **estruturados** (CPF, CNPJ, e-mail, telefone, CEP) antes de enviar o texto ao LLM externo. Mas **nomes** de pessoas/empresas não são um padrão estrutural — e estavam indo ao LLM em claro, um risco LGPD relevante em produção com peças reais.

Detecção robusta de nomes normalmente exige **NER** (Named Entity Recognition). A opção avaliada foi o **Microsoft Presidio** (`AnalyzerEngine` com modelo spaCy `pt_core_news_sm` + `AnonymizerEngine`), já presente como adapter opcional (`PresidioAnonymizer`, extra `ner`). Trade-offs:

| | Regex por âncora | NER (Presidio) |
|---|---|---|
| Cobertura | nomes na **qualificação** (perto de cues) | nomes em **qualquer lugar** (contextual) |
| Custo | O(n), **zero dependências** | spaCy/modelo (~100s MB), inferência mais lenta |
| Determinismo | total | probabilístico (falsos pos/neg) |
| Instalação | nenhuma | `uv sync --extra ner` + download do modelo |

Em petições, os nomes das partes aparecem em **posições previsíveis**: imediatamente antes de marcadores de qualificação ("brasileiro", "pessoa jurídica", "inscrito no CPF") ou logo após "em face de". Isso permite uma heurística determinística de baixo falso-positivo.

## Decisão

Adotar, no MVP, o **`RegexNameAnonymizer`**: mascara por **âncora** o nome adjacente aos marcadores de qualificação → `[NOME]`. Composto com o `RegexAnonymizer` via `CompositeAnonymizer`, controlado pela flag `anonymize_names` (default ligado), ativo só quando o LLM é externo. Não altera veredito nem admissibilidade (que usam o texto **original**).

O **NER (Presidio)** fica como **evolução** (Fase 4), para cobrir nomes em texto livre quando a operação com peças reais exigir cobertura completa.

## Consequências

**Positivas**

- Fecha o vazamento principal de PII de nomes (as partes) a custo zero e de forma determinística.
- Sem dependências pesadas nem download de modelo; rápido e testável.

**Negativas / limitações**

- **Best-effort**: nomes citados livremente nos fatos (fora das âncoras) podem não ser mascarados; raramente pode mascarar a mais.
- Mitigação atual: *synthetic-first* (dados fictícios) + revisão humana. Para produção com peças reais, reavaliar a adoção do Presidio (ADR futuro registraria a troca).
