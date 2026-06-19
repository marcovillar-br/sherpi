---
title: "Glossário Jurídico — Conceitos do Escopo"
description: "Primer dos principais conceitos jurídicos do SHERPI, em linguagem acessível, para validação com especialista."
doc_type: reference
project: SHERPI
status: draft
version: 1.1
updated: 2026-06-19
language: pt-BR
tags: [juridico, glossario, cpc, clt, conceitos, validacao]
---

# Glossário Jurídico — Conceitos do Escopo (SHERPI)

> **Para que serve:** dar ao time **não-jurista** uma base acessível dos conceitos que o produto
> manipula, para **confirmar com um(a) advogado(a)/especialista**. **Não é parecer jurídico** — foi
> redigido com apoio de IA; os itens marcados **⚠️ confirmar** merecem validação humana. Base: CPC/2015
> (Lei 13.105), CLT, e leis específicas citadas.

## 1. A petição inicial e seus requisitos (art. 319 do CPC)

A **petição inicial** é a peça que dá início ao processo (o autor provoca o Judiciário). O art. 319
lista o que ela deve conter:

| Inc. | Conceito | Em linguagem simples | No SHERPI |
|---|---|---|---|
| I | **Juízo** a que é dirigida | o "endereçamento": a vara/juízo competente | extraído (`juizo`) e checado |
| II | **Qualificação das partes** | quem são autor e réu (nome, **CPF/CNPJ**, endereço…) | `partes` + validação de CPF/CNPJ |
| III | **Fatos e fundamentos jurídicos** (*causa de pedir*) | o que aconteceu **e** o porquê jurídico | `fato_gerador` + `fundamentacao` |
| IV | **Pedido** com especificações | o que se requer ao juiz | `pedidos` |
| V | **Valor da causa** | quanto vale economicamente a ação | `valor_causa` |
| VI | **Provas** | como pretende provar os fatos | `requer_provas` |
| VII | **Opção por audiência** de conciliação/mediação | sim/não para tentar acordo | `opcao_audiencia` |

- **Documentos indispensáveis (art. 320):** acompanham a inicial (ex.: **procuração**, contrato,
  comprovantes). ⚠️ *confirmar quais documentos são "indispensáveis" por tipo de ação.*

## 2. Pedido: qualidades e cumulação

- **Pedido certo e determinado (arts. 322–324):** o pedido deve ser claro e específico (o que, quanto).
- **Pedido líquido:** pedido com **valor definido**. ⚠️ *No cível é regra geral o pedido certo/determinado;
  no **trabalhista** a exigência de pedido com **indicação de valor** (líquido) é mais forte — confirmar.*
- **Cumulação de pedidos (art. 327):** vários pedidos numa só ação. Requer compatibilidade entre eles,
  mesmo juízo competente e mesmo rito. ⚠️ *muito comum no trabalhista (cumulação massiva) — confirmar
  requisitos de compatibilidade.*
- **Tutela de urgência / liminar (art. 300) e tutela de evidência (art. 311):** decisão **provisória e
  imediata** (antes do fim do processo) quando há **probabilidade do direito** + **perigo de dano**.
  No SHERPI: `tem_liminar` (alerta prioritário). ⚠️ *confirmar distinção urgência × evidência.*

## 3. Admissibilidade: o que acontece se faltar algo

- **Admissibilidade:** juízo preliminar se a inicial preenche os requisitos para seguir.
- **Emenda à inicial (art. 321):** havendo defeito/falta, o juiz manda **corrigir em 15 dias**.
- **Indeferimento da inicial (art. 330):** se não corrigida (ou vício insanável), a inicial é
  **rejeitada** (extinção sem resolução de mérito). No SHERPI: o `AdmissibilityReport` sinaliza
  semáforo (verde/amarelo/vermelho) e `requer_emenda`. ⚠️ *confirmar quais vícios são "essenciais"
  (exigem emenda) vs. menores.*

## 4. Partes e papéis

- **Autor / Reclamante:** quem propõe a ação (no trabalhista, "reclamante").
- **Réu / Reclamada:** contra quem se propõe (no trabalhista, "reclamada").
- **Polo ativo / passivo:** lado de quem pede (ativo = autor) e de quem é demandado (passivo = réu).

