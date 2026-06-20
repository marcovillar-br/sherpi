---
title: "Modelo de Ameaças"
description: "Ativos, atores e mitigações (STRIDE) do SHERPI."
doc_type: threat-model
project: SHERPI
status: approved
version: 1.3
updated: 2026-06-20
language: pt-BR
tags: [seguranca, ameacas, stride, lgpd]
---

# Modelo de Ameaças — SHERPI

| Campo | Valor |
|---|---|
| Documento | Threat Model |
| Versão | 1.2 |
| Status | Aprovado |
| Última atualização | 2026-06-20 |

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
| **T1** | **Tampering** — prompt injection no PDF/DOCX | Branco-no-branco, fonte <1pt, fora da CropBox, U+200B, OCG oculto, /ActualText, XMP suspeito; **DOCX**: texto oculto `w:vanish`, cor/tamanho, metadados; **evasão por rasterização** (conteúdo em imagem) | Análise de IA | **Firewall determinístico** (PyMuPDF no PDF, python-docx no DOCX) antes do LLM; verdito `BLOCK` encerra sem chamada ao modelo. PDFs **sem camada de texto** (imagem/escaneado) são sinalizados e **não** seguem para o LLM; páginas **mistas** (texto + imagem dominante) são sinalizadas como conteúdo possivelmente não extraído (não há laudo "íntegro" falso). Defesa em profundidade: *defensive prompting* (texto como dado, não instrução). Firewall é heurístico → eval por vetor. |
| **T2** | **Denial of Service / Elevation** — upload hostil | PDF/DOCX malicioso explorando CVEs do parser; *zip-bomb* (DOCX); arquivo gigante | Documentos, disponibilidade | Validação de **assinatura** (PDF ou OOXML; rejeita o resto) e **tamanho máximo**; **limite de páginas** (PDF) / **teto de parágrafos** (DOCX); **timeout** (best-effort) no parsing; tratar o documento como hostil. Fase 4: sandbox de parsing, antimalware, isolamento de processo/recursos. |
| **T3** | **Information Disclosure** — vazamento de PII para LLM externo | Texto da petição (com CPF/nomes/endereços) enviado ao LLM externo (Gemini/Grok/Anthropic) | PII (LGPD) | **Synthetic-first** no MVP (garantia real de "sem PII"); port **`Anonymizer`** mascara identificadores estruturados (CPF/CNPJ/e-mail/telefone/CEP) **e nomes das partes** (regex ancorado, best-effort — [ADR-0010](adr/0010-name-masking-regex-vs-ner.md)) antes do envio; **sem PII em log**; o prompt persistido para auditoria já é o pseudonimizado. O masking é **reversível e LLM-only** — por reter o mapa de reversão é, sob a LGPD, **pseudonimização** (art. 5º, XI), não anonimização: o resumo do revisor é restaurado com os valores reais ([ADR-0012](adr/0012-reversible-anonymization-restore.md)). Por ser reversível, o texto pseudonimizado **continua sendo dado pessoal** (não sai do escopo da LGPD — art. 12) — reduz a exposição ao LLM, não isenta; e o **resumo persistido contém PII** (protegido por JWT; criptografia em repouso = Fase 4). Fase 4: NER de nomes (cobertura completa), criptografia em repouso, retenção/eliminação, DPIA, LLM local. |
| **T4** | **Spoofing** — abuso de autenticação | Brute-force/credential stuffing no `/auth/login` | Credenciais | **Rate-limit/lockout** no login; bcrypt com custo adequado; JWT com **expiração**; cookie **httpOnly+Secure+SameSite**; erros sem vazar detalhe. Fase 4: MFA, refresh tokens. |
| **T5** | **Repudiation** — negação de ação / adulteração de auditoria | Edição/remoção de registros de revisão | Trilha de auditoria | **Auditoria append-only** vinculada a `User` autenticado; cada `/review` grava `AuditEvent` imutável. |
| **T6** | **Information Disclosure** — vazamento de chave de API/segredos | Segredos no git; em logs | Chaves de LLM | Segredos fora do git (`.gitignore` + só `.env.example`); não logar segredos. Fase 4: secrets manager, secret scanning. |
| **T7** | **Tampering** — injeção de entrada na API | Payloads malformados; XSS via campos | Análises, sessão | Validação Pydantic (→422); CORS restrito ao frontend; proteção CSRF; cookie httpOnly; erros consistentes sem stack trace. |
| **T8** | **Denial of Service** — abuso de custo de LLM | Requisições massivas/peças enormes consumindo tokens | Chaves/custo | **Guarda de custo/tokens** (corta acima do limite); timeout + retry com backoff; circuit breaker simples; degradação graciosa (firewall e TPU funcionam sem LLM). |

---

## 4. Decisões de risco aceitas no MVP

- O firewall é **heurístico** e não cobre todos os vetores possíveis — risco residual aceito, mitigado por defesa em profundidade e eval por vetor.
- Sem RBAC/MFA no MVP — todo usuário autenticado tem o mesmo acesso (ver ADR 0007). Os papéis já estão modelados (`Role` ADMIN/REVISOR, embutidos no JWT), mas **sem enforcement** nas rotas; a autorização efetiva fica para a Fase 4.
- LLM externo (Gemini default; Grok/Anthropic opcionais) no MVP — risco de PII tratado por synthetic-first + Anonymizer (estruturados + nomes); LLM local fica para a Fase 4.

Controles detalhados e seu faseamento (MVP vs. Fase 4) em `security.md`.
