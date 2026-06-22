---
title: "Roadmap (MVP + Fase 4)"
description: "Roadmap das sprints (MVP em 2 semanas + Fase 4 concluída), com Definition of Done e marcos."
doc_type: roadmap
project: SHERPI
status: approved
version: 1.5
updated: 2026-06-22
language: pt-BR
tags: [roadmap, sprints, planejamento, mvp]
---

# Roadmap — SHERPI

| Campo | Valor |
|---|---|
| Documento | Roadmap |
| Versão | 1.5 |
| Status | Aprovado |
| Última atualização | 2026-06-22 |

O **MVP** é entregue em **2 Sprints (2 semanas)**, conforme o Guia de Diretrizes da disciplina, com
ritmo de **Design Sprint semanal** e **Sprint Review aos sábados** (ver [`agile-process.md`](agile-process.md)).
Cada sprint tem objetivos, entregáveis e **critérios de saída (Definition of Done)**. O escopo além
do MVP está registrado como **visão de futuro** (ver [`backlog.md`](backlog.md)) e detalhado na **Fase 4**.

---

## Sprint 1 (Semana 1) — Fundações + Firewall + Extração

**Objetivo**: erguer o esqueleto hexagonal, entregar o diferencial do produto (firewall) testado, os dados sintéticos do eval e a extração estruturada agnóstica a LLM.

**Entregáveis**

- Scaffolding `backend/` (uv); `docker-compose` com PostgreSQL 16; CI (lint + type + test).
- `shared_kernel`: Value Objects (CPF, CNPJ, ValorCausa, RiskVerdict) e ports transversais (LLMProvider, BlobStorage, Anonymizer).
- Bounded context **document_integrity** completo: `DetectInjection` + `PyMuPDFParser`, cobrindo os 7 vetores de injeção, fortemente unit-testado. ✅
- **Gerador de petições sintéticas**: peças limpas + injeções plantadas de cada vetor (ground truth). ✅
- Port `LLMProvider` + adapter **Gemini (default)** + `FakeProvider`.
- Bounded context **petition_analysis** (parcial): `ExtractPetition` (JSON validado, temperature=0, *defensive prompting*, *chunking* >100 págs).

**Definition of Done**

- [x] `uv run pytest` verde no domínio puro e no firewall (um teste por vetor de injeção).
- [x] CI executa lint (ruff), type (mypy) e testes em cada push.
- [x] Dataset sintético com rótulos disponível via `synthetic.generate`.
- [x] `LLMProvider` trocável por config; `ExtractPetition` retorna `PetitionSummary` validado (com `FakeProvider`).
- [ ] **Sprint Review (sábado)**: demo do firewall bloqueando PDF malicioso + extração de uma petição limpa.

---

## Sprint 2 (Semana 2) — Admissibilidade + Orquestração + Persistência + UI

**Objetivo**: fechar o MVP demonstrável ponta a ponta: admissibilidade, orquestrador, persistência e uma UI mínima.

**Entregáveis**

- **petition_analysis**: `CheckAdmissibility` (validadores determinísticos + extração semântica, arts. 319/321) com proveniência dos campos.
- Use case orquestrador `analyze_petition` (integrity → [BLOCK?] → extração → admissibilidade).
- API FastAPI: `POST /analyze`, `/health`, `/ready`.
- Persistência: SQLModel + Alembic, repositório das análises.
- **UI mínima**: upload do PDF → painel com laudo de segurança + resumo estruturado (tarja vermelha em `BLOCK`).
- **Eval harness**: precision/recall do firewall e F1 da extração; gate no CI.

**Definition of Done**

- [x] Orquestrador testado com `FakeProvider` (sem rede): caminho feliz e early-exit por `BLOCK`.
- [x] Validadores determinísticos (checksum CPF/CNPJ, valor da causa, pedidos) com testes exatos.
- [x] `POST /analyze`: PDF limpo → resumo + admissibilidade; PDF com injeção → `BLOCK` **sem chamada LLM**; análise persistida e recuperável.
- [x] UI: upload → laudo + resumo lado a lado; tarja vermelha quando houver injeção.
- [x] `uv run python -m evals.run` produz métricas; CI falha abaixo do limiar.
- [x] `ruff` e `mypy` limpos.
- [ ] **Sprint Review (sábado)**: demo do MVP completo (upload → análise consolidada na UI).

---

## Fase 4 — Continuação em sprints (priorizadas por importância/ganho)

Pós-MVP, ordenadas por `(importância × ganho) ÷ (esforço × risco)`, respeitando dependências.
Detalhe das histórias/tasks em [`backlog.md`](backlog.md); gerência em [`pmp.md`](pmp.md).

### Sprint 3 — Domínio Trabalhista (CLT 840) + arquitetura rito-aware

**Objetivo**: foco do grupo. Tornar o domínio **plugável por rito** (ver [ADR-0008](adr/0008-multi-domain-architecture.md))
e entregar o **trabalhista** como primeira nova estratégia de admissibilidade.

