import { CLAIM_TYPE_LABEL, POLO_LABEL } from "@/lib/labels";
import type { PetitionSummary } from "@/lib/types";

export function SummaryPanel({ summary }: { summary: PetitionSummary }) {
  return (
    <section className="space-y-4 rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Resumo estruturado</h2>
        {summary.has_injunction && (
          <span
            data-testid="summary-has-injunction"
            className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
          >
            ⚠ Pedido de liminar
          </span>
        )}
      </div>

      <Field label="Partes">
        <ul className="space-y-1">
          {summary.parties.map((p, i) => (
            <li key={i}>
              <span className="font-medium">{p.name}</span>{" "}
              <span className="text-xs text-gray-500">
                ({POLO_LABEL[p.pole] ?? p.pole.toLowerCase()}
                {p.document ? ` · ${p.document}` : ""})
              </span>
            </li>
          ))}
        </ul>
      </Field>

      <Field label="Fatos">{summary.facts || "—"}</Field>
      <Field label="Fundamentação">{summary.legal_basis || "—"}</Field>

      <Field label="Pedidos">
        <ul className="list-disc pl-5">
          {summary.claims.map((p, i) => (
            <li key={i} className={p.type === "INJUNCTION" ? "font-semibold text-red-700" : ""}>
              {p.description}
              {p.type !== "MAIN" && (
                <span className="ml-1 text-xs text-gray-500">
                  [{CLAIM_TYPE_LABEL[p.type] ?? p.type.toLowerCase()}]
                </span>
              )}
            </li>
          ))}
        </ul>
      </Field>

      <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
        <Field label="Valor da causa">{summary.claim_amount ?? "—"}</Field>
        <Field label="Documentos mencionados">
          {summary.cited_documents.join(", ") || "—"}
        </Field>
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</div>
      <div className="text-sm text-gray-700">{children}</div>
    </div>
  );
}
