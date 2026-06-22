---
title: "ADR-0013: Suporte a .docx com firewall nativo (OOXML)"
description: "Aceitar upload de .docx parseando OOXML nativamente (python-docx) e reusando o DetectInjection, em vez de converter para PDF."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-20
language: pt-BR
tags: [adr, firewall, docx, arquitetura]
---

# ADR 0013 — Suporte a .docx com firewall nativo

**Status**: Aceito

## Contexto

O MVP só aceitava **PDF**. Advogados redigem em **.docx** e querem validar a integridade
da peça **antes de gerar o PDF** (pegar texto oculto/injeção ainda no rascunho). Tudo
**depois do parser** (anonimização, extração, admissibilidade, TPU) já é agnóstico ao
formato; o que é PDF-específico são o `guard_upload` e o **firewall**, cujos vetores
(branco-no-branco, fonte minúscula, fora da CropBox, OCG, `/ActualText`, metadados) são de
PDF. O .docx tem **outros** mecanismos de texto oculto (`w:vanish`, cor da fonte, `<w:sz>`
minúsculo, metadados/core properties).

Três caminhos avaliados: **(A)** converter .docx→PDF (LibreOffice) e reusar o pipeline;
**(B)** parser .docx nativo + detecção docx-específica; **(C)** só extrair texto, sem firewall.

## Decisão

Adotar **(B) — parser nativo**. O `DocxParser` (python-docx) produz o **mesmo**
`ParsedDocument` do PDF, populando os atributos de que o detector já depende: cor da fonte,
tamanho, **texto oculto** (`w:vanish` → `in_hidden_ocg`) e metadados (core properties). Com
isso o `DetectInjection` é **reusado quase integralmente** — só as checagens geométricas
(off-cropbox/OCG/`/ActualText`) não se aplicam (DOCX é fluxo, sem coordenadas).

- `detect_format` (magic bytes) + `guard_upload` aceitam PDF/DOCX; `DispatchingParser` roteia.
- Port renomeado `PdfParser` → `DocumentParser`.
- Cobertura v1: corpo, tabelas e cabeçalhos/rodapés.

**Por que não A nem C:** **A** adiciona a dependência pesada do LibreOffice (subprocesso
sobre input hostil) e a conversão **descarta** runs ocultos — muda o artefato analisado.
**C** burla o firewall (o diferencial). **B** inspeciona o .docx como-está, sem dep pesada.

## Consequências

**Positivas**
- Valida a integridade do .docx **antes** do PDF — caso de uso real do advogado.
- Reusa o firewall e todo o pipeline; sem LibreOffice.

**Negativas / limitações**
- **Caixas de texto** (drawing XML) e **cores de tema** ficam fora da cobertura v1 (um nome
  branco via cor de tema, p.ex., não é pego). Texto-em-imagem dentro do .docx idem.
- A heurística reusa `in_hidden_ocg` para o `w:vanish` (o laudo descreve ambos); o nome do
  enum `HIDDEN_OCG_LAYER` permanece por compatibilidade.
- *Zip-bomb*: mitigado por limite de tamanho de upload + teto de parágrafos; isolamento
  pleno fica para a Fase 4 (como no parsing de PDF).