**Entregáveis**
- Enum `Rito` + `AdmissibilityStrategy` + registro; cível extraído para `CivelStrategy`.
- `TrabalhistaStrategy` (CLT art. 840 §1º), incluindo a checagem de **pedido líquido** (valor por pedido);
  `Pedido.valor` no `PetitionSummary`.
- Parâmetro `rito` no `POST /v1/analyze` (default cível); cenários sintéticos **trabalhistas** na massa.

**Definition of Done**
- [x] Admissibilidade despacha por rito; cível inalterado; `TrabalhistaStrategy` valida pedido líquido.
- [x] Massa com cenários trabalhistas (cumulação massiva, pedido líquido × ilíquido). Testes verdes.

### Sprint 4 — Confiança & Conformidade (`identity` + `review`)

**Objetivo**: nenhum tribunal adota IA sem controle humano auditável (Res. CNJ 615/2025). Entregar
login obrigatório e o *human-in-the-loop* completo.

**Entregáveis**
- **identity**: `User`/`Role`, `Authenticate` (OAuth2 password + JWT), `BcryptHasher`, `JwtIssuer`,
  `UserRepository`; usuário semeado via `.env`; `POST /v1/auth/login`; rotas de domínio protegidas por JWT.
- **review**: `ReviewDecision` + `AuditEvent`, `RecordReview`, `AuditRepository` (append-only);
  `POST /v1/analyses/{id}/review`.
- **Hardening de auth**: cookie httpOnly+Secure+SameSite, rate-limit/lockout no login, CSRF.
- **UI**: tela de login + ações de revisão (aceitar/rejeitar/corrigir).

**Definition of Done**
- [x] `/v1/analyze` sem token → 401; `POST /v1/auth/login` retorna JWT; lockout após N falhas.
- [x] `POST /v1/analyses/{id}/review` grava `AuditEvent` vinculado ao usuário; trilha append-only.
- [ ] UI: login → análise → registrar revisão. *(frontend pendente)*

### Sprint 5 — Classificação TPU (`taxonomy`)

**Objetivo**: 3ª capacidade núcleo — sugerir a classe/assunto do CNJ, atacando o gargalo da autuação
(por ramo: cível e trabalhista).

**Entregáveis**
- Deps de ML (`uv sync --extra ml`); **seed rotulado** petição→código TPU.
- `EmbeddingModel` (JurisBERT via HuggingFace) + `TpuIndex` (k-NN em **numpy/bytes**); `ClassifyTpu` +
  `SuggestTpu`; ligação no orquestrador (`… → tpu`).
- UI: top-3 sugestões com confiança e exemplos-âncora (interpretabilidade).

**Definition of Done**
- [x] `SuggestTpu` retorna top-3 com confiança sobre o seed; índice populado (k-NN numpy/bytes).
- [x] Eval reporta acurácia top-1/top-3 **honestamente** (sem prometer número). Testes verdes.

### Sprint 6 — Produção (observabilidade, LGPD pleno, deploy)

**Objetivo**: tornar operável, observável e conforme para sair do escopo acadêmico.

**Entregáveis**
- **Observabilidade**: logging estruturado (`structlog`) + **correlation IDs** (middleware), *error
  tracking* (Sentry), métricas básicas.
- **LGPD pleno**: NER de nomes (Presidio/spaCy), anonimização reversível, retenção/eliminação.
- **Deploy**: containerização completa (app+db), CI/CD com deploy; segredos em *secrets manager*; TLS.

**Definition of Done**
- [x] Logs estruturados com correlation id e **sem PII**; política de retenção configurável.
- [x] Imagem da app + pipeline de deploy; `pip-audit` como gate (sem alta severidade).

### Sprint 7 — Integração PJe/E-Proc

**Objetivo**: ingestão real a partir dos sistemas processuais (maior ganho de adoção; maior dependência externa).

**Entregáveis**
- Novo bounded context de integração (adapter PJe/E-Proc); ingestão em lote; execução assíncrona/fila para escala.

**Definition of Done**
- [x] Ingestão de ao menos um sistema (sandbox) processada ponta a ponta de forma assíncrona.

### Sprint 8 — UI das Sprints 4–7 (Auth + Rito + TPU + Revisão)

**Objetivo**: fechar o gap entre backend completo e a interface — tornar as capacidades entregues nas
Sprints 4–7 acessíveis ao usuário final sem exigir o Swagger.

**Entregáveis**
- Página `/login` com formulário email+senha; cookie httpOnly definido pelo backend; redirecionamento
  automático em 401 no fluxo de análise.
- Seletor de rito (Cível/Trabalhista) no formulário de upload.
- `TpuPanel`: top-3 sugestões TPU com barra de confiança e trecho-âncora.
- `ReviewPanel`: botões ACEITAR/CORRIGIR/REJEITAR, campo de comentário, trilha de auditoria append-only.

**Definition of Done**
- [x] `npm run build` e `npm run lint` limpos; zero erros TypeScript.
- [x] Login → análise → revisão funcionando ponta a ponta no navegador.
- [x] 401 em `/` redireciona para `/login` automaticamente.

### Sprint 9 — Refactor de nomenclatura en-US (EP12)

**Objetivo**: eliminar o débito técnico de identificadores pt-BR no domínio Python, garantindo conformidade com a regra de duas camadas documentada no `CONTRIBUTING.md`.

