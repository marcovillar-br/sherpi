// Cliente tipado da API do SHERPI.

import type { AnalyzeResponse } from "./types";

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

/** Envia o PDF para análise e retorna o resultado consolidado. */
export async function analyzePetition(file: File): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/v1/analyze`, { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((b: { detail?: string }) => b.detail)
      .catch(() => undefined);
    throw new ApiError(res.status, detail ?? `Falha na análise (HTTP ${res.status}).`);
  }
  return (await res.json()) as AnalyzeResponse;
}
