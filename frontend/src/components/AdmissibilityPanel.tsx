import type { AdmissibilityReport, Semaforo } from "@/lib/types";

const SEMAFORO: Record<Semaforo, { dot: string; label: string }> = {
  VERDE: { dot: "bg-green-500", label: "Apto a prosseguir" },
  AMARELO: { dot: "bg-amber-500", label: "Vícios menores" },
  VERMELHO: { dot: "bg-red-500", label: "Requer emenda (art. 321)" },
};

export function AdmissibilityPanel({ report }: { report: AdmissibilityReport }) {
  const s = SEMAFORO[report.semaforo];
  return (
    <section className="space-y-3 rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-2">
        <span className={`inline-block h-3 w-3 rounded-full ${s.dot}`} aria-hidden />
        <h2 className="font-semibold text-gray-800">Admissibilidade — {s.label}</h2>
      </div>

      <ul className="space-y-1 text-sm">
        {report.itens.map((item) => (
          <li key={item.requisito} className="flex items-start gap-2">
            <span className={item.presente ? "text-green-600" : "text-red-600"}>
              {item.presente ? "✓" : "✗"}
            </span>
            <span>
              <span className="font-medium capitalize">{item.requisito}</span>
              <span className="ml-1 text-xs text-gray-400">[{item.metodo.toLowerCase()}]</span>
              {item.detalhe && <span className="text-gray-600"> — {item.detalhe}</span>}
              {item.evidencia && (
                <span className="ml-1 text-xs text-gray-500">({item.evidencia})</span>
              )}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
