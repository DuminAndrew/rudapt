"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Clock, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

type Report = {
  id: string;
  startup_id: string;
  region: string;
  regions?: string[] | null;
  status: "pending" | "running" | "done" | "failed";
  created_at: string;
};

const STATUS = {
  pending: { icon: Clock, label: "В очереди", v: "default" as const },
  running: { icon: Loader2, label: "Генерируется", v: "violet" as const },
  done: { icon: CheckCircle2, label: "Готов", v: "cyan" as const },
  failed: { icon: AlertCircle, label: "Ошибка", v: "rose" as const },
};

export default function ReportsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => api<{ items: Report[]; total: number }>("/api/reports"),
    refetchInterval: 5000,
  });

  return (
    <div className="container mx-auto px-6 py-10">
      <h1 className="font-display text-4xl font-black mb-8">
        Мои <span className="text-gradient">бизнес-планы</span>
      </h1>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card h-20 animate-pulse" />
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="glass-card p-10 text-center text-ink-muted">
          Пока пусто. Перейдите в <Link href="/feed" className="text-violet-brand hover:underline">ленту стартапов</Link> и сгенерируйте первый план.
        </div>
      ) : (
        <div className="space-y-3">
          {(data?.items || []).map((r) => {
            const s = STATUS[r.status];
            const Icon = s.icon;
            return (
              <Link
                key={r.id}
                href={`/reports/${r.id}`}
                className="glass-card p-5 flex items-center justify-between hover:bg-white/[0.06] transition"
              >
                <div>
                  <div className="flex items-center gap-3">
                    <Badge variant={s.v}>
                      <Icon className={`h-3 w-3 mr-1 ${r.status === "running" ? "animate-spin" : ""}`} />
                      {s.label}
                    </Badge>
                    <span className="font-display text-lg font-bold">
                      {r.regions && r.regions.length > 1
                        ? `${r.regions.slice(0, 2).join(" · ")}${r.regions.length > 2 ? ` +${r.regions.length - 2}` : ""}`
                        : r.region}
                    </span>
                  </div>
                  <div className="text-xs text-ink-dim mt-1">
                    {new Date(r.created_at).toLocaleString("ru-RU")}
                  </div>
                </div>
                <span className="text-ink-muted">→</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
