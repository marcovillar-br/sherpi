import type { TpuSuggestion } from "@/lib/types";

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-200">
        <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-500">{pct}%</span>
    </div>
  );
}

export function TpuPanel({ suggestions }: { suggestions: TpuSuggestion[] }) {
  return (
    <section className="space-y-3 rounded-lg border border-blue-200 bg-blue-50/40 p-4">
      <h2 className="font-semibold text-gray-800">Sugestão TPU (top‑3)</h2>
      <ol className="space-y-3">
        {suggestions.map((s, i) => (
          <li key={`${s.tpu_code}-${i}`} className="rounded-md border border-gray-200 bg-white p-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-xs font-semibold text-gray-400">#{i + 1} · cód. {s.tpu_code}</span>
                <p className="mt-0.5 text-sm font-medium text-gray-800">{s.description}</p>
                {s.anchor_excerpt && (
                  <p className="mt-1 text-xs text-gray-500 italic">&ldquo;{s.anchor_excerpt}&rdquo;</p>
                )}
              </div>
              <ConfidenceBar value={s.confidence} />
            </div>
          </li>
        ))}
      </ol>
      <p className="text-xs text-gray-400">
        Classificação por similaridade semântica — sujeita a revisão humana.
      </p>
    </section>
  );
}
