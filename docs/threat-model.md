---
title: "Modelo de Ameaças"
description: "Ativos, atores e mitigações (STRIDE) do SHERPI."
doc_type: threat-model
project: SHERPI
status: approved
version: 1.1
updated: 2026-06-19
language: pt-BR
tags: [seguranca, ameacas, stride, lgpd]
---

# Modelo de Ameaças — SHERPI

| Campo | Valor |
|---|---|
| Documento | Threat Model |
| Versão | 1.1 |
| Status | Aprovado |
| Última atualização | 2026-06-19 |

Modelo de ameaças do SHERPI, derivado da seção "Segurança & Confiabilidade" do plano. Acompanha `security.md` (controles concretos).

---

## 1. Ativos

| Ativo | Sensibilidade | Por quê |
|---|---|---|
| **PDFs de petições** | Alta | Conteúdo não confiável (parser hostil); pode conter injeções e PII. |
| **PII das partes** (CPF/CNPJ, nomes, endereços) | Alta (LGPD) | Dados pessoais; envio a LLM externo é risco regulatório. |
| **Análises persistidas** (resumos, laudos, sugestões TPU) | Média/Alta | Refletem conteúdo processual; base da decisão humana. |
| **Credenciais e tokens** (senha bcrypt, JWT) | Alta | Acesso ao sistema; identidade da trilha de auditoria. |
| **Trilha de auditoria** (`AuditEvent`) | Alta (integridade) | Valor legal (CNJ 615/2025); deve ser append-only. |
| **Chaves de API de LLM** | Alta | Acesso/custo do provider; vazamento gera abuso. |

## 2. Atores de ameaça

| Ator | Motivação |
|---|---|
| **Litigante/advogado mal-intencionado** | Manipular a análise de IA (prompt injection) para obter resumo falso ou liminar indevida. |
| **Atacante externo** | Comprometer credenciais (brute-force), abusar de upload para explorar CVEs do parser. |
| **Insider/operador** | Acesso indevido a PII; manipulação de trilha de auditoria. |
| **Terceiro (LLM provider)** | Exposição inadvertida de PII enviada ao modelo externo. |

---

## 3. Ameaças → vetores → mitigação (STRIDE)

| # | Ameaça (STRIDE) | Vetor | Ativo | Mitigação |
|---|---|---|---|---|
| **T1** | **Tampering** — prompt injection no PDF | Branco-no-branco, fonte <1pt, fora da CropBox, U+200B, OCG oculto, /ActualText, XMP suspeito | Análise de IA | **Firewall determinístico** (PyMuPDF) antes do LLM; verdito `BLOCK` encerra sem chamada ao modelo. Defesa em profundidade: *defensive prompting* (texto como dado, não instrução). Firewall é heurístico → eval por vetor. |
| **T2** | **Denial of Service / Elevation** — upload hostil | PDF malicioso explorando CVEs do parser; bomba de descompressão; PDF gigante | PDFs, disponibilidade | Validação de MIME/tipo e **tamanho máximo**; **limite de páginas**; **timeout e limite de recursos** no parsing; rejeitar não-PDF; tratar PDF como hostil. Fase 4: sandbox de parsing, antimalware, isolamento de processo. |
| **T3** | **Information Disclosure** — vazamento de PII para LLM externo | Texto da petição (com CPF/nomes/endereços) enviado ao Gemini | PII (LGPD) | **Synthetic-first** no MVP; port **`Anonymizer`** mascara identificadores estruturados (CPF/CNPJ/e-mail/telefone/CEP) antes do envio; **nomes** dependem do synthetic-first (NER é Fase 4); **sem PII em log**. Fase 4: NER de nomes, criptografia em repouso, retenção/eliminação, DPIA, LLM local. |
| **T4** | **Spoofing** — abuso de autenticação | Brute-force/credential stuffing no `/auth/login` | Credenciais | **Rate-limit/lockout** no login; bcrypt com custo adequado; JWT com **expiração**; cookie **httpOnly+Secure+SameSite**; erros sem vazar detalhe. Fase 4: MFA, refresh tokens. |
| **T5** | **Repudiation** — negação de ação / adulteração de auditoria | Edição/remoção de registros de revisão | Trilha de auditoria | **Auditoria append-only** vinculada a `User` autenticado; cada `/review` grava `AuditEvent` imutável. |
| **T6** | **Information Disclosure** — vazamento de chave de API/segredos | Segredos no git; em logs | Chaves de LLM | Segredos fora do git (`.gitignore` + só `.env.example`); não logar segredos. Fase 4: secrets manager, secret scanning. |
| **T7** | **Tampering** — injeção de entrada na API | Payloads malformados; XSS via campos | Análises, sessão | Validação Pydantic (→422); CORS restrito ao frontend; proteção CSRF; cookie httpOnly; erros consistentes sem stack trace. |
| **T8** | **Denial of Service** — abuso de custo de LLM | Requisições massivas/peças enormes consumindo tokens | Chaves/custo | **Guarda de custo/tokens** (corta acima do limite); timeout + retry com backoff; circuit breaker simples; degradação graciosa (firewall e TPU funcionam sem LLM). |

---

## 4. Decisões de risco aceitas no MVP

- O firewall é **heurístico** e não cobre todos os vetores possíveis — risco residual aceito, mitigado por defesa em profundidade e eval por vetor.
- Sem RBAC/MFA no MVP — todo usuário autenticado tem o mesmo acesso (ver ADR 0007).
- LLM externo (Gemini) no MVP — risco de PII tratado por synthetic-first + Anonymizer; LLM local fica para a Fase 4.

Controles detalhados e seu faseamento (MVP vs. Fase 4) em `security.md`.
