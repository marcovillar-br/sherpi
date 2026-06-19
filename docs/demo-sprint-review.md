---
title: "Roteiro de Demo — Sprint Review"
description: "Runbook passo a passo para apresentar o SHERPI (MVP + rito trabalhista) ao professor na Sprint Review."
doc_type: runbook
project: SHERPI
status: approved
version: 1.2
updated: 2026-06-19
language: pt-BR
tags: [demo, sprint-review, runbook, apresentacao]
---

# Roteiro de Demo — Sprint Review (SHERPI)

Runbook para apresentar o **SHERPI completo (Sprints 1–9)** ao professor.
Duração-alvo: **~15 minutos** (12 de demo + 3 de Q&A).
Mensagem central: *"triagem assistida com firewall, admissibilidade multi-rito, controle humano
auditável e ingestão automatizada — do PDF à sugestão de TPU, com LGPD e observabilidade prontas
para produção"*.

## 0. Antes de apresentar (checklist — rodar 15 min antes)

> **Importante:** nunca exporte o `backend/.env` no shell (`export $(cat .env...)`);
> o `uv run` lê o arquivo automaticamente. Exportar variáveis manualmente corrompe
> valores JSON (ex: `SHERPI_CORS_ORIGINS`) e quebra o startup.

```bash
# 1) Variáveis de ambiente — editar backend/.env uma única vez
#    SHERPI_LLM_API_KEY=<chave Gemini>
#    SHERPI_JWT_SECRET=<segredo forte>
#    SHERPI_SEED_USER_PASSWORD=<senha>   → cria gabinete@sherpi.local no startup

# 2) Setup inicial (banco + migrations + índice TPU + corpus sintético)
make setup
# fallback sem Docker: editar SHERPI_DATABASE_URL=sqlite:///./sherpi.db no .env
#                      e rodar: cd backend && uv run alembic upgrade head && make seed-tpu synthetic

# 3) Suba os serviços em terminais separados
make dev-backend    # backend em http://localhost:8000
make dev-frontend   # frontend em http://localhost:3000
```

**Verificação rápida:**
```bash
curl localhost:8000/health   # → {"status":"ok"}
curl localhost:8000/ready    # → {"status":"ok"}
```

> Tenha abertos: navegador em `localhost:3000`, `http://localhost:8000/docs` (Swagger), este roteiro.

---

## 1. Contexto (1 min — falar, sem tela)

- Litigiosidade massiva, **até 60 % das iniciais** com vícios; petições de 49–116 págs.
- Ameaça concreta: **prompt injection** em PDFs (casos reais PA e SP) — comandos ocultos que
  enganam a IA e quebram o contraditório.
- SHERPI faz **triagem assistida**: firewall → extração → admissibilidade multi-rito → revisão
  humana → sugestão de TPU → ingestão automatizada. **Sempre apoio, nunca decisão automática**
  (Res. CNJ 615/2025).

---

## 2. Sprint 1–2: caminho feliz — petição cível limpa (2 min)

> Demonstra firewall + extração + admissibilidade (MVP).

1. **Login**: acessar `localhost:3000`, entrar com `gabinete@sherpi.local` / senha configurada.
2. Enviar **`data/synthetic/clean_acao_cobranca.pdf`** → **Analisar**.
3. Mostrar lado a lado:
   - **Laudo de integridade**: verde "Documento íntegro".
   - **Resumo estruturado**: partes (CPF/CNPJ anonimizados no LLM), fato gerador, pedidos,
     valor da causa. *"Economiza a leitura de dezenas de laudas."*
   - **Admissibilidade**: semáforo VERDE + checklist (arts. 319/321), método e evidência por item.
4. *Interpretabilidade:* "cada item mostra COMO foi verificado e a evidência — o juiz entende
   **por que** o sistema disse aquilo."

---

## 3. Sprint 1: o diferencial — bloqueio de prompt injection (2 min)

