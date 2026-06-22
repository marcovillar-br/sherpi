---
title: "ADR-0015: claims de extração restritos ao mérito (exclui pedidos procedimentais)"
description: "Restringir o campo claims do PetitionSummary aos pedidos de mérito, excluindo pedidos procedimentais/instrumentais (citação, audiência, gratuidade), que já têm campo próprio ou não são tutela de mérito."
doc_type: adr
project: SHERPI
status: accepted
version: 1.1
updated: 2026-06-22
language: pt-BR
tags: [adr, extracao, prompt, claims, tpu, llm]
---

# ADR 0015 — claims restritos ao mérito

**Status**: Aceito · **Refina** [ADR-0014](0014-rito-neutral-extraction-prompt.md) (prompt v3→v4)

## Contexto

O prompt de extração (`EXTRACTION_SYSTEM_PROMPT`, em
`petition_analysis/application/extract.py`) instruía a incluir em `claims` "apenas pedidos
formalmente formulados (seção de pedidos/requerimentos)". A seção de pedidos de uma inicial
brasileira mistura, no mesmo bloco, **dois tipos** de requerimento:

- **de mérito** — a tutela jurisdicional pleiteada contra a parte contrária (condenação,
  pagamento, indenização, obrigação de fazer, declaração, rescisão);
- **procedimentais/instrumentais** — citação/intimação da parte contrária, designação ou
  realização de audiência (conciliação/mediação/instrução), concessão de gratuidade da
  justiça, prioridade na tramitação, protesto genérico por produção de provas.

Como o prompt não os distinguia, requerimentos procedimentais entravam em `claims`. Numa
auditoria real (cenário `clean_cobranca_..._v1`), o pedido de "citação ... para comparecer à
Audiência de Conciliação ... sob pena de revelia" foi extraído como um claim — tecnicamente
"formalmente formulado", porém **sem conteúdo de mérito**.

Dois problemas decorrem disso:

1. **Lista poluída**: o revisor vê boilerplate processual misturado à tutela pleiteada.
2. **Sinal da TPU degradado**: a sugestão de TPU passou a compor sua query a partir do mérito
   extraído (`facts + legal_basis + claims`, ver o commit `feat(tpu): query a partir do
   mérito extraído`). Um claim procedimental injeta ruído no embedding e pode deslocar o
   ranking de classe/assunto.

Vários desses requerimentos, ademais, **já são capturados em campos próprios** do
`PetitionSummary`: audiência → `hearing_option`; produção de provas → `requests_evidence`;
tutela de urgência/liminar → `has_injunction`. Duplicá-los em `claims` é redundante.

## Decisão

Restringir `claims` aos **pedidos de mérito**. No prompt (v4), a regra de `claims` passa a:

1. Definir claim como a **tutela de mérito** pleiteada contra a parte contrária.
2. **Excluir** explicitamente os pedidos procedimentais/instrumentais (citação/intimação,
   audiência, gratuidade da justiça, prioridade na tramitação, protesto genérico por provas).
3. Apontar o **campo próprio** de cada requerimento já modelado (`hearing_option`,
   `requests_evidence`, `has_injunction`) — a tutela de urgência, quando tiver conteúdo de
   mérito próprio, ainda pode ser registrada em `claims` com `type=INJUNCTION`.

Mudança **só de prompt** — o schema `PetitionSummary` e o `ClaimType` permanecem intactos.
A extração segue **rito-neutra** (ADR-0014): a distinção mérito × procedimento é comum a
cível e trabalhista, não ramifica por rito.

> **Nota (evolução posterior).** A decisão acima firmou a versão **v4** do prompt. O prompt
> seguiu evoluindo de forma ortogonal a esta decisão — hoje em **v5** (`extract.py`: proíbe
> placeholders-lixo como "null"/"N/A"). É refinamento de robustez, não muda o critério
> mérito-only aqui registrado; por isso não há novo ADR. A versão corrente vive no código.

## Consequências

**Positivas**
- `claims` reflete a tutela pleiteada; o revisor lê a pretensão sem boilerplate processual.
- **Sinal da TPU mais limpo**: a query (que consome `claims`) deixa de carregar requerimentos
  procedimentais — reforça a melhoria do `feat(tpu)`.
- Sem redundância: cada requerimento procedimental fica no seu campo booleano próprio.

**Negativas / trade-offs**
- É um critério **semântico** (mérito × procedimento) confiado ao LLM; casos de fronteira
  (ex.: honorários sucumbenciais, custas) podem variar. Aceitável: a regra prioriza a tutela
  contra a parte contrária e a extração só registra o que está explícito.
- Quem quiser auditar pedidos procedimentais não os encontrará em `claims`; se isso virar
  requisito, modela-se um campo dedicado (novo ADR), em vez de poluir `claims`.
