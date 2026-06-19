---
title: "ADR-0008: Arquitetura multi-domínio (rito-aware)"
description: "Arquitetura multi-domínio (rito-aware) — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.1
updated: 2026-06-19
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0008 — Arquitetura multi-domínio (rito-aware)

**Status**: Aceito

## Contexto

O SHERPI nasceu focado no **cível** (requisitos do art. 319 do CPC). O grupo definiu o **trabalhista**
como foco principal, e o Judiciário tem outros domínios de **altíssimo volume** (previdenciário/INSS —
maior litigante do país; execução fiscal; família; juizados). Cada domínio tem **regras de
admissibilidade distintas** e taxonomia (TPU) própria:

- **Cível** — CPC art. 319.
- **Trabalhista** — CLT art. 840 §1º, com exigência de **pedido líquido** (certo, determinado e com valor).
- **Previdenciário** — CPC + Lei 8.213 (prévio requerimento/DER, benefício).
- **Execução fiscal** — Lei 6.830 (CDA; sem "fatos" no sentido clássico).

Porém, o **firewall** (anti prompt-injection) e a **extração estruturada** são **agnósticos ao
domínio** — o que varia é a admissibilidade, a TPU e alguns campos. Precisamos suportar vários
domínios **incrementalmente**, sem reescrever o que já existe.

## Decisão

Adotar uma arquitetura **rito-aware** baseada em **estratégias por domínio** (padrão Strategy +
registro), aderente ao DDD/hexagonal já existente:

1. **`Rito`** (enum): hoje `CIVEL` e `TRABALHISTA`; `PREVIDENCIARIO`, `FISCAL`, … previstos (cresce por demanda).
2. **`AdmissibilityStrategy`** (Protocol/Strategy de domínio, em `petition_analysis/domain/strategies.py`):
   cada domínio implementa seu conjunto de regras; o registro **`DEFAULT_STRATEGIES`** mapeia
   `Rito → estratégia`. `CheckAdmissibility` apenas **despacha** para a estratégia do rito.
   O cível atual vira `CivelStrategy`; o **trabalhista** (`TrabalhistaStrategy`, CLT 840 + pedido
   líquido) é a primeira nova estratégia.
3. **Extração compartilhada**: `PetitionSummary` permanece comum, com **campos opcionais** por domínio
   (ex.: `Pedido.valor` para o pedido líquido trabalhista).
4. **Roteamento de rito**: informado na requisição (`rito` no `/v1/analyze`) inicialmente; um
   **classificador automático de rito** fica como evolução futura.
5. **Ordem incremental** (por volume/ganho): Cível ✅ → **Trabalhista** → Previdenciário (INSS) →
   Execução fiscal → Família/JEC. Criminal/eleitoral/militar ficam fora (objeto processual diverso).

## Consequências

**Positivas**
- **Open/closed**: novo domínio = nova estratégia + cenários + (depois) ramo de TPU, **sem tocar** nos
  domínios existentes.
- Reaproveita firewall, extração, persistência, API e anonimização entre todos os domínios.
- Torna explícita a diferença legal entre ritos (ex.: pedido líquido no trabalhista).

**Negativas / trade-offs**
- Exige **roteamento de rito** (informado ou, no futuro, detectado) — risco de classificação errada.
- Cada domínio demanda **dados rotulados próprios** (cenários sintéticos, seed de TPU).
- Mais superfície de regras a manter — mitigado por estratégias **isoladas e testadas** por domínio.

## Errata (2026-06-19)

Esclarecimentos de redação após a implementação na Sprint 3 (**não alteram a decisão**):

- `AdmissibilityStrategy` é um **`Protocol` de domínio** (`@runtime_checkable`) em
  `petition_analysis/domain/strategies.py` — **não** um *port* hexagonal (não há adapter de
  infraestrutura). O termo "port" no item 2 da Decisão era impreciso.
- O registro `Rito → estratégia` é a constante **`DEFAULT_STRATEGIES`** no mesmo módulo.
- O enum `Rito` implementado contém apenas `CIVEL` e `TRABALHISTA`; os demais ritos são previstos.
- A checagem de pedido líquido foi materializada no requisito `Requisito.PEDIDO_LIQUIDO`
  (determinístico, art. 840 §1º).
