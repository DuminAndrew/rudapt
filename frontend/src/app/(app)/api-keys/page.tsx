"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, KeyRound, Plus, Trash2, Check } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

type ApiKey = {
  id: string;
  name: string;
  prefix: string;
  rate_limit_per_min: number;
  created_at: string;
  last_used_at: string | null;
  revoked_at: string | null;
};

type Created = ApiKey & { plaintext: string };

export default function ApiKeysPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [rate, setRate] = useState(60);
  const [created, setCreated] = useState<Created | null>(null);
  const [copied, setCopied] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => api<ApiKey[]>("/api/api-keys"),
  });

  const createMut = useMutation({
    mutationFn: () =>
      api<Created>("/api/api-keys", {
        method: "POST",
        json: { name: name.trim(), rate_limit_per_min: rate },
      }),
    onSuccess: (key) => {
      setCreated(key);
      setName("");
      qc.invalidateQueries({ queryKey: ["api-keys"] });
    },
  });

  const revokeMut = useMutation({
    mutationFn: (id: string) => api(`/api/api-keys/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["api-keys"] }),
  });

  return (
    <div className="container mx-auto px-6 py-10 max-w-4xl">
      <h1 className="font-display text-4xl font-black mb-2">
        API <span className="text-gradient">ключи</span>
      </h1>
      <p className="text-ink-muted">
        Используйте для интеграции с RuDapt из ваших приложений. Эндпоинты:{" "}
        <code className="text-ink">/api/v1/startups</code>,{" "}
        <code className="text-ink">/api/v1/generate-plan</code>,{" "}
        <code className="text-ink">/api/v1/reports/&#123;id&#125;</code>. Передавайте ключ в
        заголовке <code className="text-ink">X-API-Key</code>.
      </p>

      <div className="glass-card p-6 mt-8">
        <h2 className="font-display text-xl font-bold mb-4 flex items-center gap-2">
          <Plus className="h-5 w-5" /> Создать ключ
        </h2>
        <div className="flex flex-col md:flex-row gap-3">
          <Input
            placeholder="Название (например: prod, ci)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            type="number"
            min={1}
            max={1000}
            value={rate}
            onChange={(e) => setRate(Number(e.target.value))}
            className="md:w-40"
            placeholder="rate/min"
          />
          <Button
            onClick={() => createMut.mutate()}
            disabled={!name.trim() || createMut.isPending}
          >
            {createMut.isPending ? "..." : "Создать"}
          </Button>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="font-display text-xl font-bold mb-4 flex items-center gap-2">
          <KeyRound className="h-5 w-5" /> Мои ключи
        </h2>
        {isLoading ? (
          <div className="glass-card h-24 animate-pulse" />
        ) : !data?.length ? (
          <div className="glass-card p-6 text-ink-muted">Пока пусто.</div>
        ) : (
          <div className="space-y-3">
            {data.map((k) => (
              <div
                key={k.id}
                className="glass-card p-4 flex items-center justify-between gap-4"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-display font-bold">{k.name}</span>
                    {k.revoked_at ? (
                      <Badge variant="rose">отозван</Badge>
                    ) : (
                      <Badge variant="cyan">активен</Badge>
                    )}
                    <Badge>{k.rate_limit_per_min}/мин</Badge>
                  </div>
                  <div className="mt-1 text-xs text-ink-dim font-mono">
                    {k.prefix}••••••••
                  </div>
                  <div className="mt-1 text-xs text-ink-dim">
                    {new Date(k.created_at).toLocaleDateString("ru-RU")}
                    {k.last_used_at &&
                      ` · последний раз: ${new Date(k.last_used_at).toLocaleString("ru-RU")}`}
                  </div>
                </div>
                {!k.revoked_at && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm(`Отозвать ключ "${k.name}"?`)) revokeMut.mutate(k.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <Dialog open={!!created} onOpenChange={(o) => !o && setCreated(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-display text-2xl font-bold">
              Скопируйте ключ сейчас
            </DialogTitle>
            <DialogDescription className="text-ink-muted">
              Это единственный раз, когда вы видите ключ целиком. После закрытия модалки —
              только префикс.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 rounded-xl border border-violet-brand/40 bg-violet-brand/10 p-3 font-mono text-xs break-all select-all">
            {created?.plaintext}
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <Button
              variant="ghost"
              onClick={() => {
                if (created) {
                  navigator.clipboard.writeText(created.plaintext);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                }
              }}
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? "Скопировано" : "Копировать"}
            </Button>
            <Button onClick={() => setCreated(null)}>Готово</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
