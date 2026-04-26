"use client";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export type Filters = { q: string; source: string };

const SOURCES = [
  { id: "", label: "Все" },
  { id: "producthunt", label: "Product Hunt" },
  { id: "yc", label: "Y Combinator" },
  { id: "crunchbase", label: "Crunchbase" },
];

export function StartupFilters({
  filters,
  onChange,
}: {
  filters: Filters;
  onChange: (f: Filters) => void;
}) {
  return (
    <div className="flex flex-col md:flex-row gap-3">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-dim" />
        <Input
          placeholder="Поиск по названию или таглайну…"
          value={filters.q}
          onChange={(e) => onChange({ ...filters, q: e.target.value })}
          className="pl-10"
        />
      </div>
      <div className="flex gap-2">
        {SOURCES.map((s) => (
          <button
            key={s.id}
            onClick={() => onChange({ ...filters, source: s.id })}
            className={cn(
              "rounded-xl px-4 py-2 text-sm transition border",
              filters.source === s.id
                ? "border-violet-brand/50 bg-violet-brand/15 text-ink"
                : "border-white/10 bg-white/5 text-ink-muted hover:text-ink"
            )}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
