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

### TPU semântica (opcional — JurisBERT + TUA real do CNJ)

Sem o extra `ml`, a sugestão de TPU usa o `FakeEmbeddingModel` (embeddings por hash,
**não-semântico**: ranking determinístico porém sem significado — útil só para dev/CI).
Para sugestões reais, ligue o **JurisBERT** (embeddings jurídicos em PT, ~440 MB, CPU,
sem custo de API) sobre a **Tabela Única de Assuntos real do CNJ** (ADR-0016):

```bash
uv sync --extra ml           # instala torch + transformers (~1,5–3 GB em disco)
make seed-tpu-cnj            # baixa a TUA do CNJ + RE-SEMEIA o índice com JurisBERT — da raiz
make dev-backend             # já sobe com --extra ml (TPU semântica)
```

> ⚠️ **`uv run` reverte o ambiente para o default** (sem o extra `ml`) a cada chamada — por
> isso `--extra ml` precisa ir em **cada** comando que usa JurisBERT. `make seed-tpu-cnj` e
> `make dev-backend` já passam o extra. Se subir o backend manualmente, inclua-o:
> `PYTHONPATH=. uv run --extra ml uvicorn sherpi.interfaces.api.main:app --reload --port 8000`.
> Sem o extra, o embedder cai no Fake (64-dim) ≠ índice JurisBERT (768) e a TPU é desabilitada
> (com erro claro no log, graças ao `SHERPI_TPU_EMBEDDER` — ver ADR-0016).

O `build_tpu_embedder` (em `taxonomy/infrastructure/embedding.py`) usa JurisBERT quando o
extra `ml` está presente e cai no Fake com WARNING caso contrário — nunca degrada em
silêncio. **Build e busca precisam do mesmo embedder**: ao trocar o embedder, re-semeie
(dimensões diferentes não casam; o `search` retorna `[]` e loga se houver mismatch).

- `make seed-tpu` — seed sintético de 30 entradas (rápido; CI/eval).
- `make tpu-catalog` — baixa só o catálogo da TUA (`data/cnj/tpu_assuntos.json`).
- `make seed-tpu-cnj` — TUA real (~1.3k assuntos cível+trabalhista) com JurisBERT.

## Estrutura (bounded contexts)

```
src/sherpi/
  shared_kernel/        # VOs e ports transversais (CPF, CNPJ, ClaimAmount, RiskVerdict, LLMProvider...)
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
uv run python -m synthetic.generate    # gera data/synthetic/ (corpus rotulado, PDFs do zero)

# Petições a partir de templates reais (.docx em docs/templates/) — preenche os
# campos com dados sintéticos e emite .docx + .pdf + ground truth. PDF via
# LibreOffice (soffice). --enrich-llm reescreve a narrativa via LLMProvider.
uv run python -m synthetic.from_template "../docs/templates/2.1 ACIDENTE ....docx" --n 3

# Catálogo de identidades fake (PF/PJ com CPF/CNPJ de checksum válido e dados
# cadastrais coerentes) — fonte única usada por from_template e builder.
uv run python -m synthetic.entities --pf 30 --pj 15   # exporta data/fake_entities.json
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
