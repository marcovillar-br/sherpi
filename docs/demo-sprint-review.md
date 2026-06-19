---
title: "Roteiro de Demo — Sprint Review"
description: "Runbook passo a passo para apresentar o MVP do SHERPI ao professor na Sprint Review."
doc_type: runbook
project: SHERPI
status: approved
version: 1.1
updated: 2026-06-19
language: pt-BR
tags: [demo, sprint-review, runbook, apresentacao]
---

# Roteiro de Demo — Sprint Review (SHERPI)

Runbook para apresentar o **MVP** ao professor. Duração-alvo: **~10 minutos** (8 de demo + 2 de Q&A).
Mensagem central: *"devolver tempo cognitivo ao gabinete, com um firewall inédito contra fraude
algorítmica, sob supervisão humana"*.

## 0. Antes de apresentar (checklist — rodar 15 min antes)

```bash
# 1) Banco — opção A (recomendada): Postgres via Docker
docker compose up -d db
cd backend && export SHERPI_DATABASE_URL="postgresql+psycopg://sherpi:sherpi@localhost:5432/sherpi"
#    opção B (fallback sem Docker): SQLite
#    export SHERPI_DATABASE_URL="sqlite:///./sherpi.db"

# 2) Migrations + corpus de demonstração
uv run alembic upgrade head
uv run python -m synthetic.generate          # gera data/synthetic/*.pdf

# 3) Confirme a chave do Gemini no backend/.env (SHERPI_LLM_API_KEY)

# 4) Suba os serviços (dois terminais)
uv run uvicorn sherpi.interfaces.api.main:app --port 8000      # API
cd ../frontend && npm run dev                                   # UI em http://localhost:3000
```

**Verificação rápida** (deve responder `ok` / `200`):
`curl localhost:8000/health` · abrir `http://localhost:3000`.

> Tenha abertos: o navegador em `localhost:3000`, `http://localhost:8000/docs` (Swagger) e este roteiro.

## 1. Contexto (1 min — falar, sem tela)

- O Judiciário afoga em triagem manual: litigiosidade massiva, **até 60% das iniciais** com vícios,
  petições prolixas (49–116 págs).
- Ameaça nova e concreta: **prompt injection** em PDFs (casos reais Parauapebas/PA e SP) — comandos
  ocultos que enganam a IA e quebram o contraditório.
- SHERPI faz **triagem assistida**: firewall → resumo → admissibilidade. **Sempre apoio, nunca decisão
  automática** (Res. CNJ 615/2025).

## 2. Caminho feliz — petição limpa (2 min)

1. Na UI, enviar **`data/synthetic/clean_acao_cobranca.pdf`** → clicar **Analisar**.
2. Mostrar, lado a lado:
   - **Laudo de integridade**: verde "Documento íntegro".
   - **Resumo estruturado**: partes (com CPF/CNPJ), fato gerador sintetizado, fundamentação, pedidos,
     valor da causa. *Falar:* "isto economiza a leitura de dezenas de laudas".
   - **Admissibilidade**: semáforo + checklist (arts. 319/321) com **método** e **evidência** por item.
3. *Ponto de interpretabilidade:* "cada item mostra como foi verificado (determinístico vs. semântico)
   e a evidência — o juiz entende **por que** o sistema disse aquilo".

> O semáforo pode vir **amarelo** se a peça não mencionar procuração — é correto (vício menor, sem
> exigir emenda). Use isso para explicar os três níveis (verde/amarelo/vermelho).

## 3. O diferencial — bloqueio de prompt injection (2 min)

1. Enviar **`data/synthetic/injection_texto_branco.pdf`** (tem comando oculto em texto branco).
2. Mostrar a **tarja vermelha**: "Risco grave — bloqueado", com as anomalias (branco-no-branco +
   comando à IA), página e o trecho-evidência.
3. *Falar os 2 pontos fortes:*
   - **Determinístico e sem LLM** — o fluxo encerra **antes** de qualquer chamada ao modelo (não
     gasta token e não alimenta a IA com conteúdo manipulado).
   - Subsidia o juiz para **multa por litigância de má-fé** (torna visível o que era invisível).

## 4. Multi-domínio — rito trabalhista (1,5 min — Sprint 3)

