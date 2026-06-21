# Contribuindo com o SHERPI

Convenções do projeto — **versionadas no repositório**, válidas para qualquer pessoa **e qualquer
ferramenta/agente de IA** (são agnósticas a LLM, como o próprio produto). O [`AGENTS.md`](AGENTS.md)
referencia este documento.

## Idioma — regra geral

Duas camadas, regra clara:

| Camada | Idioma | Justificativa |
|---|---|---|
| Código Python — identificadores, constantes internas, chaves de dicionário, nomes de arquivo referenciados no código | **en-US** | PEP 8; interoperabilidade com libs e ferramentas anglófonas |
| Saída para o usuário — UI, mensagens de erro, labels de API, logs legíveis por humanos | **pt-BR** | língua do público-alvo (gabinete judicial brasileiro) |
| Conteúdo de `docs/` e comentários Python | **pt-BR** | documentação interna do time |
| Nomes de arquivo em `docs/` (e `docs/adr/`) | **en-US**, kebab-case ASCII | descoberta por ferramentas; convenção do projeto |
| Siglas | padrão internacional — **PMP** (não PGP), **WBS** (não EAP) | — |

**`trabalhista`** é exceção documentada: termo jurídico brasileiro sem equivalente en-US limpo;
aceito em ambas as camadas (código e dados).

### O que NÃO fazer

```python
# ❌ identificador em pt-BR — viola PEP 8 e confunde ferramentas
def build_integra() -> bytes: ...
category = "injecao"

# ✅ identificador en-US; saída para o usuário em pt-BR
def build_clean() -> bytes: ...
category = "clean"
raise ValueError("Documento bloqueado pelo firewall.")  # mensagem pt-BR: ok
```

### Corpus sintético (`backend/data/synthetic/`)

Convenção de nome de arquivo: `<categoria>_<cenario>.pdf`

- Categorias en-US: `clean_*`, `defect_*`, `injection_*`
- Categoria exceção: `trabalhista_*` (termo jurídico)
- Cenários em pt-BR (descrevem a situação jurídica): `clean_acao_cobranca.pdf`, `injection_texto_branco.pdf`

### Nomes de arquivo em `docs/`

- ✅ `tech-spec-sherpi.md`, `legal-glossary.md`, `0008-multi-domain-architecture.md`
- ❌ `spec-tecnica.md`, `glossario-juridico.md`, `0008-multi-dominio-...`

## Fluxo de Git

- **Nunca** commite nem dê push **direto na `development`**. Toda mudança vai em um **feature-branch**
  (`feat/…`, `fix/…`, `docs/…`, `chore/…`) e entra na `development` **via Pull Request**.
- O **merge `development → main`** é feito pelo **mantenedor (usuário)** — não mergeie nem abra PR
  para `main` por conta própria, salvo pedido explícito.
- Commits no estilo *conventional* (`feat:`, `fix:`, `docs:`, `chore:`, `test:`…), mensagem em pt-BR,
  escopados por assunto.
- **Nome do branch**: `<tipo>/<descrição-curta>` em kebab-case. Tipos válidos: `feat`, `fix`, `docs`,
  `refactor`, `test`, `chore` (os mesmos do conventional commit). Ex.: `fix/ci-ruff-baseline`,
  `docs/git-conventions-pr-template`.
- **Base do PR**: sempre `development` — **nunca empilhe** um PR sobre outro feature-branch. Se um
  trabalho depende de mudança ainda não mesclada, **serialize**: mescle o pai, atualize a `development`
  (`git pull`), rebaseie o filho e só então abra o PR. *(PR empilhado é frágil: ao mesclar o pai com
  `--delete-branch`, o GitHub pode não re-apontar a base do filho — que acaba mesclado no branch órfão
  e não chega à `development`. Após cadeias de merge, confirme que o conteúdo está na `development` e
  remova branches órfãos.)*

**Por que PR (e não push direto):** o CI roda em `pull_request` — sem PR, nada é validado antes de
entrar na `development`. O PR é o portão onde lint/type/test/eval rodam.

**Enforcement (o "nunca" é técnico, não só convenção):**

- **Branch protection** na `development` no GitHub: exige PR, bloqueia push direto (inclusive de
  admin) e force-push/deleção. Em emergência, o mantenedor desabilita a proteção temporariamente.
- **Hook local** (`.claude/hooks/block-direct-development.sh`, ligado em `.claude/settings.json`):
  recusa `git commit`/`git push` direto na `development` já no agente, antes de chegar ao GitHub.

**Antes de abrir o PR:**

- **Audite o stage** — confirme que nenhum segredo, chave de API ou `.env` entrou (revise
  `git diff --cached`). Segredos só em `.env` local (ignorado); apenas `.env.example` é versionado.
- **Rode os gates localmente** (`ruff` check+format, `mypy`, `pytest`) — o CI repete, mas falhar local
  poupa um ciclo. **Em dev/WSL, prefira `make test-sliced`** (suíte fatiada por domínio) a `make test`:
  rodar tudo de uma vez pode esgotar recursos e derrubar a sessão. Use `make test-domain D=<dir>` para
  um domínio. O `pytest-timeout` (config no `pyproject`) corta qualquer teste pendurado.
- **Não misture** mudanças não relacionadas no mesmo PR: um PR, um assunto.
- O corpo do PR segue [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) — o GitHub
  o injeta automaticamente; via `gh pr create`, **omita `--body`** para puxá-lo.

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
