"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { NavHeader } from "@/components/NavHeader";
import { ApiError, listAnalyses } from "@/lib/api";
import { ADMISSIBILITY_LABEL, REVIEW_DECISION_LABEL, RITO_LABEL, VERDICT_LABEL } from "@/lib/labels";
import type {
  AdmissibilityStatus,
  AnalysisSummary,
  ReviewDecision,
  RiskVerdict,
  Rito,
} from "@/lib/types";

const VERDICT_DOT: Record<RiskVerdict, string> = {
  PASS: "bg-green-500",
  WARN: "bg-amber-500",
  BLOCK: "bg-red-500",
};

const ADM_DOT: Record<AdmissibilityStatus, string> = {
  GREEN: "bg-green-500",
  YELLOW: "bg-amber-500",
  RED: "bg-red-500",
};

const DECISION_STYLE: Record<ReviewDecision, string> = {
  ACCEPT: "text-green-700",
  AMEND: "text-amber-700",
  REJECT: "text-red-700",
};

type VerdictFilter = "ALL" | RiskVerdict;
type RitoFilter = "ALL" | Rito;
type AdmFilter = "ALL" | AdmissibilityStatus | "BLOCKED";

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const SELECT_CLASS =
  "rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm shadow-sm focus:border-gray-500 focus:outline-none";

export default function HistoryPage() {
  const router = useRouter();
  const [items, setItems] = useState<AnalysisSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [rito, setRito] = useState<RitoFilter>("ALL");
  const [adm, setAdm] = useState<AdmFilter>("ALL");
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
    if (rito !== "ALL" && it.rito !== rito) return false;
    if (adm === "BLOCKED" && it.admissibility_status !== null) return false;
    if (adm !== "ALL" && adm !== "BLOCKED" && it.admissibility_status !== adm) return false;
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
          <select
            value={rito}
            onChange={(e) => setRito(e.target.value as RitoFilter)}
            className={SELECT_CLASS}
            aria-label="Filtrar por rito"
          >
            <option value="ALL">Rito: todos</option>
            <option value="CIVEL">{RITO_LABEL.CIVEL}</option>
            <option value="TRABALHISTA">{RITO_LABEL.TRABALHISTA}</option>
          </select>
          <select
            value={adm}
            onChange={(e) => setAdm(e.target.value as AdmFilter)}
            className={SELECT_CLASS}
            aria-label="Filtrar por admissibilidade"
          >
            <option value="ALL">Admissibilidade: todas</option>
            <option value="GREEN">{ADMISSIBILITY_LABEL.GREEN}</option>
            <option value="YELLOW">{ADMISSIBILITY_LABEL.YELLOW}</option>
            <option value="RED">{ADMISSIBILITY_LABEL.RED}</option>
            <option value="BLOCKED">Bloqueada (sem análise)</option>
          </select>
          <select
            value={verdict}
            onChange={(e) => setVerdict(e.target.value as VerdictFilter)}
            className={SELECT_CLASS}
            aria-label="Filtrar por veredito"
          >
            <option value="ALL">Veredito: todos</option>
            <option value="PASS">{VERDICT_LABEL.PASS}</option>
            <option value="WARN">{VERDICT_LABEL.WARN}</option>
            <option value="BLOCK">{VERDICT_LABEL.BLOCK}</option>
          </select>
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
        <p className="text-sm text-gray-500">Nenhuma análise corresponde aos filtros.</p>
      )}

      {filtered.length > 0 && (
        <ul className="divide-y divide-gray-100 rounded-md border border-gray-200">
          {filtered.map((item) => {
            const status = item.admissibility_status;
            return (
              <li key={item.id}>
                <Link
                  href={`/analises/${item.id}`}
                  className="block px-4 py-2 transition-colors hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full ${VERDICT_DOT[item.verdict]}`}
                      title={`Firewall: ${VERDICT_LABEL[item.verdict]}`}
                      aria-hidden
                    />
                    <span className="min-w-0 truncate text-sm font-medium text-gray-800">
                      {item.filename ?? "(sem nome)"}
                    </span>
                    <span className="shrink-0 font-mono text-xs text-gray-400">
                      #{item.id.slice(0, 8)}
                    </span>
                    <span className="ml-auto flex shrink-0 items-center gap-2 text-xs text-gray-500">
                      <span>{RITO_LABEL[item.rito]}</span>
                      {status ? (
                        <span className="flex items-center gap-1">
                          <span className={`inline-block h-2 w-2 rounded-full ${ADM_DOT[status]}`} aria-hidden />
                          {ADMISSIBILITY_LABEL[status]}
                        </span>
                      ) : (
                        <span className="text-gray-400">bloqueada</span>
                      )}
                      {item.has_injunction && <span className="text-amber-700">⚡</span>}
                      <span className="tabular-nums text-gray-400">{formatDate(item.created_at)}</span>
                    </span>
                  </div>

                  {item.review_decision && (
                    <div className="mt-0.5 flex items-center gap-1.5 pl-[22px] text-xs text-gray-500">
                      <span className={`font-medium ${DECISION_STYLE[item.review_decision]}`}>
                        ✓ {REVIEW_DECISION_LABEL[item.review_decision]}
                      </span>
                      {item.review_comment && (
                        <span className="min-w-0 truncate italic">“{item.review_comment}”</span>
                      )}
                    </div>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
