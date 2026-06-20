"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { AdmissibilityPanel } from "@/components/AdmissibilityPanel";
import { ForensicsBanner } from "@/components/ForensicsBanner";
import { ReviewPanel } from "@/components/ReviewPanel";
import { SummaryPanel } from "@/components/SummaryPanel";
import { TpuPanel } from "@/components/TpuPanel";
import { analyzePetition, logout, ApiError } from "@/lib/api";
import type { AnalyzeResponse, Rito } from "@/lib/types";

const RITOS: { value: Rito; label: string }[] = [
  { value: "CIVEL", label: "Cível" },
  { value: "TRABALHISTA", label: "Trabalhista" },
];

export default function Home() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [rito, setRito] = useState<Rito>("CIVEL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);

  function selectFile(f: File | null) {
    if (f && f.type !== "application/pdf") {
      setError("Selecione um arquivo PDF.");
      return;
    }
    setFile(f);
    setResponse(null);
    setError(null);
  }

  function clearFile() {
    selectFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      setResponse(await analyzePetition(file, rito));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Erro inesperado ao analisar.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  const result = response?.result;

  return (
    <main className="mx-auto max-w-5xl space-y-6 p-6">
      <header className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">SHERPI</h1>
          <p className="text-sm text-gray-500">
            Triagem assistida de petições iniciais — firewall, resumo e admissibilidade.
          </p>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-gray-900"
        >
          Sair
        </button>
      </header>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-gray-200 p-4"
      >
        <h2 className="text-sm font-semibold text-gray-800">Nova análise</h2>

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => selectFile(e.target.files?.[0] ?? null)}
        />

        <div
          role="button"
          tabIndex={0}
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            setDragActive(false);
          }}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            selectFile(e.dataTransfer.files?.[0] ?? null);
          }}
          className={`flex cursor-pointer flex-col items-center justify-center gap-1 rounded-md border-2 border-dashed px-4 py-8 text-center transition-colors ${
            dragActive ? "border-gray-900 bg-gray-50" : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <span className="text-2xl text-gray-400" aria-hidden>
            ⬆
          </span>
          <span className="text-sm text-gray-600">
            Arraste o PDF aqui ou{" "}
            <span className="font-medium text-gray-900">clique para selecionar</span>
          </span>
        </div>

        {file && (
          <div className="flex items-center justify-between rounded-md bg-gray-50 px-3 py-2 text-sm">
            <span className="truncate text-gray-700">
              <span aria-hidden>📄</span> {file.name}
              <span className="ml-2 text-xs text-gray-400">{formatSize(file.size)}</span>
            </span>
            <button
              type="button"
              onClick={clearFile}
              className="ml-3 shrink-0 text-xs text-gray-500 hover:text-red-600"
            >
              remover
            </button>
          </div>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Rito:</span>
            <div className="flex overflow-hidden rounded-md border border-gray-300">
              {RITOS.map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => setRito(r.value)}
                  className={`px-3 py-1.5 text-sm font-medium transition-colors ${
                    rito === r.value
                      ? "bg-gray-900 text-white"
                      : "bg-white text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            data-testid="analyze-btn"
            disabled={!file || loading}
            className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            {loading ? "Analisando…" : "Analisar →"}
          </button>
        </div>
      </form>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div data-testid="analysis-result" className="space-y-4">
          <ForensicsBanner report={result.forensics} />

          {result.summary && result.admissibility ? (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                <SummaryPanel summary={result.summary} />
                <AdmissibilityPanel report={result.admissibility} />
              </div>

              {result.tpu_suggestions && result.tpu_suggestions.length > 0 && (
                <TpuPanel suggestions={result.tpu_suggestions} />
              )}

              <ReviewPanel analysisId={response!.id} />
            </>
          ) : (
            <p className="text-sm text-gray-500">
              Análise cognitiva não executada — o documento foi bloqueado pelo firewall.
            </p>
          )}

          <p className="text-xs text-gray-400">
            id: {response?.id} · rito: {result.rito?.toLowerCase() ?? "cível"}
          </p>
        </div>
      )}
    </main>
  );
}
