import type { PetitionSummary } from "@/lib/types";

export function SummaryPanel({ summary }: { summary: PetitionSummary }) {
  return (
    <section className="space-y-4 rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Resumo estruturado</h2>
        {summary.tem_liminar && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
            ⚠ Pedido de liminar
          </span>
        )}
      </div>

      <Field label="Partes">
        <ul className="space-y-1">
          {summary.partes.map((p, i) => (
            <li key={i}>
              <span className="font-medium">{p.nome}</span>{" "}
              <span className="text-xs text-gray-500">
                ({p.polo.toLowerCase()}
                {p.documento ? ` · ${p.documento}` : ""})
              </span>
            </li>
          ))}
        </ul>
      </Field>

      <Field label="Fato gerador">{summary.fato_gerador}</Field>
      <Field label="Fundamentação">{summary.fundamentacao}</Field>

      <Field label="Pedidos">
        <ul className="list-disc pl-5">
          {summary.pedidos.map((p, i) => (
            <li key={i} className={p.tipo === "LIMINAR" ? "font-semibold text-red-700" : ""}>
              {p.descricao}
              {p.tipo !== "PRINCIPAL" && (
                <span className="ml-1 text-xs text-gray-500">[{p.tipo.toLowerCase()}]</span>
              )}
            </li>
          ))}
        </ul>
      </Field>

      <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
        <Field label="Valor da causa">{summary.valor_causa ?? "—"}</Field>
        <Field label="Documentos mencionados">
          {summary.documentos_mencionados.join(", ") || "—"}
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
