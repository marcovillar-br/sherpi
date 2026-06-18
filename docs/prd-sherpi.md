---
title: "Documento de Requisitos de Produto (PRD)"
description: "Visão, problema, personas, histórias de usuário, escopo e métricas do SHERPI."
doc_type: prd
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [produto, requisitos, personas, metricas]
---

# PRD — SHERPI

**Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais**

| Campo | Valor |
|---|---|
| Documento | Documento de Requisitos de Produto (PRD) |
| Versão | 1.0 |
| Status | Aprovado para POC |
| Natureza | MVP acadêmico (pós-graduação) — prova de conceito em 3 semanas + roadmap de produção |
| Última atualização | 2026-06-17 |

---

## 1. Visão e proposta de valor

O SHERPI é um sistema de apoio à triagem de petições iniciais cíveis para gabinetes e secretarias do Judiciário brasileiro. Ele recebe o PDF de uma petição inicial e devolve, em segundos, três insumos para a decisão humana:

1. Um **laudo de integridade do documento** que detecta tentativas de *prompt injection* (comandos ocultos no PDF dirigidos a sistemas de IA) **antes** de qualquer envio do texto a um modelo de linguagem.
2. Um **resumo estruturado** da petição (partes, fato gerador, fundamentação, pedidos, pedido de liminar, valor da causa) acompanhado de um **checklist de admissibilidade** baseado nos arts. 319 e 321 do CPC.
3. Uma **sugestão de classificação TPU** (Tabelas Processuais Unificadas do CNJ): as três classes/assuntos mais prováveis, com grau de confiança.

A proposta de valor é **devolver tempo cognitivo** ao magistrado e à sua equipe: reduzir o tempo de leitura/triagem de peças prolixas, antecipar a necessidade de emenda à inicial e padronizar a autuação — sempre como **apoio**, nunca como decisão automática. O diferencial técnico do produto é o **firewall anti prompt-injection**: um controle determinístico que ataca uma ameaça concreta e recente, ainda sem solução de mercado consolidada.

### O que o SHERPI **não** é

- Não é um sistema de decisão automática. Toda saída é uma sugestão sujeita à supervisão humana obrigatória (*human-in-the-loop*).
- Não é um classificador "pronto" com acurácia garantida. A classificação TPU é construída sobre embeddings + k-NN e tem acurácia **medida e reportada honestamente**, não prometida.
- Não é, no POC, uma integração com o PJe/E-Proc. A ingestão é por upload manual de PDF.

---

## 2. Problema (diagnóstico)

O Judiciário brasileiro opera sob pressão de demanda sem paralelo. O relatório de pesquisa (`sherpi-deep-research-v1.md`) identifica três gargalos na porta de entrada do processo, todos atacados pelo SHERPI.

### 2.1 Litigiosidade e sobrecarga

Segundo o *Justiça em Números 2025* (ano-base 2024, CNJ), dos vinte maiores réus do país dez são entes públicos, somando **6,84 milhões de ações pendentes** (~8,5% do acervo nacional). O INSS isoladamente figura no polo passivo de mais de **4,2 milhões de processos**. Tribunais de médio/grande porte registram cargas extenuantes — no TJSC, **8.011 processos por magistrado** em 2024. O resultado é uma triagem manual massiva de demandas repetitivas.

### 2.2 Defeitos de admissibilidade e retrabalho

Levantamentos indicam que **até 60% das petições iniciais** em algumas varas cíveis e juizados apresentam vícios estruturais (ausência de procuração válida, falta de comprovante de residência, omissão de memória de cálculo, pedidos incompatíveis com os fatos). Cada vício dispara o ciclo do art. 321 do CPC: despacho de emenda → intimação → nova petição → nova leitura integral. É a "indústria do retrabalho" que infla a taxa de congestionamento. Soma-se a isso a **prolixidade** — petições de 49 a 116 páginas para questões simples (caso paradigmático no RN, Proc. 0100222-69.2014.8.20.0125, em que o juiz classificou a inicial de 49 páginas como "um livro").

### 2.3 Prompt injection em PDFs (a nova ameaça)

Com a adoção de ferramentas de IA generativa para leitura de PDFs, surgiu a fraude por **prompt injection**: inserção de comandos imperativos ocultos no PDF para induzir o LLM a produzir resumos falsos ou a recomendar concessões indevidas. Há casos concretos documentados:

- **3ª Vara do Trabalho de Parauapebas (PA), 13/05/2026** — primeira punição registrada; advogadas inseriram comandos em fonte branca sobre fundo branco, invisíveis ao humano mas extraíveis pelo parser. Multa por litigância de má-fé (arts. 5º e 77 do CPC).
- **Foro Central Cível de São Paulo (Proc. 4050201-45.2025.8.26.0100)** — petição de banco réu com instruções ocultas dirigidas a sistemas automáticos; juiz exigiu explicações sob pena de acionar OAB e Corregedoria.

Essa fraude aniquila o contraditório (a contraparte não pode impugnar o que não enxerga) e torna impraticável a supervisão humana exigida pela **Resolução CNJ 615/2025**: o magistrado não consegue revisar um viés injetado por texto que ele fisicamente não vê na tela.

---

## 3. Personas

| Persona | Perfil | Dores | Como o SHERPI ajuda |
|---|---|---|---|
| **Magistrado(a)** | Responsável pela decisão final; sobrecarregado; precisa enxergar o essencial de cada peça e detectar urgências e fraudes. | Tempo de leitura de peças prolixas; risco de não enxergar pedido de liminar oculto; risco de viés por conteúdo manipulado que não consegue ver. | Resumo estruturado com destaque para liminar; laudo de integridade tornando visível o que estava oculto. |
| **Assessor(a) de gabinete** | Minuta despachos e decisões; faz a leitura analítica das peças sob delegação do juiz. | Extração manual de requisitos do art. 319 em meio a "juridiquês" e cópia de jurisprudência; retrabalho na emenda. | Extração de partes/fatos/fundamentação/pedidos + checklist de admissibilidade que antecipa a necessidade de emenda. |
| **Servidor(a) de triagem** | Recebe, autua e classifica a petição na TPU; identifica urgências. | Classificação TPU complexa (6 níveis) e frequentemente errada pelo advogado; leitura integral só para autuar. | Sugestão top-3 de TPU e alerta de liminar, reduzindo a triagem analógica. |

---

## 4. Histórias de usuário

**Triagem e integridade**

- Como **servidor de triagem**, quero submeter o PDF de uma petição e receber um laudo de integridade, para barrar peças com comandos ocultos antes que cheguem à análise de IA ou ao gabinete.
- Como **magistrado**, quero que o sistema me mostre, em destaque, qualquer texto oculto detectado no PDF, para que eu possa fundamentar eventual multa por litigância de má-fé.

**Extração e admissibilidade**

- Como **assessor**, quero um resumo estruturado da petição (partes, fato gerador, fundamentação, pedidos, valor da causa), para não precisar ler dezenas de páginas de citações já conhecidas.
- Como **assessor**, quero um checklist de admissibilidade (art. 319/321 do CPC) com semáforo, para decidir rapidamente se é caso de emenda à inicial.
- Como **magistrado**, quero um alerta destacado quando houver pedido de tutela de urgência/liminar, para priorizar o feito e evitar perecimento de direito.

**Classificação**

- Como **servidor de triagem**, quero ver as três classes TPU mais prováveis com grau de confiança, para autuar corretamente sem ter de ler a peça inteira.

**Supervisão e auditoria**

- Como **magistrado**, quero registrar minha decisão de revisão (aceitar/rejeitar/corrigir) sobre cada sugestão do sistema, para manter o controle humano e uma trilha auditável conforme a Resolução CNJ 615/2025.
- Como **usuário autenticado**, quero acessar o sistema com login obrigatório, para que cada ação fique vinculada à minha identidade na trilha de auditoria.

---

## 5. Escopo

### 5.1 Dentro do escopo (POC)

- Upload manual de PDF de petição inicial.
- Firewall anti prompt-injection determinístico (PyMuPDF, sem LLM).
- Extração estruturada via LLM (provider injetável; default Gemini Flash).
- Checagem de admissibilidade híbrida (validadores determinísticos + extração semântica).
- Sugestão TPU (embedding JurisBERT + k-NN sobre seed rotulado).
- Orquestração explícita: integridade → [BLOCK?] → extração → admissibilidade → TPU.
- Persistência das análises (PostgreSQL + pgvector).
- Autenticação obrigatória (OAuth2 password + JWT, perfil único).
- Registro de revisão humana e trilha de auditoria append-only.
- Frontend Next.js: login, viewer de PDF, painel de extração, laudo de segurança.
- Dados **sintéticos primeiro** (synthetic-first) com injeções plantadas para avaliação.
- Eval harness com métricas reportadas honestamente.