1. Enviar **`data/synthetic/injection_texto_branco.pdf`** (comando oculto em texto branco).
2. Mostrar a **tarja vermelha**: "Risco grave — bloqueado", anomalia, página, evidência.
3. *Dois pontos fortes:*
   - **Determinístico e sem LLM** — encerra antes de qualquer chamada ao modelo (sem custo,
     sem alimentar a IA com conteúdo manipulado).
   - Subsidia o juiz para **multa por litigância de má-fé**.

---

## 4. Sprint 3: multi-domínio — rito trabalhista (1,5 min)

*"A mesma base atende vários ramos; o que muda é a estratégia de admissibilidade por rito
(arquitetura rito-aware, ADR-0008)."*

1. Enviar **`data/synthetic/trabalhista_pedido_iliquido.pdf`** com rito **Trabalhista** →
   **VERMELHO**: checklist acusa **pedido ilíquido** (CLT art. 840 §1º exige valor por pedido).
2. Enviar **`data/synthetic/trabalhista_pedido_liquido.pdf`** (mesmo rito) → **VERDE**.
3. *Ponto arquitetural:* "o mesmo PDF como **cível** não exige pedido líquido. Previdenciário,
   fiscal e família entram como novos encaixes sem reescrever firewall nem extração."

---

## 5. Sprint 4 + 8: confiança & conformidade — revisão humana (1,5 min)

*"Nenhum tribunal adota IA sem controle humano auditável (Res. CNJ 615/2025)."*

1. Na análise exibida, clicar **ACEITAR**, **CORRIGIR** ou **REJEITAR** no `ReviewPanel`;
   adicionar comentário opcional → **Registrar revisão**.
2. A trilha aparece imediatamente abaixo: decisão + comentário + horário.
3. *Falar:* "a trilha é imutável — append-only — e vinculada ao usuário autenticado.
   Cada ação fica registrada para fins de compliance."
4. *Alternativa (Swagger)*: `POST /v1/analyses/{id}/review` + `GET /v1/analyses/{id}/reviews`.
5. *Segurança:* `POST /v1/analyze` sem token → 401 → redirect automático para `/login`;
   lockout após 5 tentativas incorretas.

---

## 6. Sprint 5 + 8: classificação TPU (1 min)

*"3ª capacidade núcleo: sugerir a classe/assunto do CNJ, atacando o gargalo da autuação."*

1. Na análise, rolar até o **`TpuPanel`**: top-3 sugestões com código, descrição, barra de
   confiança e trecho-âncora. *"O assessor vê em qual trecho da petição o sistema se baseou."*
2. Mostrar no terminal:
   ```bash
   uv run python -m evals.run
   # → TPU top-1=1.000  top-3=1.000  (sanidade over seed)
   ```
3. *Honestidade acadêmica:* "avaliação over seed — os números servem de sanidade, não de
   performance em dados não vistos."

---

## 7. Sprint 6: produção — observabilidade e LGPD (1 min)

*"Tornar o sistema operável, observável e conforme."*

1. **Logs** (terminal da API): cada request tem `correlation_id` único, `method`, `path` —
   sem PII.
2. **LGPD**: mostrar no código que `MappedRegexAnonymizer` substitui CPF, CNPJ, e-mail,
   telefone e CEP antes de enviar ao Gemini. Para nomes: `PresidioAnonymizer` (extra `ner`).
3. **Retenção**: `DELETE /v1/analyses?older_than_days=90` remove análises antigas
   (direito ao esquecimento, LGPD art. 18).
4. **Supply-chain**: `uv run pip-audit` — nenhuma vulnerabilidade conhecida.
5. Mostrar **`backend/Dockerfile`** (multi-stage, usuário não-root) e
   **`docker-compose.prod.yml`**.

---

## 8. Sprint 7: integração processual — ingestão assíncrona (1,5 min)

*"Maior ganho de adoção: ingestão direta dos sistemas processuais."*

1. Pela API (Swagger):
   ```json
   POST /v1/ingestion/jobs
   { "source": "SANDBOX", "tribunal": "TJSP",
     "date_from": "2024-01-01", "date_to": "2024-01-07" }
   ```
   → **202 Accepted**, `status: QUEUED`.
