// Guarda de rota no edge (Next.js 16): redireciona para /login sem cookie de sessão.
//
// ⚠️ Convenção Next.js 16: este recurso era o "Middleware" (middleware.ts / função
// `middleware`) e foi RENOMEADO para "Proxy" (proxy.ts / função `proxy`). O nome antigo
// ainda funciona mas emite *deprecation warning*. Mantenha este arquivo como `proxy.ts`
// exportando `proxy` — NÃO renomeie de volta para `middleware.ts`. Não é um BFF (o cliente
// chama a API diretamente). Decisão registrada em docs/adr/0017-frontend-decoupled-spa.md.
// Ref: https://nextjs.org/docs/messages/middleware-to-proxy
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const token = request.cookies.get("access_token");
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!login|_next/static|_next/image|favicon.ico).*)"],
};
