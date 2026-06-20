---
title: "Backlog do Produto e Sprint Backlog"
description: "Backlog do Produto (épicos e histórias, visão de futuro) e Sprint Backlog (tasks estimadas por sprint)."
doc_type: backlog
project: SHERPI
status: approved
version: 1.5
updated: 2026-06-20
language: pt-BR
tags: [backlog, epicos, historias-de-usuario, sprint, estimativas]
---

# Backlog — SHERPI

Sob responsabilidade do **Product Owner (PO)**. Conforme o Guia de Diretrizes, o backlog é dividido
em duas partes: o **Backlog do Produto** (visão completa de futuro) e o **Sprint Backlog** (recorte
de execução das Sprints, desdobrado em tasks estimadas).

Legenda — Prioridade (MoSCoW): **M**ust · **S**hould · **C**ould · **W**on't (agora).
Estimativa em *story points* (SP, Fibonacci). Recorte: 🔵 Sprint · ⚪ Futuro.

---

## Parte 1 — Backlog do Produto (visão completa)

### Épico EP1 — Integridade Documental (firewall) 🔵 *core diferencial*

| ID | História | Prio | Status |
|---|---|---|---|
| US1.1 | Como **assessor**, quero que o sistema detecte texto oculto/*prompt injection* no PDF **antes** de qualquer análise, para não ser enganado por conteúdo manipulado. | M | ✅ feito |
| US1.2 | Como **magistrado**, quero um laudo das anomalias (tipo, página, evidência), para fundamentar eventual multa por má-fé. | M | ✅ feito |
| US1.3 | Como **servidor**, quero que arquivos não-PDF/grandes demais sejam rejeitados com mensagem clara, para garantir segurança de upload. | S | ✅ feito |

### Épico EP2 — Análise da Petição (extração + admissibilidade) 🔵 *core domain*

| ID | História | Prio | Recorte |
|---|---|---|---|
| US2.1 | Como **assessor**, quero um resumo estruturado (partes, fatos, fundamentação, pedidos, valor da causa), para reduzir o tempo de leitura. | M | 🔵 S1 |
| US2.2 | Como **magistrado**, quero destaque de pedidos de **liminar/tutela de urgência**, para priorizar a análise. | M | 🔵 S2 |
| US2.3 | Como **servidor**, quero um **checklist de admissibilidade** (arts. 319/321) com semáforo, para identificar necessidade de emenda. | M | 🔵 S2 |
| US2.4 | Como **assessor**, quero ver a **proveniência** (trecho de origem) de cada campo extraído, para confiar no resumo (interpretabilidade). | S | 🔵 S2 |

### Épico EP3 — Orquestração & Plataforma 🔵

| ID | História | Prio | Recorte |
|---|---|---|---|
| US3.1 | Como **usuário**, quero enviar um PDF e receber a análise consolidada em uma única operação. | M | 🔵 S2 |
| US3.2 | Como **time**, quero que o LLM seja trocável por configuração, para não depender de um fornecedor. | M | 🔵 S1 |
| US3.3 | Como **time**, quero **persistir** as análises, para consultá-las posteriormente. | S | 🔵 S2 |
| US3.4 | Como **time**, quero um **eval harness** com métricas, para medir a qualidade objetivamente. | S | 🔵 S2 |

### Épico EP4 — Experiência do Usuário (UI mínima) 🔵

| ID | História | Prio | Recorte |
|---|---|---|---|
| US4.1 | Como **assessor**, quero uma tela para enviar o PDF e ver **laudo + resumo lado a lado**. | M | 🔵 S2 |
| US4.2 | Como **magistrado**, quero **tarja vermelha** quando houver injeção detectada, para perceber o risco de imediato. | M | 🔵 S2 |

### Épicos da Fase 4 (agendados em sprints — ordem por importância/ganho)

| Épico | Histórias (resumo) | Prio | Sprint |
|---|---|---|---|
| EP10 — Domínio Trabalhista + rito-aware | Arquitetura por rito (ADR-0008); `TrabalhistaStrategy` (CLT 840, pedido líquido). | **M** | 3 | ✅ |
| EP6 — Identidade & Acesso | Login obrigatório (JWT, perfil único); rotas protegidas. | M | 4/8 | ✅ |
| EP7 — Revisão & Auditoria | Registrar decisão humana; trilha append-only (CNJ 615/2025). | M | 4/8 | ✅ |
| EP5 — Classificação Taxonômica (TPU) | Sugerir top-3 classes/assuntos do CNJ (JurisBERT + k-NN), por ramo. | S | 5/8 | ✅ |
| EP9 — Hardening de Produção | Observabilidade (logs+correlation id), LGPD (anonimização + retenção), deploy/CI-CD. | S | 6 | ✅ |
| EP8 — Integração Judicial | Conectores PJe/E-Proc; ingestão em lote/assíncrona. | C | 7 | ✅ |
| EP11 — Domínios adicionais | Previdenciário/INSS, execução fiscal, família/JEC (encaixes rito-aware). | C | pós-8 | — |
| EP12 — Refactor de nomenclatura (en-US compliance) | Renomear identificadores Python pt-BR para en-US nos contextos `petition_analysis` e `review`. Débito técnico; não afeta funcionalidade. | C | 9 | ✅ |
| EP13 — OCR de documentos digitalizados | Extrair texto de PDFs imagem/escaneados (total ou parcial) via OCR (Tesseract / OCR de nuvem / visão), alimentando o pipeline normal (firewall + anonimização + extração). Hoje o Nível 1 só **detecta e sinaliza** "sem camada de texto". Ver discussão em §LGPD/[ADR-0010](adr/0010-name-masking-regex-vs-ner.md). | — | — (não priorizado) | ⚪ |
| EP14 — Anonimização de nomes (LGPD default) | Mascarar nomes das partes antes do LLM externo por regex ancorado (`RegexNameAnonymizer` + `CompositeAnonymizer`), inclusive listas (litisconsórcio); robustez via `visible_text` por bloco. Best-effort; NER (Presidio) segue como evolução ([ADR-0010](adr/0010-name-masking-regex-vs-ner.md)). | M | pós-9 | ✅ |
| EP15 — Robustez de ingestão (PDF-imagem) | Detectar PDF sem camada de texto (imagem/escaneado) → sinaliza no laudo (`image_only_pages`) e pula a extração, sem laudo "íntegro" falso (Nível 1; OCR é EP13). Cenários no corpus: `scanned_acao_cobranca` (100% imagem) e `scanned_parcial` (texto + página-imagem). | S | pós-9 | ✅ |
| EP16 — Adapters de LLM Grok (xAI) e Sonnet (Anthropic) | Adapters httpx trocáveis por config sobre a base `HttpLLMProvider`; remoção da dep órfã `openai`. | C | pós-9 | ✅ |
| EP17 — UI de histórico e auditoria de LLM | Lista de análises (filtros + detalhe) e consulta do prompt anonimizado + resposta de cada chamada ao LLM (`PersistingLLMProvider`). | C | pós-9 | ✅ |

### Limitações conhecidas (medidas, não mascaradas)

- **Extração recupera campos formalmente omitidos.** A extração via LLM pode reconstruir, a partir da narrativa dos fatos, elementos que a peça omite formalmente — ex.: o *rol de pedidos* em `defect_sem_pedidos`. Nesses casos a admissibilidade pode não disparar RED. O *prompt v2* mitiga parte dos casos (valor da causa, fundamentação), mas o rol de pedidos persiste. **Baseline `make e2e-llm`: 9/10.** Mitigação atual: *human-in-the-loop* (toda saída é sugestão revisável; o rótulo do cenário segue RED, sem mascarar). Melhoria futura: extração mais literal / validação cruzada estrutura↔narrativa.

---

## Parte 2 — Sprint Backlog (execução)

Histórias selecionadas por sprint, desdobradas em **tasks técnicas estimadas**. Sprints 1–9
concluídas (MVP + multi-domínio + Fase 4 backend + UI frontend S4–S7 + en-US), além dos
**refinamentos pós-9** (EP14–EP17, ver tabela acima).

### Sprint 1 — Fundações + Firewall + Extração *(grande parte concluída)*

| História | Task | SP | Status |
|---|---|---|---|
| — | Scaffold DDD + tooling + CI + docker-compose | 5 | ✅ |
| US1.1/1.2 | Detector puro (7 vetores) + `ForensicsReport` | 5 | ✅ |
| US1.1 | Adapter PyMuPDF (CropBox→MediaBox) | 3 | ✅ |
| US1.3 | Guarda de upload (tipo/tamanho/páginas) | 2 | ✅ |
| — | Gerador de dados sintéticos + corpus rotulado | 3 | ✅ |
| US3.2 | Port `LLMProvider` + adapter Gemini + `FakeProvider` | 5 | ✅ |
| US2.1 | `ExtractPetition` + schema `PetitionSummary` + retry | 5 | ✅ |
| US2.1 | *Defensive prompting* + *chunking* (>100 págs) | 3 | ✅ |
| **Total Sprint 1** | | **31** | ✅ |

### Sprint 2 — Admissibilidade + Orquestração + Persistência + UI

| História | Task | SP |
|---|---|---|
| US2.3 | Validadores determinísticos (CPF/CNPJ, valor, pedidos) | 3 |
| US2.3 | Checagem semântica de documentos + `AdmissibilityReport` (semáforo) | 5 |
| US2.2 | Destaque de liminar/tutela de urgência | 2 |
| US2.4 | Proveniência dos campos extraídos (interpretabilidade) | 3 |
| US3.1 | Orquestrador `analyze_petition` (firewall→extração→admissibilidade) | 3 |
| US3.1 | API FastAPI `POST /analyze` + `/health` `/ready` | 3 |
| US3.3 | Persistência (SQLModel + Alembic + repositório) | 5 |
| US3.4 | Eval harness + métricas + gate de CI | 5 |
| US4.1 | UI mínima: upload → painel laudo + resumo | 5 |
| US4.2 | Tarja de risco (BLOCK) na UI | 2 |
| **Total Sprint 2** | | **36** ✅ |

### Sprint 3 — Domínio Trabalhista (CLT 840) + rito-aware

| Épico | Task | SP | Status |
|---|---|---|---|
| EP10 | Enum `Rito` + `AdmissibilityStrategy` (Protocol) + registro; extrair `CivelStrategy` (sem mudar comportamento) | 5 | ✅ |
| EP10 | `TrabalhistaStrategy` (CLT art. 840 §1º) + checagem de **pedido líquido** | 5 | ✅ |
| EP10 | `Pedido.valor` no `PetitionSummary` + prompt; parâmetro `rito` no `POST /v1/analyze` | 3 | ✅ |
| EP10 | Cenários sintéticos trabalhistas (cumulação massiva; pedido líquido × ilíquido) | 3 | ✅ |
| **Total Sprint 3** | | **16** | ✅ |

**Desdobramento técnico** (execução):

- **Rito-aware** (ADR-0008): `Rito` (enum) em `shared_kernel/value_objects.py`;
  `AdmissibilityStrategy` (`Protocol`), `CivelStrategy`, `TrabalhistaStrategy` e
  `DEFAULT_STRATEGIES` em `petition_analysis/domain/strategies.py`. `CheckAdmissibility`
  vira **dispatcher** `Rito → estratégia` (default cível); cível byte-a-byte inalterado
  (testes legados intactos como prova de não-regressão).
- **Pedido líquido**: `TrabalhistaStrategy` herda o checklist do art. 319 e acrescenta o
  requisito `PEDIDO_LIQUIDO` (cada `Pedido` precisa de `valor` parseável); ilíquido →
  emenda (VERMELHO). `Pedido.valor` adicionado ao `PetitionSummary` + instrução no prompt.
- **Roteamento**: `AnalyzePetition.run(..., rito=CIVEL)` e `AnalysisResult.rito`; `rito` como
  *form field* em `POST /v1/analyze` (default cível; valor inválido → 422).
- **Massa**: `trabalhista_pedido_liquido` (verde), `trabalhista_pedido_iliquido` (vermelho),
  `trabalhista_cumulacao_massiva` (verde); rótulo `rito` no corpus/`labels.json`.

**Definition of Done (Sprint 3)**

- [x] Admissibilidade despacha por rito; cível inalterado; `TrabalhistaStrategy` valida pedido líquido.
- [x] Massa com cenários trabalhistas (cumulação massiva, pedido líquido × ilíquido). Testes verdes.
- [x] `POST /v1/analyze` aceita `rito` (default cível); rito inválido → 422.
- [x] `ruff`/`mypy`/`pytest` limpos; eval do firewall no limiar (precision/recall = 1.0).
- [ ] **Sprint Review (sábado)**: demo do trabalhista (pedido ilíquido → VERMELHO) vs. cível.

### Sprint 4 — Confiança & Conformidade (`identity` + `review`)

| Épico | Task | SP | Status |
|---|---|---|---|
| EP6 | Contexto `identity`: `User`/`Role`, `BcryptHasher`, `JwtIssuer`, `UserRepository` (SQLModel) | 5 | ✅ |
| EP6 | `Authenticate` (OAuth2 password + JWT) + `POST /v1/auth/login` + usuário semeado | 3 | ✅ |
| EP6 | Proteção de rotas por JWT (cookie httpOnly+SameSite=lax) + rate-limit/lockout | 5 | ✅ |
| EP7 | Contexto `review`: `ReviewDecision`, `AuditEvent`, `RecordReview`, `AuditRepository` (append-only) | 5 | ✅ |
| EP7 | `POST /v1/analyses/{id}/review` + `GET /v1/analyses/{id}/reviews` | 3 | ✅ |
| EP6/EP7 | UI: tela de login + ações de revisão (aceitar/rejeitar/corrigir) | 5 | planejada |
| **Total Sprint 4** | | **26** | ✅ (backend; UI frontend pendente) |

### Sprint 5 — Classificação TPU (`taxonomy`)

| Épico | Task | SP | Status |
|---|---|---|---|
| EP5 | Deps de ML (`--extra ml`) + **seed rotulado** petição→código TPU (`synthetic/tpu_seed.py`, 30 entradas) | 5 | ✅ |
| EP5 | `EmbeddingModel` (Protocol) + `FakeEmbeddingModel` + `JurisbertEmbeddingModel`; `TpuIndex` k-NN numpy/bytes (SQLite+Postgres) | 5 | ✅ |
| EP5 | `BuildTpuIndex` + `SuggestTpu` (top-3 com confiança + âncora) + ligação no orquestrador (`AnalysisResult.tpu_suggestions`) | 5 | ✅ |
| EP5 | Eval: `eval_tpu()` top-1/top-3 sobre seed (sanidade honesta) integrado ao `evals.run` | 3 | ✅ |
| EP5 | UI: top-3 sugestões com confiança e exemplos-âncora | 3 | planejada (frontend) |
| **Total Sprint 5** | | **21** | ✅ (backend; UI frontend pendente) |

### Sprint 6 — Produção (observabilidade, LGPD pleno, deploy)

| Épico | Task | SP | Status |
|---|---|---|---|
| EP9 | Logging estruturado (`structlog`) + correlation IDs (middleware) | 3 | ✅ |
| EP9 | *Error tracking* (Sentry, soft dep) + `sentry_dsn` config | 3 | ✅ |
| EP9 | LGPD: `MappedRegexAnonymizer` (reversível) + `PresidioAnonymizer` (extra `ner`) | 5 | ✅ |
| EP9 | Retenção/eliminação (`DELETE /v1/analyses/{id}` + bulk) | 3 | ✅ |
| EP9 | `Dockerfile` multi-stage + `docker-compose.prod.yml` + `.env.example` | 5 | ✅ |
| EP9 | `pip-audit` como gate real no CI | — | ✅ |
| **Total Sprint 6** | | **19** | ✅ |

### Sprint 7 — Integração PJe/E-Proc

| Épico | Task | SP | Status |
|---|---|---|---|
| EP8 | Bounded context de integração: adapter PJe/E-Proc (sandbox) | 8 | ✅ |
| EP8 | Ingestão em lote + execução assíncrona/fila | 5 | ✅ |
| **Total Sprint 7** | | **13** | ✅ |

### Sprint 8 — UI das Sprints 4–7 (Auth + Rito + TPU + Revisão)

| Épico | Task | SP | Status |
|---|---|---|---|
| EP6 | Página de login (`/login`): formulário email+senha, cookie httpOnly via backend, redirect em 401 | 5 | ✅ |
| EP6/EP7 | `api.ts`: `credentials:"include"` em todos os fetches; `login()`, `submitReview()`, `getReviews()` | 3 | ✅ |
| EP5/S3 | `types.ts`: `Rito`, `ReviewDecision`, `AuditEvent`, `TpuSuggestion`; seletor de rito no formulário | 3 | ✅ |
| EP5 | `TpuPanel`: top-3 sugestões com barra de confiança e trecho-âncora | 3 | ✅ |
| EP7 | `ReviewPanel`: botões ACEITAR/CORRIGIR/REJEITAR + comentário + trilha append-only | 5 | ✅ |
| **Total Sprint 8** | | **19** | ✅ |

**Definition of Done (Sprint 8)**

- [x] `npm run build` e `npm run lint` limpos; zero erros de TypeScript.
- [x] Login page em `/login`; 401 em `/` redireciona para `/login` automaticamente.
- [x] Seletor de rito (Cível/Trabalhista) no formulário de análise.
- [x] `TpuPanel` exibido quando `tpu_suggestions` retornado pela API.
- [x] `ReviewPanel` com seleção de decisão, comentário e trilha de auditoria abaixo da análise.

> As estimativas serão recalibradas em cada *Sprint Planning* conforme a capacidade real da equipe e
> o framework de Design Sprint.

---

### Sprint 9 — Refactor de nomenclatura en-US (EP12) ✅

| Task | SP | Status |
|---|---|---|
| Renomear `summary.py` (campos Pydantic + enum `ClaimType`) + atualizar prompt LLM | 5 | ✅ |
| Renomear `admissibility.py` (classes, enums, campos) + `ClaimAmount` (ex-`ValorCausa`) | 5 | ✅ |
| Renomear métodos privados de `strategies.py` + refs de campos | 3 | ✅ |
| Renomear `ReviewDecision` (ACCEPT/REJECT/AMEND) | 3 | ✅ |
| Atualizar todos os testes e evals | 5 | ✅ |
| Atualizar contrato de API (response schema + frontend `types.ts` + componentes) | 3 | ✅ |
| **Total Sprint 9** | **24** | ✅ |

**Definition of Done (Sprint 9)**

- [x] `uv run pytest -q` → 196 passed, 0 failed.
- [x] `ruff check --fix . && ruff format . && mypy src/ evals/` → limpos.
- [x] `npm run build && npm run lint` → limpos.
- [x] Nenhum identificador pt-BR violando a regra de duas camadas (exceção `trabalhista` documentada).

---

### EP12 — Refactor de nomenclatura (en-US compliance) ✅ *concluído na Sprint 9*

**Contexto:** A regra estabelecida no `CONTRIBUTING.md` determina que identificadores Python devem ser
en-US. Uma auditoria pós-S8 identificou violações sistemáticas nos contextos `petition_analysis` e
`review`, herdadas do scaffold inicial (anterior à formalização da regra).

**Escopo das violações:**

| Arquivo | Exemplos de identificadores a renomear |
|---|---|
| `petition_analysis/domain/summary.py` | `Parte.nome/documento/polo/endereco`, `Pedido.descricao/tipo/valor`, `TipoPedido.PRINCIPAL/LIMINAR/SUBSIDIARIO`, `PetitionSummary.juizo/partes/fato_gerador/fundamentacao/pedidos/tem_liminar/valor_causa/requer_provas/opcao_audiencia/documentos_mencionados` |
| `petition_analysis/domain/admissibility.py` | `class Semaforo` → `AdmissibilityStatus`; valores `VERDE/AMARELO/VERMELHO`; `class MetodoCheck` + `DETERMINISTICO/SEMANTICO`; `class Requisito` + todos os valores; campos `ChecklistItem` e `AdmissibilityReport` |
| `petition_analysis/domain/strategies.py` | `_check_juizo`, `_check_partes`, `_check_pedidos`, `_check_valor_causa`, `_check_provas`, `_check_audiencia`, `_check_documentos`, `_check_pedido_liquido`, `_DOCS_ESSENCIAIS` |
| `review/domain/events.py` | `ReviewDecision.ACEITAR/REJEITAR/CORRIGIR` → `ACCEPT/REJECT/AMEND` |

**Blast radius:** alto — mudança de campo Pydantic altera o contrato JSON de `POST /v1/analyze`,
o schema enviado ao LLM no prompt, e praticamente todos os testes. Requer Sprint dedicada com
migration de API versionada ou flag de compatibilidade.

**Impacto no usuário:** nenhum (débito interno). **Impacto em CI:** nenhum (todos os testes passam
com os nomes atuais; a Sprint só será desbloqueadora de novos contribuidores que leiam o código).

| Task | SP |
|---|---|
| Renomear `summary.py` (campos Pydantic + enum `TipoPedido`) + atualizar prompt LLM | 5 |
| Renomear `admissibility.py` (classes, enums, campos) | 5 |
| Renomear métodos privados de `strategies.py` | 3 |
| Renomear `ReviewDecision` + migration Alembic (coluna no banco) | 3 |
| Atualizar todos os testes e evals | 5 |
| Atualizar contrato de API (response schema + frontend `types.ts`) | 3 |
| **Total estimado EP12** | **24** |
