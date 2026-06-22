---
name: lgpd-compliance
description: >-
  Conformidade com a LGPD (Lei 13.709/2018) aplicada ao SHERPI. Use ao tocar em
  PII, masking/anonimização, envio de texto a LLM externo, persistência de
  resumos com dados das partes, retenção/eliminação, logs, ou ao redigir/revisar
  docs de segurança e privacidade. Traz a distinção carregada entre
  anonimização (irreversível, fora do escopo) e pseudonimização (reversível,
  continua sendo dado pessoal) — que governa o que o SHERPI pode e não pode
  afirmar sobre conformidade.
---

# LGPD aplicada ao SHERPI

> **Não é parecer jurídico.** Primer de engenharia para decidir com consistência ao mexer em
> dados pessoais. Itens de enquadramento merecem validação de um(a) advogado(a). Conteúdo pt-BR.

## Quando este skill se aplica

Ative quando o trabalho envolver: masking/anonimização de PII, o port `Anonymizer`/`ReversibleAnonymizer`,
envio de texto a LLM **externo** (Gemini/Grok/Anthropic), persistência do `PetitionSummary` com dados
das partes, logs que possam conter PII, retenção/eliminação, ou redação de `security.md` / `threat-model.md` /
`legal-glossary.md` / ADRs de privacidade.

## As definições que decidem tudo (Lei 13.709/2018)

| Conceito | Artigo | Definição (resumo) | Efeito na LGPD |
|---|---|---|---|
| **Dado pessoal** | art. 5º, I | informação sobre pessoa natural **identificada ou identificável** | dentro do escopo |
| **Dado pessoal sensível** | art. 5º, II | origem racial/étnica, saúde, vida sexual, dado genético/biométrico, convicção etc. | escopo + base legal **mais estrita** (art. 11) |
| **Anonimização** | art. 5º, III + **art. 12** | dado que **não pode** ser reassociado ao titular, com meios razoáveis | **sai do escopo** da LGPD |
| **Pseudonimização** | art. 5º, XI | dado que perde a associação ao titular **exceto pelo uso de informação adicional mantida em separado** | **continua sendo dado pessoal** |

**Regra de ouro (art. 12, caput):** a isenção da LGPD vale só para anonimização **irreversível** com
esforços razoáveis. Se existe um **mapa de reversão** guardado, é **pseudonimização** → dado pessoal,
escopo pleno. Pseudonimização **reduz risco**, **não isenta** de obrigação.

```
Existe forma de voltar ao valor real (mapa, chave, tabela)?
  ├─ NÃO (irreversível) ............ ANONIMIZAÇÃO → fora do escopo da LGPD (art. 12)
  └─ SIM (mapa em separado) ........ PSEUDONIMIZAÇÃO (art. 5º XI) → continua dado pessoal
```

## Como o SHERPI se enquadra (estado real do código)

O fluxo é: **synthetic-first** → mascarar-antes-do-LLM → **restaurar no resumo** → JWT.

- O masking que vai ao LLM externo (`MappedRegexAnonymizer`/`MappedRegexNameAnonymizer`,
  `deanonymize_model`) **retém o mapa** `[CPF_1]→529.982.247-25` e **restaura** os valores no resumo do
  revisor (ADR-0012). Juridicamente isso é **pseudonimização** (art. 5º, XI) — **não** anonimização,
  apesar do nome das classes.
- **Consequências corretas e já assumidas:** o **resumo persistido contém PII** (dado pessoal pleno —
  JWT; cripto em repouso = Fase 4). O **prompt de auditoria** fica pseudonimizado (é o que o LLM viu).
- A **garantia real de "sem PII"** no MVP vem do **synthetic-first** (dados sintéticos), não do masking.
- Masking de **nomes é best-effort** (regex por âncora): nomes citados livremente nos fatos **podem
  vazar**. Cobertura completa = **NER (Presidio)**, Fase 4. Não troque NER por regex novo: vira
  gato-e-rato.

## Checklist ao mexer em PII (use em PRs)

- [ ] Estou chamando de "anonimização" algo **reversível**? → corrija para **pseudonimização** (ou
      "anonimização reversível (= pseudonimização)" para preservar o nome do componente).
- [ ] O **mapa de reversão** fica **em separado** do dado pseudonimizado e com acesso controlado?
- [ ] Nenhum **valor real de PII** vai para **log** (nem em DEBUG)? O que se persiste para auditoria é o
      texto pseudonimizado.
- [ ] Texto enviado a **LLM externo** passou pelo masking quando `is_external_llm`? (LLM local = no-op.)
- [ ] Resumo persistido com PII está atrás de **JWT**? Cripto em repouso documentada como Fase 4?
- [ ] Afirmação de conformidade não promete **isenção da LGPD** por causa de masking reversível?
- [ ] Há **dado sensível** (saúde/biometria — comum em previdenciário/família)? Base legal art. 11,
      tratamento mais restrito, segredo de justiça.

## Linguagem correta nos docs

- ✅ "**pseudonimização** das partes antes do LLM externo (art. 5º, XI)"
- ✅ "anonimização **reversível** (= pseudonimização sob a LGPD)" — quando precisar citar o nome do código
- ✅ "**anonimização**" sem ressalva **só** quando for irreversível (não é o caso do MVP)
- ❌ "anonimização tira os dados do escopo da LGPD" — falso para masking reversível
- ⚠️ `Anonymizer`, `RegexAnonymizer`, `MappedRegexAnonymizer` são **nomes de código** (substantivos
  próprios) — não os renomeie no texto; explique o conceito ao lado.

## Referências

- **LGPD — Lei 13.709/2018**: arts. 5º (I, II, III, XI), 7º (bases legais), 11 (dados sensíveis),
  12 (anonimização fora do escopo), 13 §4º (pseudonimização em pesquisa em saúde), 46 (segurança),
  37–38 (registro/DPIA). Texto oficial: planalto.gov.br.
- **ANPD** (Autoridade Nacional de Proteção de Dados): orientações sobre dados anonimizados/pseudonimizados.
- **Resolução CNJ 615/2025**: IA no Judiciário (human-in-the-loop) — complementa, não substitui a LGPD.
- Internas: [`docs/legal-glossary.md`](../../../docs/legal-glossary.md),
  [`docs/security.md`](../../../docs/security.md), [`docs/threat-model.md`](../../../docs/threat-model.md),
  ADRs [0010](../../../docs/adr/0010-name-masking-regex-vs-ner.md) (regex×NER) e
  [0012](../../../docs/adr/0012-reversible-anonymization-restore.md) (restauração no resumo).
