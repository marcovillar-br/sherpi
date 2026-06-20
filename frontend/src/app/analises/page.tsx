"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { NavHeader } from "@/components/NavHeader";
import { ApiError, listAnalyses } from "@/lib/api";
import type { AdmissibilityStatus, AnalysisSummary, RiskVerdict, Rito } from "@/lib/types";

const VERDICT_DOT: Record<RiskVerdict, string> = {
  PASS: "bg-green-500",
  WARN: "bg-amber-500",
  BLOCK: "bg-red-500",
};

const ADM: Record<AdmissibilityStatus, { dot: string; label: string }> = {
  GREEN: { dot: "bg-green-500", label: "Verde" },
  YELLOW: { dot: "bg-amber-500", label: "Amarelo" },
  RED: { dot: "bg-red-500", label: "Vermelho" },
};

const RITO_LABEL: Record<Rito, string> = { CIVEL: "Cível", TRABALHISTA: "Trabalhista" };

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoryPage() {
  const router = useRouter();
  const [items, setItems] = useState<AnalysisSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    listAnalyses()
      .then((data) => {
        if (active) setItems(data);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setError("Erro ao carregar o histórico.");
      });
    return () => {
      active = false;
    };
  }, [router]);

  return (
    <main className="mx-auto w-[80%] max-w-6xl space-y-6 p-6">
      <NavHeader />

      <h2 className="text-lg font-semibold text-gray-800">Histórico de análises</h2>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {items === null && !error && <p className="text-sm text-gray-500">Carregando…</p>}

      {items !== null && items.length === 0 && (
        <p className="text-sm text-gray-500">
          Nenhuma análise ainda — comece em{" "}
          <Link href="/" className="font-medium text-gray-900 hover:underline">
            Nova análise
          </Link>
          .
        </p>
      )}

      {items !== null && items.length > 0 && (
        <ul className="space-y-2">
          {items.map((item) => {
            const adm = item.admissibility_status ? ADM[item.admissibility_status] : null;
            return (
              <li key={item.id}>
                <Link
                  href={`/analises/${item.id}`}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-gray-200 px-4 py-3 transition-colors hover:bg-gray-50"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <span
                      className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full ${VERDICT_DOT[item.verdict]}`}
                      title={`Firewall: ${item.verdict}`}
                      aria-hidden
                    />
                    <span className="truncate text-sm font-medium text-gray-800">
                      {item.filename ?? "(sem nome)"}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>{RITO_LABEL[item.rito]}</span>
                    {adm ? (
                      <span className="flex items-center gap-1">
                        <span className={`inline-block h-2 w-2 rounded-full ${adm.dot}`} aria-hidden />
                        {adm.label}
                      </span>
                    ) : (
                      <span className="text-gray-400">— (bloqueada)</span>
                    )}
                    {item.has_injunction && <span className="text-amber-700">⚡ liminar</span>}
                    <span className="tabular-nums">{formatDate(item.created_at)}</span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