## 5. Domínios da Justiça (ritos) e suas diferenças

O SHERPI **é multi-domínio** desde a Sprint 3 (ver [ADR-0008](adr/0008-multi-domain-architecture.md)). Cada domínio
tem **regras de admissibilidade próprias**:

| Domínio | Base legal | Diferença-chave | ⚠️ Confirmar |
|---|---|---|---|
| **Cível** | CPC art. 319 | requisitos gerais | escopo das varas cíveis |
| **Trabalhista** | CLT **art. 840 §1º** | **pedido líquido** (com valor); cumulação massiva | exigência exata de liquidez pós-reforma trabalhista |
| **Previdenciário** (INSS) | CPC + Lei 8.213 | exige **prévio requerimento administrativo** | Tema 350 do STF (RE 631.240) e exceções |
| **Execução fiscal** | Lei 6.830 (LEF) | baseia-se na **CDA** (certidão de dívida ativa); não há "fatos" clássicos | requisitos da petição de execução fiscal |
| **Família** | CPC + Código Civil/ECA | alimentos, guarda; **segredo de justiça** | particularidades de rito |

## 6. Fenômenos que o produto combate

- **Prolixidade:** petições longas e repetitivas (citação excessiva de jurisprudência) que dificultam
  a leitura. O SHERPI resume.
- **Litigância predatória (*sham litigation*):** ajuizamento massivo e abusivo de ações sem lastro
  fático (petições padronizadas, fragmentação de demandas). ⚠️ *confirmar critérios de caracterização
  (ex.: Recomendação CNJ 159/2024).*
- **Prompt injection em PDF:** **conceito técnico** — comandos ocultos no PDF (texto branco no branco,
  fonte minúscula, metadados) que tentam enganar a IA que lê a peça. Juridicamente, pode configurar
  **litigância de má-fé** (arts. 5º, 77, 80 do CPC). ⚠️ *confirmar enquadramento e o caso de Parauapebas.*

## 7. Conformidade, dados e taxonomia

- **TPU — Tabelas Processuais Unificadas (CNJ):** padronização nacional de **classe** e **assunto**
  processual (Res. CNJ 46/2007 e 326/2020). O SHERPI sugerirá a classificação. ⚠️ *confirmar níveis
  hierárquicos e a base oficial vigente.*
- **Resolução CNJ 615/2025:** regula o uso de **IA no Judiciário**, exigindo **supervisão humana**
  (*human-in-the-loop*). Implementado na Sprint 4: `ReviewDecision` (ACEITAR/REJEITAR/CORRIGIR) +
  `AuditEvent` append-only vinculado ao usuário autenticado. ⚠️ *confirmar exigências aplicáveis a uma ferramenta como o SHERPI.*
- **Segredo de justiça:** processos com acesso restrito por sigilo legal (ex.: família, dados
  sensíveis) — motiva o uso de dados **sintéticos** no projeto.
- **LGPD (Lei 13.709):** proteção de dados pessoais (CPF, nomes, endereços das partes) — motiva a
  **anonimização** de identificadores estruturados (CPF/CNPJ/e-mail/telefone/CEP) antes de enviar
  texto a um LLM externo (`MappedRegexAnonymizer`); anonimização de **nomes** via NER disponível
  como extra opcional (`PresidioAnonymizer`, `--extra ner`) desde a Sprint 6.

---

## Checklist para o(a) especialista validar

1. Os requisitos do art. 319 estão corretamente interpretados (esp. III "fundamentos jurídicos" vs. mérito)?
2. Quais vícios devem **exigir emenda** (essenciais) e quais são **menores**?
3. **Pedido líquido** no trabalhista (CLT 840 §1º): qual o nível exato de exigência hoje?
4. **Cumulação de pedidos** (art. 327): requisitos de compatibilidade que valem checar automaticamente?
5. **Previdenciário:** como tratar o prévio requerimento administrativo (Tema 350 STF) e exceções?
6. **Execução fiscal:** quais requisitos da inicial verificar (CDA, etc.)?
7. **Litigância predatória** e **prompt injection**: enquadramento jurídico e sinais a sinalizar.
8. **TPU** e **Res. CNJ 615/2025**: fontes oficiais e exigências aplicáveis.
