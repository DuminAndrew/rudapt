"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { tokens } from "@/lib/api";
import { LayoutGrid, FileText, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/feed", label: "Лента стартапов", icon: LayoutGrid },
  { href: "/reports", label: "Мои планы", icon: FileText },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!tokens.access) router.replace("/login");
    else setReady(true);
  }, [router]);

  if (!ready) return null;

  function logout() {
    tokens.clear();
    router.replace("/login");
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/5 backdrop-blur-xl bg-bg-deeper/60 sticky top-0 z-30">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <Logo size={32} />
          <nav className="hidden md:flex items-center gap-1">
            {NAV.map((n) => {
              const active = pathname === n.href || pathname?.startsWith(n.href + "/");
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={cn(
                    "flex items-center gap-2 rounded-xl px-4 py-2 text-sm transition",
                    active
                      ? "bg-white/10 text-ink"
                      : "text-ink-muted hover:bg-white/5 hover:text-ink"
                  )}
                >
                  <n.icon className="h-4 w-4" />
                  {n.label}
                </Link>
              );
            })}
          </nav>
          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4" /> Выйти
          </Button>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
