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

type VerdictFilter = "ALL" | RiskVerdict;
const VERDICT_FILTERS: { value: VerdictFilter; label: string }[] = [
  { value: "ALL", label: "Todos" },
  { value: "PASS", label: "PASS" },
  { value: "WARN", label: "WARN" },
  { value: "BLOCK", label: "BLOCK" },
];

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
  const [query, setQuery] = useState("");
  const [verdict, setVerdict] = useState<VerdictFilter>("ALL");

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

  const q = query.trim().toLowerCase();
  const filtered = (items ?? []).filter((it) => {
    if (verdict !== "ALL" && it.verdict !== verdict) return false;
    if (q && !`${it.filename ?? ""} ${it.id}`.toLowerCase().includes(q)) return false;
    return true;
  });

  return (
    <main className="mx-auto w-[80%] max-w-6xl space-y-6 p-6">
      <NavHeader />

      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-semibold text-gray-800">Histórico de análises</h2>
        {items !== null && (
          <span className="text-xs text-gray-400">
            {filtered.length} de {items.length}
            {items.length === 50 ? " (últimas 50)" : ""}
          </span>
        )}
      </div>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {items !== null && items.length > 0 && (
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por arquivo ou id…"
            className="min-w-0 flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm shadow-sm focus:border-gray-500 focus:outline-none"
          />
          <div className="flex overflow-hidden rounded-md border border-gray-300">
            {VERDICT_FILTERS.map((f) => (
              <button
                key={f.value}
                type="button"
                onClick={() => setVerdict(f.value)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-colors ${
                  verdict === f.value
                    ? "bg-gray-900 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50"
                }`}
              >
                {f.value !== "ALL" && (
                  <span className={`inline-block h-2 w-2 rounded-full ${VERDICT_DOT[f.value]}`} aria-hidden />
                )}
                {f.label}
              </button>
            ))}
          </div>
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

      {items !== null && items.length > 0 && filtered.length === 0 && (
        <p className="text-sm text-gray-500">Nenhuma análise corresponde ao filtro.</p>
      )}

      {filtered.length > 0 && (
        <ul className="space-y-2">
          {filtered.map((item) => {
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
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-gray-800">
                        {item.filename ?? "(sem nome)"}
                      </div>
                      <div className="font-mono text-xs text-gray-400">#{item.id.slice(0, 8)}</div>
                    </div>
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
