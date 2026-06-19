import type { AdmissibilityReport, AdmissibilityStatus } from "@/lib/types";

const STATUS: Record<AdmissibilityStatus, { dot: string; label: string }> = {
  GREEN: { dot: "bg-green-500", label: "Apto a prosseguir" },
  YELLOW: { dot: "bg-amber-500", label: "Vícios menores" },
  RED: { dot: "bg-red-500", label: "Requer emenda (art. 321)" },
};

export function AdmissibilityPanel({ report }: { report: AdmissibilityReport }) {
  const s = STATUS[report.status];
  return (
    <section className="space-y-3 rounded-lg border border-gray-200 p-4">
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
            <span>
              <span className="font-medium capitalize">{item.requirement}</span>
              <span className="ml-1 text-xs text-gray-400">[{item.method.toLowerCase()}]</span>
              {item.detail && <span className="text-gray-600"> — {item.detail}</span>}
              {item.evidence && (
                <span className="ml-1 text-xs text-gray-500">({item.evidence})</span>
              )}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
