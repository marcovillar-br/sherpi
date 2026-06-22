---
title: "ADR-0014: Prompt de extração rito-neutro (reforça o 0008)"
description: "Manter o prompt de extração agnóstico ao rito (cível/trabalhista), citando CPC 319 e CLT 840 lado a lado, em vez de ramificar o prompt por rito."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-20
language: pt-BR
tags: [adr, extracao, prompt, rito, llm]
---

# ADR 0014 — Prompt de extração rito-neutro

**Status**: Aceito · **Reforça** [ADR-0008](0008-multi-domain-architecture.md)

## Contexto

O prompt de extração (`EXTRACTION_SYSTEM_PROMPT`, em
`petition_analysis/application/extract.py`) abria com *"petições iniciais **cíveis**
brasileiras"* e ancorava os requisitos formais **apenas no art. 319 do CPC**. Isso o
deixava **mais estreito que o próprio schema**: o `PetitionSummary` já é compartilhado
entre ritos e `Pedido.amount` cita explicitamente o **pedido líquido trabalhista**
(CLT 840 §1º). Numa reclamatória trabalhista (endereçada à Vara do Trabalho, sem "valor
da causa" no mesmo sentido, com pedido líquido obrigatório), as deixas literais cíveis do
prompt não se aplicam e o modelo tende a extrapolar ou esvaziar campos.

Ao revisar o prompt, considerou-se **ramificá-lo por rito** (núcleo comum + addendum
cível/trabalhista, selecionado pelo `rito` já conhecido no orquestrador). Mas a
[ADR-0008](0008-multi-domain-architecture.md) já decidiu que **o firewall e a extração são
agnósticos ao rito** — o que varia por rito é a **admissibilidade** (estratégias por
domínio) e a TPU, não a extração. Ramificar o prompt contradiria essa decisão e
introduziria no caminho de extração um acoplamento ao rito que a arquitetura
deliberadamente evita.

## Decisão

Manter **um único** prompt de extração, **rito-neutro**, sem threading de `rito` para
`ExtractPetition` (reforço da ADR-0008). Concretamente:

1. Abertura genérica: *"petições iniciais brasileiras (rito cível ou trabalhista)"*.
2. Requisitos formais citam **CPC art. 319 e CLT art. 840 lado a lado** — `court`
   reconhece Vara Cível, Juizado Especial **ou** Vara do Trabalho; nota de que no
   trabalhista o pedido costuma ser líquido (CLT 840 §1º).
3. A diferença legal entre ritos (ex.: pedido líquido **obrigatório**) permanece onde a
   ADR-0008 a colocou: na **admissibilidade rito-aware**, não na extração.

Na mesma revisão (v2→v3 do prompt), reforços de **completude** ortogonais ao rito —
ignorar artefatos de formulário não preenchidos, não listar documentos apenas *sugeridos*,
restringir `parties` às partes formalmente qualificadas e preservar **verbatim** os
marcadores de PII pseudonimizada (`[NOME_1]`/`[CPF_2]`) para a restauração da
[ADR-0012](0012-reversible-anonymization-restore.md).

## Consequências

**Positivas**
- Extração e schema voltam a ficar **coerentes**; um só prompt cobre cível e trabalhista.
- **Nenhum acoplamento** novo ao rito no caminho de extração — fiel à ADR-0008
  (open/closed: novo rito = nova estratégia de admissibilidade, prompt intocado).
- Menos superfície a versionar: não há N prompts por rito para manter em sincronia.

**Negativas / trade-offs**
- Um prompt genérico é **menos específico** que um dedicado por rito — aceitável porque a
  extração só registra o que está **explícito**; a checagem rito-específica é da
  admissibilidade.
- Ao adicionar ritos de objeto muito distinto (ex.: execução fiscal — CDA, sem "fatos"
  clássicos), o prompt rito-neutro pode precisar de **revisão**; se a divergência crescer,
  esta decisão deve ser **reavaliada** (eventual addendum por rito), registrando-se novo ADR.