### 5.2 Fora do escopo (POC) → Fase 4

- Integração com PJe/E-Proc.
- Autorização granular (RBAC), MFA, refresh tokens.
- Detecção de litigância predatória por análise de rede/clustering entre processos.
- Processamento de documentos anexos (procuração, comprovantes) por OCR/visão computacional.
- Execução assíncrona/fila para escala; containerização completa; deploy gerenciado.
- Storage de blobs em S3/MinIO; criptografia em repouso; política de retenção/DPIA.

---

## 6. Não-objetivos

- **Não** decidir automaticamente sobre admissão, emenda, liminar ou classificação. O SHERPI sugere; o humano decide.
- **Não** substituir o juízo de admissibilidade — apenas instruí-lo.
- **Não** prometer métricas de mercado (ex.: "90% de acurácia na TPU"). Métricas são metas a medir no eval.
- **Não** processar PII real de processos sob segredo de justiça no POC (synthetic-first).
- **Não** acoplar o sistema a um fornecedor específico de LLM.

---

## 7. Métricas de sucesso

As métricas abaixo são **metas a medir** no eval harness sobre o dataset sintético rotulado, não promessas.

| Capacidade | Métrica | Meta inicial (a calibrar) |
|---|---|---|
| Firewall | Precision / Recall na detecção de injeções plantadas (por vetor) | Recall alto nos vetores cobertos; falsos positivos baixos |
| Firewall | Tempo de análise por documento | Ordem de milissegundos a poucos segundos, sem chamada LLM |
| Extração | F1 por campo (partes, pedidos, valor da causa, flag de liminar) | Reportado por campo; sem alucinação de campos ausentes |
| Admissibilidade | Acurácia do checklist vs. ground truth (art. 319) | Validadores determinísticos: exatos; extração semântica: medida |
| TPU | Acurácia top-1 e top-3 sobre o seed | Reportada honestamente, **sem prometer número** |
| Produto | Tempo de triagem humano com vs. sem SHERPI (teste comparativo) | Redução mensurável do tempo de leitura/extração |

---

## 8. Riscos e considerações ética/legais

| Risco | Descrição | Mitigação |
|---|---|---|
| **Decisão automática indevida** | Tratar a saída do sistema como decisão, violando o devido processo. | Invariante de domínio "nunca decisão automática"; *human-in-the-loop* obrigatório; registro de revisão; UI que rotula tudo como sugestão. |
| **Vazamento de PII (LGPD)** | Envio de dados pessoais das partes a LLM externo (Gemini). | Synthetic-first no POC; port `Anonymizer` (mascara CPF/CNPJ/nomes/endereços) antes do envio; sem PII em log. Fase 4: opção de LLM local, criptografia, retenção. |
| **Segredo de justiça** | Processamento de peças sigilosas. | Dados sintéticos no POC; em produção, classificação de sigilo e LLM on-prem para sensíveis. |
| **Falso negativo do firewall** | Vetor de injeção não coberto pela heurística passa despercebido. | Firewall é heurístico e não pega tudo — combinado a *defensive prompting* (texto tratado como dado, não instrução) em defesa em profundidade; eval por vetor. |
| **Falso positivo do firewall** | Bloquear peça legítima (ex.: ruído de digitalização). | Verdito gradual `BLOCK/WARN/PASS` com `risk_score`; revisão humana; calibração no eval. |
| **Viés/erro da TPU e da extração** | Sugestão incorreta induzindo autuação errada. | Apresentação como sugestão com confiança; top-3 (não top-1 forçado); supervisão humana; acurácia medida. |
| **Conformidade CNJ 615/2025** | Falta de transparência/auditabilidade do uso de IA. | Trilha de auditoria append-only vinculada a usuário autenticado; supervisão humana obrigatória; laudo de integridade explicável. |

---

## 9. Referências

- `docs/sherpi-deep-research-v1.md` — relatório de pesquisa (diagnóstico, vetores de injeção, proposta de MVP).
- `docs/tech-spec-sherpi.md` — especificação técnica.
- `docs/roadmap.md` — roadmap idea→produção.
- `docs/threat-model.md` / `docs/security.md` — segurança.
- Resolução CNJ 615/2025; CPC/2015 (arts. 319, 321, 330); LGPD (Lei 13.709/2018).
