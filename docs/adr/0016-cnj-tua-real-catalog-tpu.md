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
2. **Texto de embedding híbrido** (feito): **caminho hierárquico SEMPRE + glossário oficial
   quando houver** (combinados, não um ou outro). Diagnóstico mostrou que glossário sozinho
   embeda pior quando é um one-liner fraco, e path sozinho confunde irmãos do mesmo caminho;
   combinar resolveu os dois. Cobertura de glossário é desigual: **cível ~96%**, **trabalhista
   ~4%** (811 folhas só-path). Enriquecimento por **LLM** das folhas trabalhistas só-path fica
   como melhoria **futura e de baixa prioridade** (custo×benefício: o combine grátis já entregou
   o maior ganho; LLM em escala = batch, cobrança por token). O texto é o que mais move a
   acurácia — não o motor.
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

## Progresso

- ✅ Ingestão da TUA + escopo (`scripts/fetch_tpu_cnj.py`).
- ✅ Texto de embedding híbrido (caminho + glossário) + re-seed (`synthetic/tpu_cnj.py`).
- ✅ Eval rotulado (`evals/tpu_labeled.py`). Combine elevou top-1 0.500→0.625 e top-3 0.625→0.750.
- ✅ Dedup da hierarquia paralela trabalhista + caminho canônico (1326→1135 folhas).
- ✅ Embedder explícito (`SHERPI_TPU_EMBEDDER`) + check de dimensão (fim do "sumiço silencioso").
- ✅ **Ranking híbrido denso + léxico/IDF** (`sql_index._lexical_scores`): resgata o assunto cujo
  termo distintivo ("consignado", "indireta") aparece na query mas perde no cosseno puro.
  Consignado e rescisão indireta destravados, sem regressão. Sem custo de LLM (re-ranking em
  tempo de query).
- ✅ Conjunto rotulado ampliado para **n=15** (incl. 4 trabalhistas só-path). Os só-path
  (periculosidade, adicional noturno, intervalo) acertam em #1 — valida o híbrido sem glossário.
  A ampliação pegou um rótulo errado (equiparação apontava p/ nicho "Digitadores").
- ✅ **Dedup por chave normalizada** (`_dedup_key`: minúsculo/sem acento/espaços/pontuação): colapsa
  pares "Salário / Diferença" vs "Salário/Diferença" que escapavam da dedup e ocupavam slots do
  top-k. Índice 1135→**1007**. **Baseline atual: top-1 0.800, top-3 1.000, top-5 1.000** (equiparação
  #5→#3, rescisão indireta #3→#2).

## Itens pendentes (ordem sugerida)
1. UX de confiança/rejeição (limiar + "nenhuma classe próxima").
2. Normalizar o texto da petição ANTES do LLM (colapsar espaços/quebras excedentes da extração
   PDF/DOCX) — reduz tokens e ruído; medir economia e impacto.
3. (Baixa prioridade) Enriquecimento por LLM das folhas trabalhistas só-path (em batch).