2. `GET /v1/ingestion/jobs/{id}` → mostrar status evoluindo de `RUNNING` para `DONE`,
   com `processed` e `failed`.
3. *Design:* "o adapter sandbox usa os PDFs sintéticos que já existem. Trocar por `PjeAdapter`
   real = implementar o mesmo Protocol com credenciais de homologação."
4. *Fila:* "`asyncio.Queue` com worker iniciado no `lifespan` — sem dependência externa (Celery,
   Redis). Escala para fila distribuída na Fase 8+."

---

## 9. Princípios de engenharia/IA (1 min)

- **Agnóstico a LLM:** `SHERPI_LLM_BACKEND` / `SHERPI_LLM_MODEL` → troca provedor sem tocar
  no código (port + adapter). Default Gemini Flash; Maritaca/OpenAI/Ollama plugáveis.
- **Qualidade (medida, não prometida):**
  ```bash
  uv run python -m evals.run   # firewall precision/recall=1.0; extração campo=1.0; TPU top-3=1.0
  uv run pytest -q             # 134 testes verdes
  npm run build && npm run lint # frontend: zero erros TS/ESLint
  ```
- **Rigor:** ruff + mypy strict + pip-audit no CI (gate real). Arquitetura **DDD + hexagonal**.
- **LGPD end-to-end:** anonimização antes do LLM; retenção configurável; extra `ner` para NER
  de nomes (Presidio/spaCy).

---

## 10. Processo ágil (30s — abrir os docs)

- **9 sprints entregues** — backend completo (S1–S7) + frontend completo (S8) + refactor de qualidade (S9/EP12).
- Mostrar rapidamente: [`pmp.md`](pmp.md) (M1–M8 ✅), [`wbs.md`](wbs.md),
  [`backlog.md`](backlog.md), [`agile-process.md`](agile-process.md).

---

## 11. Encerramento (30s)

*"Em 9 sprints entregamos o SHERPI completo — backend e frontend: firewall anti prompt-injection
(inédito no mercado), admissibilidade multi-rito (cível + trabalhista), controle humano
auditável (CNJ 615/2025), classificação TPU, LGPD pronto para produção, ingestão
automatizada de sistemas processuais e UI funcional ponta a ponta. Arquitetura DDD + hexagonal,
134 testes, CI rigoroso, Next.js 16 + React 19."*

---

## Plano B (se algo falhar na hora)

| Problema | Contorno |
|---|---|
| Sem internet / Gemini fora | Demo do **firewall** (§3) é 100 % offline. Trabalhista (§4) e revisão (§5) mostrar pelos testes: `uv run pytest -k "trabalhista or review" -v`. |
| Docker indisponível | Editar `SHERPI_DATABASE_URL=sqlite:///./sherpi.db` no `backend/.env`; rodar `cd backend && uv run alembic upgrade head && make seed-tpu`. |
| Frontend não sobe | Demonstrar tudo pelo Swagger em `http://localhost:8000/docs`. |
| Índice TPU vazio | `tpu_suggestions: null` na resposta — explicar que é o estado sem seed populado; mostrar `eval_tpu()` no terminal. |
| Login falha | Verificar `SHERPI_SEED_USER_PASSWORD` no `.env`; ou mostrar o 401 como feature: "sem token, sem acesso". |

---

## Arquivos de apoio

- **PDFs** (gerados por `uv run python -m synthetic.generate` em `backend/data/synthetic/`):
  `clean_acao_cobranca.pdf`, `injection_texto_branco.pdf`,
  `trabalhista_pedido_liquido.pdf`, `trabalhista_pedido_iliquido.pdf`.
- **Métricas ao vivo:** `uv run python -m evals.run`
- **Testes:** `uv run pytest -q` (134 testes)
- **Contrato da API:** [`tech-spec-sherpi.md`](tech-spec-sherpi.md) §8
- **Swagger local:** `http://localhost:8000/docs`
