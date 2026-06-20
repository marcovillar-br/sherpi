import { AdmissibilityPanel } from "@/components/AdmissibilityPanel";
import { ForensicsBanner } from "@/components/ForensicsBanner";
import { ReviewPanel } from "@/components/ReviewPanel";
import { SummaryPanel } from "@/components/SummaryPanel";
import { TpuPanel } from "@/components/TpuPanel";
import type { AnalysisResult } from "@/lib/types";

/** Visão consolidada de uma análise — usada na home (resultado imediato) e no
 *  detalhe do histórico. `testId` é definido só na home (o e2e espera por ele). */
export function AnalysisResultView({
  id,
  result,
  testId,
}: {
  id: string;
  result: AnalysisResult;
  testId?: string;
}) {
  return (
    <div data-testid={testId} className="animate-result-in space-y-4">
      <ForensicsBanner report={result.forensics} />

      {result.summary && result.admissibility ? (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <SummaryPanel summary={result.summary} />
            <AdmissibilityPanel report={result.admissibility} />
          </div>

          {result.tpu_suggestions && result.tpu_suggestions.length > 0 && (
            <TpuPanel suggestions={result.tpu_suggestions} />
          )}

          <ReviewPanel analysisId={id} />
        </>
      ) : (
        <p className="text-sm text-gray-500">
          Análise cognitiva não executada — o documento foi bloqueado pelo firewall.
        </p>
      )}

      <p className="text-xs text-gray-400">
        id: {id} · rito: {result.rito?.toLowerCase() ?? "cível"}
      </p>
    </div>
  );
}