*Mensagem:* "a mesma base atende vários ramos; o que muda é a regra de admissibilidade
por rito (arquitetura rito-aware, ADR-0008). O trabalhista é o primeiro encaixe."

1. Enviar **`data/synthetic/trabalhista_pedido_iliquido.pdf`** selecionando o rito
   **Trabalhista** → resultado **VERMELHO**: o checklist acusa **pedido ilíquido**
   (CLT art. 840 §1º exige valor por pedido), listando os pedidos sem valor como evidência.
2. Enviar **`data/synthetic/trabalhista_pedido_liquido.pdf`** (mesmo rito) → **VERDE**:
   cada pedido vem com valor; requisito de pedido líquido atendido.
3. *Falar o ponto arquitetural:* "a mesma petição enviada como **cível** não exigiria
   pedido líquido — a regra é plugável por rito, sem reescrever firewall nem extração.
   Previdenciário, fiscal e família entram como novos encaixes."

> Pela API (Swagger), o rito é o campo `rito` do `POST /v1/analyze` (default cível;
> valor inválido → 422).

## 5. Princípios de engenharia/IA (1,5 min — pode usar o Swagger e o terminal)

- **Agnóstico a LLM:** mostrar no `.env` que trocar `SHERPI_LLM_BACKEND`/`SHERPI_LLM_MODEL` troca o
  provedor sem tocar no código (port + adapter). Default Gemini Flash; Maritaca/OpenAI/Ollama plugáveis.
- **LGPD:** o texto é **anonimizado** (CPF/CNPJ/e-mail/telefone) antes de ir ao LLM externo; a
  validação de CPF/CNPJ roda no texto original (não degrada). Dados de teste são **sintéticos**.
- **Qualidade (medida, não prometida):** no terminal, `uv run python -m evals.run` →
  firewall precision/recall=1.0 e acurácia de campo da extração.
- **Rigor:** `uv run pytest` (78 testes) · CI verde (ruff/mypy/test/eval) · arquitetura **DDD + hexagonal**.

## 6. Processo ágil (1,5 min — abrir os docs)

- **MVP em 2 sprints** entregue (firewall + extração + admissibilidade + UI + persistência).
- Mostrar rapidamente: **PGP** ([`pmp.md`](pmp.md)), **EAP** ([`wbs.md`](wbs.md)), **Backlog**
  produto×sprint ([`backlog.md`](backlog.md)), **processo** com Design Sprint e papéis
  ([`agile-process.md`](agile-process.md)).
- **Visão de futuro (Fase 4):** TPU (classificação CNJ), autenticação, auditoria/human-in-the-loop
  completo, anonimização de nomes (NER), integração PJe.

## 7. Encerramento (30s)

"Em 2 semanas entregamos um MVP funcional que ataca os três gargalos da triagem, com um diferencial
sem similar no mercado — o firewall anti prompt-injection — e arquitetura pronta para produção."

---

## Plano B (se algo falhar na hora)

| Problema | Contorno |
|---|---|
| Sem internet / Gemini fora | A **demo do firewall** (passo 3) é 100% offline e determinística — priorize-a. O resumo (passo 2) e o **trabalhista** (passo 4) dependem da extração via LLM (rede); se cair, mostre o contraste líquido/ilíquido pelos testes (`uv run pytest -k trabalhista`). |
| Docker indisponível | Usar o fallback **SQLite** (`SHERPI_DATABASE_URL=sqlite:///./sherpi.db`) — mesma camada de repositório. |
| Frontend não sobe | Demonstrar pela API em `http://localhost:8000/docs` (Swagger): `POST /v1/analyze` com upload do PDF. |
| Modelo Gemini indisponível | Listar modelos e ajustar `SHERPI_LLM_MODEL` (ex.: `gemini-2.5-flash`). |

## Arquivos de apoio
- PDFs (gerados por `synthetic.generate` em `backend/data/synthetic/`):
  `clean_acao_cobranca.pdf`, `injection_texto_branco.pdf`,
  `trabalhista_pedido_liquido.pdf`, `trabalhista_pedido_iliquido.pdf`.
- Métricas ao vivo: `uv run python -m evals.run`.
- Contrato da API: [`tech-spec-sherpi.md`](tech-spec-sherpi.md) §8.
