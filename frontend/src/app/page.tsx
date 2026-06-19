"use client";

import { useState } from "react";

import { AdmissibilityPanel } from "@/components/AdmissibilityPanel";
import { ForensicsBanner } from "@/components/ForensicsBanner";
import { SummaryPanel } from "@/components/SummaryPanel";
import { analyzePetition, ApiError } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      setResponse(await analyzePetition(file));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro inesperado ao analisar.");
    } finally {
      setLoading(false);
    }
  }

  const result = response?.result;

  return (
    <main className="mx-auto max-w-5xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">SHERPI</h1>
        <p className="text-sm text-gray-500">
          Triagem assistida de petições iniciais — firewall, resumo e admissibilidade.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="flex items-center gap-3">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {loading ? "Analisando…" : "Analisar"}
        </button>
      </form>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <ForensicsBanner report={result.forensics} />
          {result.summary && result.admissibility ? (
            <div className="grid gap-4 md:grid-cols-2">
              <SummaryPanel summary={result.summary} />
              <AdmissibilityPanel report={result.admissibility} />
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              Análise cognitiva não executada — o documento foi bloqueado pelo firewall.
            </p>
          )}
          <p className="text-xs text-gray-400">id da análise: {response?.id}</p>
        </div>
      )}
    </main>
  );
}
