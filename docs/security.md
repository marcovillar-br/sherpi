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
- **`RegexAnonymizer`** (implementa o port `Anonymizer`, ativo via `anonymize_before_llm` + LLM
  externo): mascara **identificadores estruturados** (CPF, CNPJ, e-mail, telefone, CEP) **antes** do
  envio ao LLM. A validação determinística de CPF/CNPJ roda sobre o **texto original**, então o
  mascaramento **não degrada** a admissibilidade.
- **`RegexNameAnonymizer`** (flag `anonymize_names`, default on): mascara **nomes das partes** por
  âncora (antes de "brasileiro/pessoa jurídica/inscrito no CPF" ou após "em face de") → `[NOME]`.
  Determinístico, O(n), sem dependências. **Best-effort**: pega os nomes da qualificação, mas pode
  não pegar nomes citados livremente nos fatos (ver [ADR-0010](adr/0010-name-masking-regex-vs-ner.md)).
- Invariante de domínio **"nunca decisão automática"** (human-in-the-loop obrigatório).
- **Sem PII em log**.

**Fase 4**

- **Anonimização de nomes por NER** (Presidio/spaCy): cobertura **completa** de nomes (inclusive em
  texto livre), substituindo/complementando a heurística por âncora do MVP. Trade-off em
  [ADR-0010](adr/0010-name-masking-regex-vs-ner.md).
- Anonimização reversível (placeholders + restauração) — **base já disponível** no MVP (`MappedRegexAnonymizer`, opt-in); ampliar o wiring onde a utilidade exigir.
- Criptografia em repouso.
- Política de **retenção e eliminação** de PDFs/análises (direito ao esquecimento) — **base já disponível** (config `retention_days` + `DELETE /analyses`); ampliar (agendamento, DPIA).
- DPIA (relatório de impacto à proteção de dados).
- Opção de **LLM local** (Ollama / Maritaca on-prem) para dados sensíveis reais.

---

## 2. Segurança de upload (parsing de arquivo não confiável)

**MVP**

- Validação de **assinatura** (magic bytes `%PDF-`) e **tamanho máximo**.
- **Limite de páginas**.
- **Timeout** no parsing (best-effort via SIGALRM; PyMuPDF tem CVEs — tratar PDF como hostil). *Isolamento pleno de recursos (subprocesso + `setrlimit`): Fase 4.*
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
| Upload | assinatura/tamanho/páginas, timeout (best-effort), content hash | Sandbox, antimalware, isolamento de recursos |
| Auth/API | JWT+exp, cookie httpOnly+Secure+SameSite, lockout, CORS, CSRF | RBAC, MFA, refresh, secrets manager, TLS/WAF |
| LLM | Timeout/retry/backoff, guarda de custo, circuit breaker, defensive prompting | Tracing de LLM, monitoramento de custo |
| Observabilidade | Logs estruturados+correlation IDs, /health, /ready, auditoria append-only | Tracing distribuído, dashboards, Sentry |
| Supply chain | Segredos fora do git, lock, pip-audit, ruff/mypy gate | SBOM, Dependabot, pentest, backups/DR |
