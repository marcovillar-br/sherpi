// Cliente tipado da API do SHERPI.

import type {
  AnalysisSummary,
  AnalyzeResponse,
  AuditEvent,
  ReviewDecision,
  Rito,
  TokenResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...init,
  });
  return res;
}

async function expectOk(res: Response): Promise<Response> {
  if (!res.ok) {
    const detail = await res
      .json()
      .then((b: { detail?: string }) => b.detail)
      .catch(() => undefined);
    throw new ApiError(res.status, detail ?? `Erro HTTP ${res.status}.`);
  }
  return res;
}

/** Encerra a sessão: apaga o cookie httpOnly via route handler do Next.js. */
export async function logout(): Promise<void> {
  await fetch("/api/logout", { method: "POST" });
}

/** Autentica com email+senha; o backend define o cookie httpOnly. */
export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password });
  const res = await apiFetch("/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  return (await expectOk(res)).json() as Promise<TokenResponse>;
}

/** Envia o PDF para análise e retorna o resultado consolidado. */
export async function analyzePetition(
  file: File,
  rito: Rito = "CIVEL",
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("rito", rito);
  const res = await apiFetch("/v1/analyze", { method: "POST", body: form });
  return (await expectOk(res)).json() as Promise<AnalyzeResponse>;
}

/** Lista o histórico de análises (resumos, mais recentes primeiro). */
export async function listAnalyses(): Promise<AnalysisSummary[]> {
  const res = await apiFetch("/v1/analyses");
  return (await expectOk(res)).json() as Promise<AnalysisSummary[]>;
}

/** Recupera uma análise salva pelo id (resultado completo). */
export async function getAnalysis(id: string): Promise<AnalyzeResponse> {
  const res = await apiFetch(`/v1/analyses/${id}`);
  return (await expectOk(res)).json() as Promise<AnalyzeResponse>;
}

/** Registra uma decisão de revisão humana sobre uma análise. */
export async function submitReview(
  analysisId: string,
  decision: ReviewDecision,
  comment?: string,
): Promise<AuditEvent> {
  const res = await apiFetch(`/v1/analyses/${analysisId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, comment: comment ?? null }),
  });
  return (await expectOk(res)).json() as Promise<AuditEvent>;
}

/** Retorna a trilha de revisões de uma análise. */
export async function getReviews(analysisId: string): Promise<AuditEvent[]> {
  const res = await apiFetch(`/v1/analyses/${analysisId}/reviews`);
  return (await expectOk(res)).json() as Promise<AuditEvent[]>;
}
