"use client";

import { useEffect, useState } from "react";
import { getReviews, submitReview, ApiError } from "@/lib/api";
import type { AuditEvent, ReviewDecision } from "@/lib/types";

const DECISIONS: { value: ReviewDecision; label: string; style: string }[] = [
  {
    value: "ACCEPT",
    label: "Aceitar",
    style: "border-green-300 bg-green-50 text-green-800 hover:bg-green-100",
  },
  {
    value: "AMEND",
    label: "Corrigir",
    style: "border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100",
  },
  {
    value: "REJECT",
    label: "Rejeitar",
    style: "border-red-300 bg-red-50 text-red-800 hover:bg-red-100",
  },
];

const DECISION_LABELS: Record<ReviewDecision, string> = {
  ACCEPT: "Aceito",
  AMEND: "Corrigir",
  REJECT: "Rejeitado",
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ReviewPanel({ analysisId }: { analysisId: string }) {
  const [reviews, setReviews] = useState<AuditEvent[]>([]);
  const [selected, setSelected] = useState<ReviewDecision | null>(null);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReviews(analysisId)
      .then(setReviews)
      .catch(() => {});
  }, [analysisId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setSubmitting(true);
    setError(null);
    try {
      const event = await submitReview(analysisId, selected, comment || undefined);
      setReviews((prev) => [...prev, event]);
      setSelected(null);
      setComment("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro ao registrar revisão.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-lg border border-gray-200 p-4">
      <h2 className="font-semibold text-gray-800">Revisão humana</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          {DECISIONS.map((d) => (
            <button
              key={d.value}
              type="button"
              onClick={() => setSelected(d.value)}
              className={`rounded-md border px-3 py-1.5 text-sm font-medium transition-colors ${d.style} ${
                selected === d.value ? "ring-2 ring-offset-1 ring-gray-400" : ""
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>

        {selected && (
          <textarea
            placeholder="Comentário opcional…"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={2}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none"
          />
        )}

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        <button
          type="submit"
          disabled={!selected || submitting}
          className="rounded-md bg-gray-900 px-4 py-1.5 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting ? "Registrando…" : "Registrar revisão"}
        </button>
      </form>

      {reviews.length > 0 && (
        <div className="space-y-2 border-t border-gray-100 pt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Trilha de auditoria
          </p>
          <ul className="space-y-1.5">
            {reviews.map((r) => (
              <li key={r.id} className="rounded-md bg-gray-50 px-3 py-2 text-sm">
                <span className="font-medium text-gray-700">
                  {DECISION_LABELS[r.decision]}
                </span>
                {r.comment && (
                  <span className="text-gray-600"> — {r.comment}</span>
                )}
                <span className="ml-2 text-xs text-gray-400">
                  {formatDate(r.created_at)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
