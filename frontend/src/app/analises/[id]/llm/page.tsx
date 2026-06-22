"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { NavHeader } from "@/components/NavHeader";
import { ApiError, getLlmCalls } from "@/lib/api";
import type { LLMCall } from "@/lib/types";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("pt-BR");
}

// O prompt é um JSON de mensagens [{role, content}]; renderiza legível, com
// fallback para o texto cru se não for parseável.
function PromptView({ prompt }: { prompt: string }) {
  let messages: { role: string; content: string }[] | null = null;
  try {
    messages = JSON.parse(prompt) as { role: string; content: string }[];
  } catch {
    messages = null;
  }
  if (!messages) {
    return <pre className="whitespace-pre-wrap break-words text-xs text-gray-700">{prompt}</pre>;
  }
  return (
    <div className="space-y-2">
      {messages.map((m, i) => (
        <div key={i}>
          <div className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            {m.role}
          </div>
          <pre className="whitespace-pre-wrap break-words text-xs text-gray-700">{m.content}</pre>
        </div>
      ))}
    </div>
  );
}

// A resposta é o JSON estruturado; mostra formatado (indentado).
function pretty(json: string): string {
  try {
    return JSON.stringify(JSON.parse(json), null, 2);
  } catch {
    return json;
  }
}

export default function LlmAuditPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [calls, setCalls] = useState<LLMCall[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getLlmCalls(params.id)
      .then((d) => {
        if (active) setCalls(d);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setError("Erro ao carregar a auditoria do LLM.");
      });
    return () => {
      active = false;
    };
  }, [params.id, router]);

  return (
    <main className="mx-auto w-[80%] max-w-6xl space-y-6 p-6">
      <NavHeader />

      <Link href={`/analises/${params.id}`} className="text-sm text-gray-500 hover:text-gray-900">
        ← Voltar à análise
      </Link>

      <h2 className="text-lg font-semibold text-gray-800">Auditoria do LLM — prompt e resposta</h2>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {calls === null && !error && <p className="text-sm text-gray-500">Carregando…</p>}

      {calls !== null && calls.length === 0 && (
        <p className="text-sm text-gray-500">
          Nenhuma chamada ao LLM registrada para esta análise (anterior à auditoria, ou bloqueada
          pelo firewall antes da extração).
        </p>
      )}

      {calls?.map((c) => (
        <section key={c.id} className="space-y-3 rounded-lg border border-gray-200 p-4">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
            <span className="font-semibold text-gray-700">{c.call_type}</span>
            {c.model && <span>modelo: {c.model}</span>}
            <span>prompt: {c.prompt_chars} chars</span>
            <span>resposta: {c.response_chars} chars</span>
            <span>{c.duration_ms} ms</span>
            <span>{formatDate(c.created_at)}</span>
          </div>

          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
              Entrada (prompt)
            </div>
            <div className="max-h-96 overflow-auto rounded-md bg-gray-50 p-3">
              <PromptView prompt={c.prompt} />
            </div>
          </div>

          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
              Saída (resposta)
            </div>
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words rounded-md bg-gray-50 p-3 text-xs text-gray-700">
              {pretty(c.response)}
            </pre>
          </div>
        </section>
      ))}
    </main>
  );
}
