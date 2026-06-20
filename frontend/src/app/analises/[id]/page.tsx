"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AnalysisResultView } from "@/components/AnalysisResultView";
import { NavHeader } from "@/components/NavHeader";
import { ApiError, getAnalysis } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";

export default function AnalysisDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getAnalysis(params.id)
      .then((d) => {
        if (active) setData(d);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setError(
          err instanceof ApiError && err.status === 404
            ? "Análise não encontrada."
            : "Erro ao carregar a análise.",
        );
      });
    return () => {
      active = false;
    };
  }, [params.id, router]);

  return (
    <main className="mx-auto w-[80%] max-w-6xl space-y-6 p-6">
      <NavHeader />

      <Link href="/analises" className="text-sm text-gray-500 hover:text-gray-900">
        ← Voltar ao histórico
      </Link>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {data === null && !error && <p className="text-sm text-gray-500">Carregando…</p>}

      {data && <AnalysisResultView id={data.id} result={data.result} />}
    </main>
  );
}
