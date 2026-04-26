"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RU_REGIONS } from "@/lib/regions";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Startup } from "@/components/StartupCard";

const MAX_REGIONS = 5;

export function RegionPickerDialog({
  startup,
  onClose,
}: {
  startup: Startup | null;
  onClose: () => void;
}) {
  const router = useRouter();
  const [selected, setSelected] = useState<string[]>([]);
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  function toggle(r: string) {
    setSelected((s) =>
      s.includes(r) ? s.filter((x) => x !== r) : s.length >= MAX_REGIONS ? s : [...s, r]
    );
  }

  function addCustom() {
    const v = custom.trim();
    if (!v) return;
    if (selected.length >= MAX_REGIONS) return;
    if (!selected.includes(v)) setSelected((s) => [...s, v]);
    setCustom("");
  }

  async function go() {
    if (!startup || !selected.length) return;
    setLoading(true);
    setErr(null);
    try {
      const r = await api<{ id: string }>("/api/generate-plan", {
        method: "POST",
        json: { startup_id: startup.id, regions: selected },
      });
      router.push(`/reports/${r.id}`);
    } catch (e: any) {
      setErr(e.message || "Ошибка");
      setLoading(false);
    }
  }

  return (
    <Dialog open={!!startup} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle className="font-display text-2xl font-bold">
            Регионы РФ
          </DialogTitle>
          <DialogDescription className="text-ink-muted text-sm">
            Локализуем <b className="text-ink">{startup?.name}</b>. Выбери до{" "}
            <b className="text-ink">{MAX_REGIONS}</b> регионов — нейросеть сравнит их
            side-by-side и подскажет, где запускать первым.
          </DialogDescription>
        </DialogHeader>

        {selected.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {selected.map((r) => (
              <span
                key={r}
                className="inline-flex items-center gap-1.5 rounded-full bg-violet-brand/20 border border-violet-brand/40 text-ink px-3 py-1 text-xs"
              >
                {r}
                <button onClick={() => toggle(r)} className="hover:text-rose-brand">
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-64 overflow-y-auto pr-1">
          {RU_REGIONS.map((r) => {
            const on = selected.includes(r);
            const disabled = !on && selected.length >= MAX_REGIONS;
            return (
              <button
                key={r}
                disabled={disabled}
                onClick={() => toggle(r)}
                className={cn(
                  "text-left text-xs rounded-lg px-3 py-2 border transition",
                  on
                    ? "border-violet-brand/60 bg-violet-brand/15 text-ink"
                    : "border-white/10 bg-white/5 text-ink-muted hover:text-ink",
                  disabled && "opacity-30 cursor-not-allowed"
                )}
              >
                {r}
              </button>
            );
          })}
        </div>

        <div className="mt-4 flex gap-2">
          <Input
            placeholder="Добавить свой регион (например: Калуга)"
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustom())}
          />
          <Button variant="ghost" onClick={addCustom} disabled={!custom.trim()}>
            Добавить
          </Button>
        </div>

        {err && <div className="mt-3 text-sm text-rose-brand">{err}</div>}

        <div className="mt-5 flex justify-between items-center">
          <span className="text-xs text-ink-dim">
            {selected.length}/{MAX_REGIONS} регионов
          </span>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Отмена</Button>
            <Button onClick={go} disabled={!selected.length || loading}>
              <Sparkles className="h-4 w-4" />
              {loading
                ? "Запускаю…"
                : selected.length > 1
                ? `Сравнить (${selected.length})`
                : "Сгенерировать"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
