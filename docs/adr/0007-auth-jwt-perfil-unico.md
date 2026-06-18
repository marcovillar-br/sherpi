---
title: "ADR-0007: Autenticação JWT com perfil único"
description: "Autenticação JWT com perfil único — contexto, decisão e consequências."
doc_type: adr
project: SHERPI
status: accepted
version: 1.0
updated: 2026-06-18
language: pt-BR
tags: [adr, arquitetura, decisao]
---

# ADR 0007 — Autenticação JWT com perfil único extensível a RBAC

**Status**: Aceito

## Contexto

A Resolução CNJ 615/2025 exige supervisão humana auditável: cada ação precisa estar vinculada a uma identidade. O MVP precisa de login obrigatório, mas não de autorização granular completa. Sobre-engenheirar RBAC/MFA/refresh tokens consumiria tempo do MVP.

## Decisão

Implementar **login obrigatório com perfil único** no contexto `identity`: OAuth2 **password flow** + **JWT** (com expiração), hash **bcrypt**, usuário semeado via `.env`, cookie **httpOnly + Secure + SameSite** no Next.js. O modelo `User` tem campo `role` **extensível a RBAC**, mas o MVP faz apenas **autenticação** (sem autorização granular). RBAC, refresh tokens e MFA ficam para a Fase 4.

## Consequências

**Positivas**

- Dá identidade à trilha de auditoria (conformidade CNJ 615/2025).
- Simples de implementar no prazo; modelo já preparado para RBAC.
- Cookie httpOnly mitiga roubo de token via XSS.

**Negativas / trade-offs**

- Sem autorização granular no MVP: todo usuário autenticado tem o mesmo acesso.
- JWT sem refresh token exige re-login na expiração — aceitável no MVP, resolvido na Fase 4.
- Necessário lockout/rate-limit no login para mitigar brute-force (ver security.md).
