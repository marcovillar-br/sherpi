"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { login, ApiError } from "@/lib/api";

const STORAGE_KEY = "sherpi_saved_credentials";

export default function LoginPage() {
  const router = useRouter();
  // Campos não-controlados (refs): o prefill do localStorage é feito via DOM no
  // effect — evita setState pós-mount (SSR-safe, sem hydration mismatch) e mantém
  // os valores fora do ciclo de render (só são lidos no submit).
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const rememberRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const { email, password } = JSON.parse(saved) as { email: string; password: string };
        if (emailRef.current) emailRef.current.value = email;
        if (passwordRef.current) passwordRef.current.value = password;
        if (rememberRef.current) rememberRef.current.checked = true;
      }
    } catch {
      // localStorage indisponível ou dados corrompidos — ignorar silenciosamente.
    }
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const email = emailRef.current?.value ?? "";
    const password = passwordRef.current?.value ?? "";
    const remember = rememberRef.current?.checked ?? false;
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      if (remember) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ email, password }));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Credenciais inválidas ou conta bloqueada. Tente novamente.");
      } else {
        setError("Erro ao conectar com o servidor. Verifique se a API está disponível.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm space-y-6 rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-gray-900">SHERPI</h1>
          <p className="mt-1 text-sm text-gray-500">
            Triagem assistida de petições iniciais
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              E-mail
            </label>
            <input
              id="email"
              ref={emailRef}
              type="email"
              autoComplete="email"
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Senha
            </label>
            <input
              id="password"
              ref={passwordRef}
              type="password"
              autoComplete="current-password"
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              id="remember"
              ref={rememberRef}
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 accent-gray-900"
            />
            <label htmlFor="remember" className="text-sm text-gray-600">
              Lembrar acesso
            </label>
          </div>

          {error && (
            <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            {loading ? "Entrando…" : "Entrar"}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400">
          Acesso restrito a servidores autorizados
        </p>
      </div>
    </main>
  );
}
