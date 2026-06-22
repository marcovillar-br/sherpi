---
title: "Governança de IA — Model Card e Conformidade CNJ 615/2025"
description: "Cartão do sistema de IA do SHERPI (uso pretendido, modelos, métricas, limitações, supervisão humana) e matriz de conformidade com a Resolução CNJ 615/2025."
doc_type: ai-governance
project: SHERPI
status: draft
version: 1.0
updated: 2026-06-22
language: pt-BR
tags: [ia, governanca, model-card, cnj-615, conformidade, human-in-the-loop]
---

# Governança de IA — SHERPI

> **Não é parecer jurídico.** Documento de governança de IA, redigido com apoio de IA. A **Parte A**
> é um *Model/System Card* (cartão do sistema de IA); a **Parte B** mapeia a **Resolução CNJ 615/2025**
> (uso de IA no Judiciário) à implementação. Referências de artigo marcadas **⚠️ confirmar** dependem
> de validação jurídica contra o texto oficial. Complementa [`dpia.md`](dpia.md) (privacidade),
> [`security.md`](security.md) e [`tech-spec-sherpi.md`](tech-spec-sherpi.md).

| Campo | Valor |
|---|---|
| Sistema | SHERPI — triagem assistida de petições iniciais |
| Versão do sistema | MVP (Sprints 1–9) + TPU 1.0 |
| Status | Rascunho (pendente de validação jurídica) |
| Última atualização | 2026-06-22 |

---

# Parte A — Model/System Card

## A.1 Visão geral e propósito

O SHERPI **apoia** (não substitui) a triagem de petições iniciais por um servidor do Judiciário.
Combina componentes **determinísticos** e de **IA**, sempre sob **supervisão humana obrigatória**:

| Componente | Tipo | É "IA generativa"? |
|---|---|---|
| Firewall anti *prompt-injection* | Determinístico (PyMuPDF/python-docx) | **Não** — heurística forense |
| Extração/resumo estruturado | **LLM** via port agnóstico | **Sim** |
| Admissibilidade rito-aware | Determinístico + semântico | Parcial (valida saída do LLM) |
| Classificação TPU | **Embedding + k-NN** (recuperação) | Não-generativa (similaridade) |

## A.2 Uso pretendido

- **Usuários**: servidores/assessores de triagem autenticados (perfil único no MVP).
- **Uso pretendido**: resumir, sinalizar requisitos de admissibilidade e **sugerir** classificação —
  como **insumo** a uma decisão **humana**.
- **Fora do escopo / usos vedados**:
  - ❌ **decisão automatizada** sobre admissão/indeferimento (o sistema **não decide**);
  - ❌ uso como peça/decisão judicial sem revisão humana;
  - ❌ tratamento de **dados pessoais reais** sem as mitigações de Fase 4 (ver [dpia.md](dpia.md));
  - ❌ domínios de **dado sensível** (previdenciário/família) ainda não habilitados.

## A.3 Modelos subjacentes

- **LLM (extração)**: **agnóstico por configuração** ([ADR-0003](adr/0003-llm-agnostic-via-port.md)) —
  default **Gemini 2.5 Flash**; **Grok 4** (xAI) e **Claude Sonnet 4.6** (Anthropic) trocáveis; `Fake`
  para testes. Chamado com **`temperature=0`**, saída **validada por schema com retry**.
- **Embedding (TPU)**: `juridics/jurisbert-base-portuguese-sts` (JurisBERT), local; índice **k-NN** sobre
  a **TUA real do CNJ** com **ranking híbrido** (denso + lexical) e **limiar de confiança 0.65**
  ([ADR-0016](adr/0016-cnj-tua-real-catalog-tpu.md), [ADR-0009](adr/0009-knn-numpy-bytes.md)).
- **Treinamento**: o SHERPI **não treina nem faz fine-tuning** de modelos. Usa modelos **pré-treinados**
  + recuperação (k-NN). Não há aprendizado a partir dos dados dos usuários.

## A.4 Dados

- **Corpus do MVP**: **sintético** (synthetic-first) — sem PII real.
- **Índice TPU**: catálogo oficial da **TUA/CNJ** (assuntos cível/trabalhista).
- **Texto enviado ao LLM**: **pseudonimizado** quando o provedor é externo (ver [dpia.md](dpia.md)).

## A.5 Avaliação e métricas

Há um **harness de avaliação versionado** (`make eval`, `backend/evals/`). As métricas e seus **gates**
(não os valores de uma execução pontual, que devem ser obtidos rodando o eval):

| Capacidade | Métrica | Gate / parâmetro |
|---|---|---|
| Firewall | precision / recall / f1 por vetor | `MIN_PRECISION` / `MIN_RECALL` em `evals/run.py` |
| TPU (seed) | acurácia **top-1 / top-3** | sobre o próprio seed |
| TPU (rotulado) | acerto **top-1 / top-3 / top-5** | conjunto rotulado sobre a TUA real (`evals/tpu_labeled_set.json`) |
| Extração | validação de schema + retry | saída malformada é rejeitada |

> **Honestidade metodológica:** os números concretos saem de `make eval` no ambiente; este card
> documenta **o que** se mede e **o limiar**, não cola valores que envelhecem. Reproduza antes de citar.

## A.6 Limitações e modos de falha conhecidos

