"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { StartupCard, type Startup } from "@/components/StartupCard";
import { StartupFilters, type Filters } from "@/components/StartupFilters";
import { RegionPickerDialog } from "@/components/RegionPickerDialog";

type ListResp = { items: Startup[]; total: number };

export default function FeedPage() {
  const [filters, setFilters] = useState<Filters>({ q: "", source: "" });
  const [picked, setPicked] = useState<Startup | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["startups", filters],
    queryFn: () => {
      const params = new URLSearchParams({ limit: "48" });
      if (filters.q) params.set("q", filters.q);
      if (filters.source) params.set("source", filters.source);
      return api<ListResp>(`/api/startups?${params.toString()}`);
    },
  });

  return (
    <div className="container mx-auto px-6 py-10">
      <div className="mb-8 flex items-end justify-between gap-6 flex-wrap">
        <div>
          <h1 className="font-display text-4xl font-black">
            Лента <span className="text-gradient">стартапов</span>
          </h1>
          <p className="mt-2 text-ink-muted">
            {data ? `${data.total} проектов` : "Загружаем свежие проекты из Product Hunt и YC…"}
          </p>
        </div>
        <div className="w-full md:w-auto md:min-w-[480px]">
          <StartupFilters filters={filters} onChange={setFilters} />
        </div>
      </div>

      {error && (
        <div className="glass-card p-6 text-rose-brand">
          Ошибка загрузки: {(error as Error).message}
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="glass-card h-56 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {(data?.items || []).map((s) => (
            <StartupCard key={s.id} startup={s} onPick={setPicked} />
          ))}
          {data && data.items.length === 0 && (
            <div className="col-span-full glass-card p-10 text-center text-ink-muted">
              Ничего не найдено. Парсер ещё не отработал — проверьте через несколько минут или
              запустите вручную через ARQ.
            </div>
          )}
        </div>
      )}

      <RegionPickerDialog startup={picked} onClose={() => setPicked(null)} />
    </div>
  );
}