**Entregáveis**
- Campos Pydantic de `PetitionSummary`, `Parte`, `Pedido`, `ChecklistItem`, `AdmissibilityReport` em en-US.
- Enums: `Polo`, `ClaimType`, `Requirement`, `CheckMethod`, `AdmissibilityStatus`, `ReviewDecision`, `ClaimAmount` renomeados.
- Métodos privados de `CivelStrategy` e `TrabalhistaStrategy` renomeados.
- Prompt `EXTRACTION_SYSTEM_PROMPT` com referências a campos en-US.
- `frontend/src/lib/types.ts` e componentes React atualizados.

**Definition of Done**
- [x] `uv run pytest -q` → 196 passed, 0 failed.
- [x] `ruff` + `mypy` limpos; `npm run build && npm run lint` limpos.
- [x] Zero identificadores pt-BR violando a regra (exceção `trabalhista` documentada).

### Refinamentos contínuos (pós-Sprint 9)

Melhorias entregues após o fechamento das sprints, na branch `development`:

- **Anonimização de nomes por default** (`RegexNameAnonymizer` + `CompositeAnonymizer`): mascara os
  nomes das partes — inclusive listas (litisconsórcio) — antes do LLM externo; robustez estrutural
  via `visible_text` por bloco. Best-effort; NER (Presidio) segue como evolução ([ADR-0010](adr/0010-name-masking-regex-vs-ner.md)).
- **Detecção de PDF imagem/escaneado**: páginas sem texto (`image_only_pages`) → pula a extração;
  páginas **mistas** (`image_heavy_pages`: têm texto, mas imagem domina) → extrai o texto e avisa
  sobre conteúdo possivelmente não extraído. Sem laudo "íntegro" falso. Corpus: `scanned_acao_cobranca`
  (100% imagem), `scanned_parcial` (texto + página-imagem) e `scanned_mista` (página mista). OCR é **EP13**.
- **Adapters de LLM Grok (xAI) e Claude Sonnet (Anthropic)** via httpx, trocáveis por config
  (com remoção da dep órfã `openai`).
- **UI**: histórico de análises (lista + filtros + detalhe) e auditoria das chamadas ao LLM
  (prompt anonimizado + resposta).
- **Cenário sintético de litisconsórcio** (multi-parte) + testes de integração ponta a ponta.
- **TPU 1.0 sobre a TUA real do CNJ** ([ADR-0016](adr/0016-cnj-tua-real-catalog-tpu.md)): substitui o
  seed sintético pelo catálogo oficial (escopo cível+trabalhista), texto de embedding híbrido (caminho +
  glossário), **ranking híbrido** (cosseno denso + léxico/IDF) e limiar de confiança
  (`SHERPI_TPU_MIN_CONFIDENCE`, default 0.65); eval rotulado (top-1/top-3/top-5). Seed sintético mantido
  para CI/testes rápidos.

Estado: **282 testes** verdes; ruff/mypy e `npm run build`/`lint` limpos.

---

### Domínios adicionais (épicos incrementais, pós rito-aware)

Com a arquitetura rito-aware pronta (Sprint 3), cada novo domínio é um **encaixe** (estratégia +
cenários + ramo de TPU), por ordem de volume: **Previdenciário/INSS** → **Execução fiscal** →
**Família/JEC**. Planejados como épicos próprios quando priorizados.

---

## Tabela de marcos

| Marco | Sprint | Resultado |
|---|---|---|
| M1 — Firewall + dados + extração | 1 | ✅ Firewall por vetor; dataset sintético; LLM agnóstico + extração. |
| M2 — MVP completo | 2 | ✅ Admissibilidade + orquestrador + persistência + UI + eval. |
| M3 — Domínio Trabalhista + rito-aware | 3 | ✅ Arquitetura por rito; `TrabalhistaStrategy` (CLT 840, pedido líquido). |
| M4 — Confiança & Conformidade | 4 | ✅ Identity (JWT) + review (human-in-the-loop + auditoria append-only). |
| M5 — Classificação TPU | 5 | ✅ `SuggestTpu` (FakeEmbeddingModel + JurisbertEmbeddingModel) top-3 com confiança; eval honesto. |
| M6 — Produção | 6 | ✅ structlog + correlation ID; `MappedRegexAnonymizer` + `PresidioAnonymizer` (extra `ner`); Dockerfile; `pip-audit` gate. |
| M7 — Integração processual | 7 | ✅ `SandboxSourceAdapter` + `IngestPetitions` + `IngestQueue` (asyncio); `POST /v1/ingestion/jobs` (202). |
| M8 — UI completa (S4–S7) | 8 | ✅ Login + seletor de rito + `TpuPanel` + `ReviewPanel`; frontend ponta a ponta. |
| M9 — en-US compliance | 9 | ✅ Todos os identificadores Python em en-US; contratos API, testes e frontend sincronizados. |
| M10 — Refinamentos pós-MVP | — | ✅ Anonimização de nomes (default); detecção de PDF-imagem; adapters Grok/Anthropic; UI histórico + auditoria de LLM. |
