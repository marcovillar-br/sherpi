import type { AdmissibilityReport, AdmissibilityStatus } from "@/lib/types";

const STATUS: Record<AdmissibilityStatus, { dot: string; label: string }> = {
  GREEN: { dot: "bg-green-500", label: "Apto a prosseguir" },
  YELLOW: { dot: "bg-amber-500", label: "Vícios menores" },
  RED: { dot: "bg-red-500", label: "Requer emenda (art. 321)" },
};

// Rótulos pt-BR dos requisitos (a API usa os valores en-US do enum Requirement).
const REQUIREMENT_LABELS: Record<string, string> = {
  court: "Endereçamento",
  parties: "Partes",
  qualification: "Qualificação",
  facts: "Fatos",
  legal_basis: "Fundamentação",
  claims: "Pedidos",
  claim_value: "Valor da causa",
  evidence: "Provas",
  hearing: "Audiência",
  documents: "Documentos",
  liquid_claim: "Pedido líquido",
};

export function AdmissibilityPanel({ report }: { report: AdmissibilityReport }) {
  const s = STATUS[report.status];
  return (
    <section
      data-testid="admissibility-panel"
      data-status={report.status}
      className="space-y-3 rounded-lg border border-gray-200 p-4"
    >
      <div className="flex items-center gap-2">
        <span className={`inline-block h-3 w-3 rounded-full ${s.dot}`} aria-hidden />
        <h2 className="font-semibold text-gray-800">Admissibilidade — {s.label}</h2>
      </div>

      <ul className="space-y-1 text-sm">
        {report.items.map((item) => (
          <li key={item.requirement} className="flex items-start gap-2">
            <span className={item.present ? "text-green-600" : "text-red-600"}>
              {item.present ? "✓" : "✗"}
            </span>
            <span className="flex flex-col">
              <span>
                <span className="font-medium">
                  {REQUIREMENT_LABELS[item.requirement] ?? item.requirement}
                </span>
                <span className="ml-1 text-xs text-gray-400">[{item.method.toLowerCase()}]</span>
                {item.detail && <span className="text-gray-600"> — {item.detail}</span>}
                {item.evidence && (
                  <span className="ml-1 text-xs text-gray-500">({item.evidence})</span>
                )}
              </span>
              {item.caveat && (
                <span
                  data-testid={`admissibility-caveat-${item.requirement}`}
                  className="mt-0.5 text-xs text-amber-700"
                >
                  ⚠ {item.caveat}
                </span>
              )}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
