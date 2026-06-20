import { ANOMALY_TYPE_LABEL, SEVERITY_LABEL } from "@/lib/labels";
import type { ForensicsReport, RiskVerdict } from "@/lib/types";

const STYLES: Record<RiskVerdict, { box: string; label: string }> = {
  BLOCK: { box: "border-red-300 bg-red-50 text-red-800", label: "Risco grave — bloqueado" },
  WARN: { box: "border-amber-300 bg-amber-50 text-amber-800", label: "Atenção — anomalias" },
  PASS: { box: "border-green-300 bg-green-50 text-green-800", label: "Documento íntegro" },
};

export function ForensicsBanner({ report }: { report: ForensicsReport }) {
  const style = STYLES[report.verdict];
  return (
    <section data-testid={`forensics-${report.verdict}`} className={`rounded-lg border p-4 ${style.box}`}>
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">Laudo de integridade — {style.label}</h2>
        <span className="text-sm">risco {report.risk_score.toFixed(2)}</span>
      </div>
      {report.image_only_pages.length > 0 && (
        <p className="mt-3 rounded border border-amber-300 bg-amber-50 p-2 text-sm text-amber-800">
          ⚠ Documento sem camada de texto em {report.image_only_pages.length} página
          {report.image_only_pages.length > 1 ? "s" : ""} (provável digitalização/imagem). A
          extração não é confiável nesse conteúdo — requer OCR.
        </p>
      )}
      {report.anomalies.length > 0 && (
        <ul className="mt-3 space-y-2 text-sm">
          {report.anomalies.map((a, i) => (
            <li key={i} className="rounded border border-current/20 bg-white/50 p-2">
              <div className="font-medium">
                {ANOMALY_TYPE_LABEL[a.type] ?? a.type} · {SEVERITY_LABEL[a.severity] ?? a.severity}
                {a.page !== null && <span> · pág. {a.page + 1}</span>}
              </div>
              <div>{a.detail}</div>
              {a.evidence && <code className="mt-1 block text-xs opacity-80">{a.evidence}</code>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
