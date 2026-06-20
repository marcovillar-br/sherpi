# SHERPI — Backend

Sistema Híbrido de Extração e Resumo Estruturado de Petições Iniciais.
Monólito modular **DDD + hexagonal (ports & adapters)**, agnóstico a LLM.

Documentação de produto e arquitetura: [`../docs/`](../docs/)
(PRD, spec técnica, roadmap, mapa de contextos DDD, ADRs, modelo de ameaças).

## Pré-requisitos

- Python ≥ 3.12 e [uv](https://docs.astral.sh/uv/)
- Docker (apenas para o PostgreSQL — ver [ADR-0006](../docs/adr/0006-docker-db-only.md))

## Setup

```bash
uv sync                      # instala dependências
cp .env.example .env         # configure SHERPI_LLM_API_KEY, SHERPI_JWT_SECRET, etc.
docker compose up -d db      # sobe PostgreSQL 16 (a partir da raiz do repo)
```

## Estrutura (bounded contexts)

```
src/sherpi/
  shared_kernel/        # VOs e ports transversais (CPF, CNPJ, ValorCausa, RiskVerdict, LLMProvider...)
  contexts/
    document_integrity/ # ✅ firewall anti prompt-injection (domain puro + PyMuPDF adapter)
    petition_analysis/  # ✅ extração + admissibilidade rito-aware (core domain)
    taxonomy/           # ✅ classificação TPU (embedding + k-NN)
    review/             # ✅ human-in-the-loop + auditoria append-only
    identity/           # ✅ autenticação JWT (perfil único)
    integration/        # ✅ ingestão assíncrona (PJe/E-Proc/sandbox)
  application/          # orquestrador cross-context (analyze_petition)
  infrastructure/       # adapters: llm/ (Gemini/Grok/Anthropic) · persistence/ · storage/ · anonymization/
  interfaces/api/       # FastAPI
synthetic/              # gerador de PDFs sintéticos rotulados (dev/eval, fora do pacote)
tests/                  # pytest
```

## Comandos

```bash
uv run pytest                          # testes (domínio puro + integração do firewall)
uv run ruff check . && uv run ruff format --check .
uv run mypy src/                       # type check strict
uv run python -m synthetic.generate    # gera data/synthetic/ (corpus rotulado)
```

## Status

Sistema completo (Sprints 1–9): firewall, extração + admissibilidade **rito-aware**
(cível/trabalhista), TPU, identidade/JWT, revisão/auditoria append-only, ingestão assíncrona
e UI. LLM **agnóstico** (Gemini default; Grok/Anthropic trocáveis por config), com PII
anonimizada (CPF/CNPJ/e-mail/telefone/CEP **e nomes**) antes do envio externo.

O contexto **document_integrity** (o firewall — diferencial do produto) detecta
branco-no-branco, fonte microscópica, texto fora da CropBox, Unicode invisível,
/ActualText divergente, metadados e comandos de injeção em texto oculto — de forma
**determinística e sem LLM**, interrompendo o fluxo (veredito `BLOCK`) antes de qualquer
gasto de token; também sinaliza PDFs **sem camada de texto** (imagem/escaneado). Cobertura
por testes de unidade (domínio) e integração (PDF→parser→laudo).
