---
title: "ADR-0017: Frontend desacoplado — cliente direto à API, cookie httpOnly e guarda de rota (Next.js Proxy)"
description: "Adotar um frontend Next.js desacoplado que consome a API diretamente (cliente tipado), com autenticação por cookie httpOnly e proteção de rotas via Proxy do Next.js (proxy.ts, ex-middleware) — explicitamente NÃO um BFF que faz proxy de dados."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-22
language: pt-BR
tags: [adr, frontend, nextjs, auth, jwt, proxy]
---

# ADR 0017 — Frontend desacoplado (cliente direto à API + guarda de rota via Proxy do Next)

**Status**: Aceito · **Relaciona-se a** [ADR-0007](0007-auth-jwt-single-profile.md) (JWT)

## Contexto

O SHERPI tem um frontend **Next.js 16 + React 19** separado do backend FastAPI. Era preciso registrar
**como o frontend conversa com a API** e **como protege rotas autenticadas**.

A dúvida recorrente é se haveria um **BFF (Backend-for-Frontend)** — uma camada server-side do Next que
faz **proxy/agregação** das chamadas à API. O termo "BFF" circulou informalmente, mas a implementação
**não** é um BFF: o `frontend/src/lib/api.ts` chama a API **diretamente** do browser
(`NEXT_PUBLIC_API_URL`, `fetch(..., { credentials: "include" })`). Não há proxy de dados no Next.

**Cuidado com a nomenclatura do Next.js 16.** A partir do Next 16, o antigo *Middleware* foi
**renomeado para *Proxy*** (arquivo `middleware.ts` → **`proxy.ts`**, função `middleware` → **`proxy`**);
o nome "proxy" reflete que ele roda **no edge, à frente da app** (não é o Express-middleware nem um BFF
de dados). O nome antigo `middleware.ts` ainda funciona, porém **emite *deprecation warning*** e deve ser
evitado. O projeto **já migrou** para a convenção nova (commit `4f3464e`), e é isso que está em produção:

- `frontend/src/proxy.ts` exporta `proxy(request)` com `config.matcher` isentando `login`, assets e
  `favicon` → redireciona para `/login` quando **não há cookie de sessão**. **Essa guarda está ATIVA**
  (é a convenção corrente do Next 16) — não confundir com o arquivo morto que seria `middleware.ts`.

> Correção de rota: uma alteração local chegou a propor renomear `proxy.ts → middleware.ts`. Isso
> **reverteria** para a forma deprecada e foi **descartado**. Mantém-se `proxy.ts`/`proxy`.

## Decisão

1. **Frontend desacoplado, sem BFF**: o cliente tipado (`lib/api.ts`) consome a API REST **diretamente**.
   Trade-off aceito: depende de **CORS restrito** + **cookie httpOnly** (ver `security.md`), em troca de
   simplicidade (sem uma segunda camada de rede para manter).
2. **Autenticação por cookie httpOnly**: o backend emite o token no login e o grava como cookie
   **httpOnly + Secure + SameSite**; o browser o reenvia automaticamente (`credentials: "include"`). O
   JS do cliente **não** lê o token (mitiga exfiltração por XSS).
3. **Logout via route handler**: `frontend/src/app/api/logout/route.ts` apaga o cookie (`maxAge: 0`) —
   único uso de código server-side do Next, e **não** é proxy de dados.
4. **Guarda de rota via Proxy do Next** (`proxy.ts`/`proxy`, convenção Next 16): redireciona para
   `/login` sem cookie de sessão. **Manter** essa convenção; **não** voltar a `middleware.ts` (deprecado).

## Consequências

**Positivas**
- Arquitetura simples e auditável; uma única fonte de verdade de contrato (a API, ver [`openapi.json`](../openapi.json)).
- Cookie httpOnly reduz superfície de XSS; guarda no edge evita *flash* de páginas protegidas.
- Frontend e backend evoluem e escalam de forma independente.

**Negativas / trade-offs**
- Exige **CORS** correto e cookies cross-site bem ajustados (atenção a `SameSite` em produção com
  domínios distintos).
- A guarda no edge é **defesa de UX/navegação**, **não** de autorização: a autorização real é sempre do
  **backend** (valida o JWT e nega 401/403). Não confiar na guarda como controle de acesso.
- Acompanhar a evolução do *Proxy* no Next (API ainda recente pós-rename).

**Riscos aceitos**
- Sem RBAC no MVP (herdado do [ADR-0007](0007-auth-jwt-single-profile.md)); `role` viaja no JWT mas não
  há enforcement por rota — Fase 4.

## Alternativas consideradas

- **BFF (proxy de dados no Next)**: ocultaria a API e centralizaria cookies/segredos, mas adiciona uma
  camada de rede e de manutenção desnecessária para um MVP com uma API única e já versionada.
  **Rejeitado** por custo/benefício — reabrir se surgir necessidade de agregação ou de esconder a origem.
- **Token em `localStorage`**: simples, porém exposto a XSS. **Rejeitado** em favor de cookie httpOnly.
- **Reverter para `middleware.ts`**: **rejeitado** — é a convenção **deprecada** no Next 16.