| Limitação | Efeito | Mitigação |
|---|---|---|
| Firewall é **heurístico** | Pode não pegar todo vetor de injeção | Defesa em profundidade (*defensive prompting*); eval por vetor; risco aceito |
| Masking de nomes é **best-effort** (regex por âncora) | Nome citado **livremente nos fatos** pode vazar ao LLM | Synthetic-first; NER (Presidio) na Fase 4 ([ADR-0010](adr/0010-name-masking-regex-vs-ner.md)) |
| LLM pode **alucinar/errar** extração | Resumo impreciso | **Human-in-the-loop**; `temperature=0`; validação de schema |
| **Sem OCR** | PDF imagem/escaneado não é analisado | Sinalizado e **não** segue ao LLM (sem laudo "íntegro" falso); OCR é Fase 4 |
| Sugestão TPU pode errar a folha | Classificação inadequada | **Limiar de confiança**; top-3 ao humano; nunca auto-aplica |
| Possíveis **vieses do LLM** | Saída enviesada | Sem decisão automatizada; revisão humana; troca de provedor |

## A.7 Supervisão humana, transparência e auditabilidade

- **Human-in-the-loop obrigatório** (invariante de domínio "nunca decisão automática").
- **Auditoria append-only** das revisões (`AuditEvent` vinculado ao usuário) e **das chamadas ao LLM**
  (prompt pseudonimizado + resposta), consultáveis na UI — transparência do que foi de fato enviado.
- **Interpretabilidade**: o resumo é estruturado e rastreável ao texto; a admissibilidade aponta o
  requisito/artigo; a TPU mostra o trecho-âncora e a confiança.

## A.8 Segurança, privacidade e manutenção

- Segurança/privacidade: ver [`security.md`](security.md), [`threat-model.md`](threat-model.md) e o
  RIPD/DPIA ([`dpia.md`](dpia.md)).
- **Versionamento**: mudanças de modelo/prompt/limiar são decisões registradas em **ADR**; reavaliar
  este card a cada troca de provedor de LLM, mudança de prompt de extração ou do catálogo TPU.

---

# Parte B — Conformidade com a Resolução CNJ 615/2025

A Res. CNJ 615/2025 disciplina o **uso de IA no Judiciário**. A matriz abaixo mapeia seus **princípios**
à implementação do SHERPI. As **referências de artigo** são indicativas e marcadas **⚠️ confirmar**
até validação contra o texto oficial.

| Princípio (Res. CNJ 615/2025) | Como o SHERPI atende | Evidência no código/docs | Lacuna / Fase 4 |
|---|---|---|---|
| **Supervisão humana** (*human-in-the-loop*) | Nenhuma decisão automatizada; humano sempre decide/revisa | `contexts/review/`; invariante de domínio | — |
| **Transparência e explicabilidade** | Resumo estruturado, requisito/artigo na admissibilidade, trecho-âncora + confiança na TPU | tech-spec §2; UI | Explicações mais ricas |
| **Auditabilidade / prestação de contas** | Auditoria **append-only** de revisões **e** de chamadas ao LLM | `security.md` §5; `AuditEvent`; `PersistingLLMProvider` | Tracing distribuído (Fase 4) |
| **Não discriminação / equidade** | Sem decisão automatizada; revisão humana; provedor trocável | A.6, A.7 | Avaliação formal de viés ⚠️ |
| **Segurança da informação** | Firewall, JWT, validação de upload, supply-chain gate | `threat-model.md`; `security.md` | RBAC/MFA, cripto repouso (Fase 4) |
| **Proteção de dados (LGPD)** | Synthetic-first; pseudonimização pré-LLM; RIPD | [dpia.md](dpia.md); ADRs 0010/0012 | NER, cripto repouso, expurgo agendado |
| **Confiabilidade / robustez** | `temperature=0`, schema+retry, circuit breaker, degradação graciosa, eval | `security.md` §4; `evals/` | Monitoramento contínuo |
| **Rastreabilidade de decisões de IA** | Prompt e resposta persistidos por análise; revisão registrada | `PersistingLLMProvider`; auditoria | — |
| **Vedação à substituição do julgador** | Sistema é **insumo de triagem**, não decide mérito | A.2 (usos vedados) | Registrar na política de adoção |
| **Governança e responsabilização** | ADRs registram decisões; este card + RIPD | `docs/adr/`, este doc, dpia.md | DPO/comitê na adoção ⚠️ |

> **Escopo de validação.** Esta matriz cobre os **princípios estruturantes** da resolução. O mapeamento
> **artigo-a-artigo** e a aderência a exigências específicas (ex.: catalogação/registro do modelo,
> classificação de risco do sistema) devem ser confirmados com a área jurídica do órgão adotante.

---

## Apêndice — rastreabilidade

| Tema | Onde |
|---|---|
| LLM agnóstico / provedores | `infrastructure/llm/`, [ADR-0003](adr/0003-llm-agnostic-via-port.md), [ADR-0005](adr/0005-gemini-flash-default.md) |
| TPU (embedding/k-NN, limiar) | `contexts/taxonomy/`, [ADR-0016](adr/0016-cnj-tua-real-catalog-tpu.md), [ADR-0009](adr/0009-knn-numpy-bytes.md) |
| Human-in-the-loop / auditoria | `contexts/review/`, [security.md](security.md) §5 |
| Harness de avaliação | `backend/evals/` (`make eval`) |
| Privacidade / LGPD | [dpia.md](dpia.md), [security.md](security.md), [threat-model.md](threat-model.md) |
