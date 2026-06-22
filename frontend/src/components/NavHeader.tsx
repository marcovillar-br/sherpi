"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { logout } from "@/lib/api";

const LINKS = [
  { href: "/", label: "Nova análise" },
  { href: "/analises", label: "Histórico" },
];

export function NavHeader() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex items-center justify-between border-b border-gray-200 pb-3">
      <div className="flex items-baseline gap-6">
        <h1 className="text-xl font-bold text-gray-900">SHERPI</h1>
        <nav className="flex gap-4 text-sm">
          {LINKS.map((l) => {
            const active = l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={
                  active
                    ? "font-medium text-gray-900"
                    : "text-gray-500 hover:text-gray-900"
                }
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <button
        type="button"
        onClick={handleLogout}
        className="text-sm text-gray-500 hover:text-gray-900"
      >
        Sair
      </button>
    </header>
  );
}
