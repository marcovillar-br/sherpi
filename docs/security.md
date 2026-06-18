---
title: "Segurança e Confiabilidade"
description: "Controles de segurança e confiabilidade, separados em MVP e Fase 4."
doc_type: security
project: SHERPI
status: approved
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [seguranca, confiabilidade, lgpd, observabilidade]
---

# Segurança e Confiabilidade — SHERPI

| Campo | Valor |
|---|---|
| Documento | Controles de Segurança e Confiabilidade |
| Versão | 1.0 |
| Status | Aprovado |
| Última atualização | 2026-06-18 |

Controles organizados em **MVP** (essencial, no escopo das 2 semanas) vs. **Fase 4** (hardening de produção). Complementa o `threat-model.md`.

---

## 1. Privacidade / LGPD

Domínio com PII jurídica — controle crítico.

**MVP**

- **Synthetic-first**: petições sintéticas evitam que PII real saia para o Gemini externo.
- Port **`Anonymizer`**: mascara CPF/CNPJ/nomes/endereços antes do envio ao LLM, com flag em `config`.
- Invariante de domínio **"nunca decisão automática"** (human-in-the-loop obrigatório).
- **Sem PII em log**.

**Fase 4**

- Criptografia em repouso.
- Política de **retenção e eliminação** de PDFs/análises (direito ao esquecimento).
- DPIA (relatório de impacto à proteção de dados).
- Opção de **LLM local** (Ollama / Maritaca on-prem) para dados sensíveis reais.

---

## 2. Segurança de upload (parsing de arquivo não confiável)

**MVP**

- Validação de **tipo/MIME** e **tamanho máximo**.
- **Limite de páginas**.
- **Timeout e limite de recursos** no parsing (PyMuPDF tem CVEs — tratar PDF como hostil).
- Rejeitar não-PDF.
- **Content hash** para deduplicação/idempotência.

**Fase 4**

- Sandbox de parsing, varredura antimalware, isolamento de processo.

---

## 3. Autenticação e hardening de API

**MVP**

- JWT com **expiração**.
- Cookie **httpOnly + Secure + SameSite**.
- **Rate-limit/lockout** no login (anti brute-force).
- Custo de bcrypt adequado.
- **CORS** restrito ao frontend.
- Proteção **CSRF**.
- Erros consistentes **sem vazar stack trace**.
- Validação de entrada (Pydantic → 422).

**Fase 4**

- Refresh tokens, MFA, RBAC.
- Segredos em **secrets manager**.
- TLS/HTTPS, WAF.

---

## 4. Resiliência de LLM e integrações

**MVP**

- **Timeout + retry com backoff** nas chamadas.
- **Guarda de custo/tokens** (corta requisição acima do limite).
- Validação de schema **com retry**.
- **Circuit breaker** simples.
- **Degradação graciosa**: firewall e TPU funcionam sem o LLM.
- **Defensive prompting**: texto do documento tratado como **dado, não instrução** (delimitadores, separação instrução/conteúdo) — defesa em profundidade além do firewall, que é heurístico e não pega tudo.

**Fase 4**

- Tracing de LLM, monitoramento de custo/qualidade, ativação avaliada do adapter Maritaca.

---

## 5. Observabilidade e operação

**MVP**

- **Logging estruturado + correlation IDs** (sem PII).
- Endpoints **`/health`** e **`/ready`** (este checa o DB).
- **Auditoria append-only** (integridade para fins legais — CNJ 615/2025).

**Fase 4**

- Tracing distribuído, métricas/dashboards, error tracking (Sentry), tracing de LLM.

---

## 6. Cadeia de suprimentos e qualidade

**MVP**

- Segredos fora do git (`.gitignore` + apenas `.env.example`).
- **Pin de versões** (uv lock).
- **pip-audit no CI**.
- ruff/mypy como **gate** de CI.

**Fase 4**

- SBOM, Dependabot, secret scanning.
- Revisão de segurança / pentest.
- Backups e DR.

---

## 7. Resumo de controles por fase

| Domínio | MVP | Fase 4 |
|---|---|---|
| Privacidade/LGPD | Synthetic-first, Anonymizer, sem PII em log | Cripto em repouso, retenção/DPIA, LLM local |
| Upload | MIME/tamanho/páginas, timeout, content hash | Sandbox, antimalware, isolamento |
| Auth/API | JWT+exp, cookie httpOnly+Secure+SameSite, lockout, CORS, CSRF | RBAC, MFA, refresh, secrets manager, TLS/WAF |
| LLM | Timeout/retry/backoff, guarda de custo, circuit breaker, defensive prompting | Tracing de LLM, monitoramento de custo |
| Observabilidade | Logs estruturados+correlation IDs, /health, /ready, auditoria append-only | Tracing distribuído, dashboards, Sentry |
| Supply chain | Segredos fora do git, lock, pip-audit, ruff/mypy gate | SBOM, Dependabot, pentest, backups/DR |
