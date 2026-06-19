# Contribuindo com o SHERPI

Convenções do projeto — **versionadas no repositório**, válidas para qualquer pessoa **e qualquer
ferramenta/agente de IA** (são agnósticas a LLM, como o próprio produto). O [`AGENTS.md`](AGENTS.md)
referencia este documento.

## Idioma e nomenclatura de arquivos

- **Conteúdo** dos documentos e código: **pt-BR** (comentários, docstrings, textos).
- **Nomes de arquivo em `docs/` (e `docs/adr/`)**: **en-US**, em kebab-case ASCII.
  - ✅ `tech-spec-sherpi.md`, `legal-glossary.md`, `0008-multi-domain-architecture.md`
  - ❌ `spec-tecnica.md`, `glossario-juridico.md`, `0008-multi-dominio-...`
- **Siglas**: padrão internacional quando houver — **PMP** (não PGP), **WBS** (não EAP), PRD, DDD, ADR.
  O título/conteúdo pode manter o termo pt-BR entre parênteses (ex.: "PGP / PMP", "EAP / WBS").

## Fluxo de Git

- Entregue sempre na branch **`development`** (commit + push).
- O **merge `development → main`** é feito pelo **mantenedor (usuário)** — não mergeie nem abra PR
  para `main` por conta própria, salvo pedido explícito.
- Commits no estilo *conventional* (`feat:`, `fix:`, `docs:`, `chore:`, `test:`…), mensagem em pt-BR,
  escopados por assunto.

## Qualidade (Definition of Done)

Um item só é "pronto" quando: código + **testes** passando; `ruff` (check + format) e `mypy` limpos;
documentação atualizada; e — para itens de modelo — **métrica medida** no *eval* (nunca prometida).
Tudo isso é gate de CI.

- **mypy strict**: libs sem tipos (PyMuPDF, google-genai) só relaxam `disallow_untyped_calls` no
  adapter que as envelopa (override em `backend/pyproject.toml`) — **nunca** no domínio.
- **Testes sem rede**: domínio puro e firewall são determinísticos; use `FakeProvider` em qualquer
  caminho com LLM. `synthetic`/`evals` são importáveis via `pythonpath = ["."]`.
- **Largura de linha**: responsabilidade do `ruff format` (line-length=100); `E501` fica desligado no
  lint (não mexer em strings/URLs na mão).

## Documentação

- Cada `.md` em `docs/` tem **frontmatter YAML padronizado**; a fonte de verdade dos metadados é
  `scripts/add_frontmatter.py`. Ao criar um doc novo: adicione a entrada no script e rode-o.
- Mantenha o índice [`docs/INDEX.md`](docs/INDEX.md) atualizado e **sem links quebrados**.

## Princípios inegociáveis do produto

Resumo (detalhe no [`AGENTS.md`](AGENTS.md)): **agnóstico a LLM** (acesso só via port `LLMProvider`);
**domínio puro** (hexagonal); **human-in-the-loop** (nunca decisão automática); **synthetic-first /
LGPD** (sem PII real; anonimizar antes de LLM externo).
