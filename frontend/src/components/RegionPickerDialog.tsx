"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
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

export function RegionPickerDialog({
  startup,
  onClose,
}: {
  startup: Startup | null;
  onClose: () => void;
}) {
  const router = useRouter();
  const [region, setRegion] = useState<string>("");
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const target = custom.trim() || region;

  async function go() {
    if (!startup || !target) return;
    setLoading(true);
    setErr(null);
    try {
      const r = await api<{ id: string }>("/api/generate-plan", {
        method: "POST",
        json: { startup_id: startup.id, region: target },
      });
      router.push(`/reports/${r.id}`);
    } catch (e: any) {
      setErr(e.message || "Ошибка");
      setLoading(false);
    }
  }

  return (
    <Dialog open={!!startup} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="font-display text-2xl font-bold">
            Целевой регион РФ
          </DialogTitle>
          <DialogDescription className="text-ink-muted text-sm">
            Локализуем <b className="text-ink">{startup?.name}</b>. Выберите регион — нейросеть
            учтёт его специфику, конкурентов и каналы.
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-72 overflow-y-auto pr-1">
          {RU_REGIONS.map((r) => (
            <button
              key={r}
              onClick={() => { setRegion(r); setCustom(""); }}
              className={cn(
                "text-left text-xs rounded-lg px-3 py-2 border transition",
                region === r && !custom
                  ? "border-violet-brand/60 bg-violet-brand/15 text-ink"
                  : "border-white/10 bg-white/5 text-ink-muted hover:text-ink"
              )}
            >
              {r}
            </button>
          ))}
        </div>

        <div className="mt-4">
          <Input
            placeholder="Или введите свой вариант (например: Калуга)"
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
          />
        </div>

        {err && <div className="mt-3 text-sm text-rose-brand">{err}</div>}

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Отмена</Button>
          <Button onClick={go} disabled={!target || loading}>
            <Sparkles className="h-4 w-4" />
            {loading ? "Запускаю…" : "Сгенерировать"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
