# Changelog

Todas as mudanças notáveis deste projeto são registradas aqui. Conteúdo em **pt-BR**.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o
projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

> O histórico detalhado de entregas por sprint está em [`docs/roadmap.md`](docs/roadmap.md)
> e [`docs/backlog.md`](docs/backlog.md); as decisões de arquitetura, em [`docs/adr/`](docs/adr/).

## [Não publicado]

### Corrigido

Auditoria de consistência documentação↔código (PRs #39–#42), tendo o **código como
fonte de verdade**. Drift factual corrigido na documentação e em docstrings:

- **Arquitetura/naming** (#39): removidos do `shared_kernel` os VOs inexistentes
  `Documento` e `Role` (este pertence ao contexto `identity`); `ValorCausa` →
  `ClaimAmount` (refactor en-US da Sprint 9); firewall passa a constar com **8 vetores**
  (inclui `INJECTION_KEYWORDS`, CRITICAL), não 7; `BlobStorage` descrito como port sem
  adapter no MVP (LocalFS/S3 na Fase 4); docstring de `LLMProvider` deixa de citar
  adapters inexistentes (Maritaca/OpenAI/Ollama).
- **ADRs** (#40): ADR-0006 alinhado à imagem `postgres:16` pura (sem pgvector/MinIO);
  ADR-0009 descreve o ranking k-NN híbrido real (cosseno + léxico/IDF + dedupe);
  ADR-0015 anota a evolução do prompt para v5; ADR-0016 corrige "substitui o seed
  sintético" para fonte **opt-in** (`--source cnj`), sintético segue default no CI/eval.
- **Terminologia LGPD** (#40): docstrings de anonimização passam a tratar o masking
  reversível como **pseudonimização** (art. 5º XI), não anonimização (ADR-0012); nomes
  de classe mantidos por estabilidade.
- **Segurança/observabilidade** (#41): Sentry registrado como soft-dependency já no MVP
  (via `SHERPI_SENTRY_DSN`), não Fase 4; documentado que o adapter de anonimização
  injetado em runtime é o `MappedRegexAnonymizer`/`MappedRegexNameAnonymizer`.
- **Contagens e descrições** (#41, #42): contagem de testes datada como snapshot por
  sprint (196 no fechamento da S9 vs. 282 atual); ocorrências residuais de `ValorCausa`
  e "7 vetores" eliminadas em roadmap/backlog/agile-process/README do backend.

### Alterado

- Descrição do upload na API de "PDF" para "PDF ou DOCX" (DOCX é suportado, ADR-0013);
  `docs/openapi.json` regenerado para refletir (#41).

### Adicionado

- Este `CHANGELOG.md`.

## [0.1.0] — MVP

Primeira versão do SHERPI (backend + frontend): firewall anti prompt-injection,
extração estruturada e admissibilidade rito-aware (cível/trabalhista), classificação
TPU sobre a TUA real do CNJ, revisão humana com auditoria append-only, ingestão
assíncrona e UI em Next.js 16. Detalhes por sprint em [`docs/roadmap.md`](docs/roadmap.md).
