---
title: "ADR-0016: TPU 1.0 sobre a TUA real do CNJ (substitui o seed sintético)"
description: "Adotar a Tabela Única de Assuntos oficial do CNJ (escopo cível+trabalhista) como catálogo da classificação TPU, com texto de embedding híbrido (glossário > caminho > descrição LLM) e eval rotulado; mantém o k-NN numpy."
doc_type: adr
project: SHERPI
status: proposed
version: 1.0
updated: 2026-06-21
language: pt-BR
tags: [adr, tpu, taxonomy, cnj, embeddings, jurisbert]
---

# ADR 0016 — TPU 1.0 sobre a TUA real do CNJ

**Status**: Proposto · **Revisa** [ADR-0009](0009-knn-numpy-bytes.md) (motor k-NN) e o seed
sintético da Sprint 5

## Contexto

A classificação TPU do MVP indexa um **seed sintético de 30 entradas** (15 cível + 15
trabalhista, `synthetic/tpu_seed.py`). Em uso real, as sugestões saem **incoerentes** porque
a classe correta simplesmente **não existe no catálogo**. Exemplo medido (petição de acidente
de trânsito com pedido de danos materiais): o top-1 vinha "Obrigação de Fazer" — a TUA tem o
assunto exato **"Responsabilidade Civil > Indenização por Dano Material > Acidente de
Trânsito"**, ausente do seed.

Antes deste ADR, dois consertos já entraram (e seguem válidos): query da TPU a partir do
mérito extraído (não do texto bruto); JurisBERT ligado de fato (antes rodava
`FakeEmbeddingModel` por hash em produção). Mas o gargalo de **cobertura** permanece.

### Spike de viabilidade (medido, não estimado)

Protótipo de ingestão (`scripts/fetch_tpu_cnj.py`) baixou a TUA oficial via webservice SOAP
do SGT/CNJ (`pesquisarItemPublicoWS`) e mediu:

- **TUA inteira: 5.601 assuntos** (22 ramos de topo).
- **Escopo SHERPI** (Direito Civil + Consumidor + Previdenciário → CIVEL; Trabalho →
  TRABALHISTA): **1.569 nós / 1.326 folhas** (566 cível + 1.003 trabalhista).
- Indexando as folhas com JurisBERT usando o **caminho hierárquico** como texto de embedding,
  o caso de acidente passa a trazer a classe correta **no top-3** (era lixo). Mas os scores
  ficam **amontoados** (72–75%): JurisBERT-STS separa mal rótulos curtos de taxonomia, e
  irmãos que dividem o prefixo (ex.: "...Dano Material > Atraso na Entrega do Imóvel")
  competem de igual; casos mais difíceis (consignado fraudulento) não cravam top-1.
- O webservice também devolve `dscGlossario` (descrição oficial do assunto) — texto rico,
  ideal para embeddar — mas presente em **apenas 37%** das folhas do escopo.

## Decisão

Para a 1.0 mini, **substituir o seed sintético pela TUA real do CNJ**, escopada a
cível+trabalhista, mantendo a arquitetura de ports (não há mudança no orquestrador):

1. **Ingestão** (feito — protótipo): `scripts/fetch_tpu_cnj.py` baixa a TUA via SGT,
   reconstrói a árvore, filtra o escopo e emite catálogo (`cod_item`, `nome`, `rito`,
   `is_leaf`, `path`, `glossario`). Re-sync manual (a TUA é versionada pelo CNJ).
2. **Texto de embedding híbrido** (pendente): `glossario` quando houver (37%, alta
   qualidade); senão o `path` hierárquico (baseline); descrição gerada por **LLM** para as
   folhas de **alta frequência** sem glossário (custo de geração modesto, revisão por
   amostragem). O texto é o que mais move a acurácia — não o motor.
3. **Motor k-NN inalterado** (revisita o ADR-0009 e confirma): brute-force numpy/bytes
   aguenta 1.326×768 com folga (<10 ms, poucos MB). FAISS/pgvector só se um dia indexar a
   TUA inteira (~5,6k) ou múltiplos ramos — desnecessário agora.
4. **Eval rotulado** (pendente, dá credibilidade): conjunto petição→assunto para medir
   top-1/top-3/top-5; sem ele não se afirma acurácia. Reportar honestamente (sem número
   prometido), como já faz o MVP.
5. **UX de confiança/rejeição** (pendente): com ~1,3k classes e scores amontoados, calibrar
   limiar e tratar "nenhuma classe próxima"; manter top-3/top-5 e o aviso de revisão humana.

## Consequências

**Positivas**
- As classes corretas passam a **existir** no catálogo (provado para o caso de acidente).
- Sem mudança de arquitetura: troca-se a **fonte de dados** (seed → TUA) e o **texto de
  embedding**; ports `EmbeddingModel`/`TpuIndex` e o orquestrador ficam intactos.
- Escala dominada: escopo + Pareto domam os 5,6k; o motor atual basta.

**Negativas / trade-offs**
- Re-seed embeda 1.326 folhas (vs 30) — minutos em CPU, uma vez por versão da TUA.
- `glossario` cobre só 37% — o item 2 (texto híbrido) é trabalho real, não "carregar CSV".
- Baixo contraste semântico em rótulos curtos: top-1 confiável exige glossário/descrição +
  eval + calibração; **top-3/top-5** é a promessa realista.
- Manutenção: re-sync com as versões da TUA do CNJ.
- Multi-assunto: a TPU admite vários assuntos por processo — a v1 fica em top-k simples;
  multi-label fica para depois (registrar se mudar).

## Itens pendentes (ordem sugerida)
1. Texto de embedding híbrido + re-seed a partir do catálogo real.
2. Eval rotulado petição→assunto (top-1/top-3/top-5).
3. UX de confiança/rejeição.
