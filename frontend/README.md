# SHERPI — Frontend

UI do SHERPI em **Next.js 16 + React 19 + TypeScript + Tailwind v4**. Cobre login, análise (seletor de
rito, laudo do firewall, resumo estruturado, TPU top-3), revisão humana, histórico e auditoria de LLM.

> Visão geral do projeto: [`../README.md`](../README.md). Decisão de arquitetura do frontend:
> [`../docs/adr/0017-frontend-decoupled-spa.md`](../docs/adr/0017-frontend-decoupled-spa.md).

## Arquitetura (resumo)

- **Desacoplado, sem BFF**: o cliente tipado (`src/lib/api.ts`) chama a **API REST diretamente**
  (`NEXT_PUBLIC_API_URL`, `credentials: "include"`). Não há proxy de dados no Next.
- **Auth por cookie httpOnly**: o backend grava o token; o browser o reenvia. O JS **não** lê o token
  (mitiga XSS). Logout via route handler (`src/app/api/logout/route.ts`) que limpa o cookie.
- **Guarda de rota no edge**: `src/proxy.ts` redireciona para `/login` sem cookie de sessão.

### ⚠️ Convenção Next.js 16 — `proxy.ts`, não `middleware.ts`

No **Next.js 16** o antigo *Middleware* (`middleware.ts` / função `middleware`) foi **renomeado para
*Proxy*** (`proxy.ts` / função `proxy`); o nome antigo ainda funciona mas emite *deprecation warning*.
Este projeto **já usa `proxy.ts`** — **não** renomeie de volta para `middleware.ts`.
Ref.: [Renaming Middleware to Proxy](https://nextjs.org/docs/messages/middleware-to-proxy).

## Desenvolvimento

```bash
npm install
npm run dev   # http://localhost:3000  (ou: make dev-frontend na raiz)
```

Requer o backend rodando (`make dev-backend` ou `make dev-backend-fake` na raiz). Configure
`NEXT_PUBLIC_API_URL` se a API não estiver em `http://localhost:8000`.

## Testes E2E (Playwright)

```bash
make e2e       # na raiz; requer `make dev-backend-fake` rodando
make e2e-llm   # cenários com LLM real; requer `make dev-backend`
```
